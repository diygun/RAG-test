### Synthetic data :
I created some synthetic data using an LLM with OpenRouter

### Setup and test the db and embedding

1. test_connection.py verifies the database engine.

2. setup_table.py verifies PostgreSQL extensions and schemas.

3. test_single_row.py verifies data types and transactions.

4. test_embedding.py verifies the local AI model.

### Full data ingestion

ingest_memos.py uses the local AI model and store the emnedding on postgresql


