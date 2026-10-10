# Enterprise Role Based Access Control Retrieval-Augmented Generation Knowledge Assistant

This repo is a small demo of my RBAC RAG system. It is just a showcase of what we can do pretty quickly nowadays.

## How to do your own RBAC RAG ?
### Architecture & Scope Definition:
What would you expect from a knowledge assistant ? How should you manage access to data ?
I used a small three privilege tiers setup to demonstrate how access can be limited.

### Synthetic data:
I generates 20 synthetic data using an LLM with OpenRouter `inclusionai/ling-3.0-flash:floor`. The data was structured as memos categorized across the three privilege tiers I previously choosed : Employee, Manager, Executive.

### Database:
I set up a docker container running PostgreSQL with the pgvector extention. You can find it in the `docker-compose.yml`.

### Setup and test the db and embedding:
1. `test_connection.py` verifies the database engine.

2. `setup_table.py` verifies PostgreSQL extensions and schemas.

3. `test_single_row.py` verifies data types and transactions.

4. `test_embedding.py` verifies the local AI model.

### Full data ingestion:
`ingest_memos.py` reads `memos.json` and generate 384 dimensional vector locally using the `sentence-transformers/all-MiniLM-L6-v2` model, a model specifically trained for Semantic Search, then inserts all 20 records into PostgreSQL with their corresponding `allowed_roles` (Employee, Manager or Executive).

### Search with Role-Based Filtering
`search.py` does the retrieval and combines two PostgreSQL operations in one SQL query. Role-Based and distance filtering which filter out unauthorized documents before vector matching and rank the remaining documents by semantic similarity. (The more words have similar meaning, the closer they are on the 384-dimensional vector).

### Security Check:
`test_security.py` runs a query as an Employee and Executive to test if we can retrieve a confidential memo. It asserts that confidential records are completely inaccessible to unauthorized roles (Employee).

### RAG Pipeline:
`rag_pipeline.py` connects retrieval to the LLM via OpenRouter and injects only the retrieved context into the prompt. And enforces source citations while instructing the model to not answer if the information is missing from the retrieved context.

### The REST API:
`main.py` wraps the pipeline in a FastAPI application and exposes a /chat endpoint that reads the user's role from the `X-User-Role` header, executes the RBAC search, and returns the grounded answer with document citations.

---

## Quickstart Guide

### Prerequisites:
- Docker
- uv
- git

### Environment Setup

Clone the repo :

```
git clone https://github.com/diygun/RAG-test.git
cd RAG-test
uv sync
```

Create a .env with your OpenRouter token :
```
TOKEN=sk---
```

### Start the Vector Database

Launch the PostgreSQL container with pgvector with Docker compose :
```
docker compose up -d
```

You can check with :
```
docker ps
```
> You should see rag_pgvector running on port 5432

### Initialize the Schema & Ingest Documents
Run the database setup script, then populate the vector database with the 20 role-tagged corporate memos:

Create the extension and document table
```
uv run python setup_table.py
```

Convert memos into 384-d vectors and save to PostgreSQL
```
uv run python ingest_memos.py
```
> Expected output: Done! Total records now in database : 20

### Optional : Run the Security Verification Test

```
uv run python test_security.py
```
> Expected output: Confirms that an Employee query returns 0 confidential documents, while an Executive query successfully retrieves restricted files.

### Start the FastAPI Application
Launch the local REST API server:
```
uv run uvicorn main:app --port 8000
```
You can enable hot reload with `--reload`

The API is now running at http://localhost:8000. You can open your browser to http://localhost:8000/docs to test all endpoints via the interactive Swagger UI.

### Test the Endpoint via cURL

#### Standard Employee Query (Authorized)
```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "X-User-Role: Employee" \
     -d '{"question": "What is the policy regarding employee laptop hardware and accessories?"}'
```

#### Executive Inquiry Under Employee Role (Blocked)
```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "X-User-Role: Employee" \
     -d '{"question": "What is the confidential acquisition strategy and target price?"}'
```
> Result: The database returns no chunks, and the model states it has no access to answer.


#### Executive Inquiry Under Executive Role (Authorized)
```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "X-User-Role: Executive" \
     -d '{"question": "What is the confidential acquisition strategy and target price?"}'
```
> Result: Returns the restricted figures and cites the confidential source memo.
