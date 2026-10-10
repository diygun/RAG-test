import os
import json
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import requests

load_dotenv()
API_KEY = os.getenv("TOKEN")

model = SentenceTransformer("all-MiniLM-L6-v2")

# test_vector = model.encode("Hello world").tolist()

# print("Length of the vector is : ", len(test_vector))

def retrieve_context(query_text: str, user_roles: list[str], tok_k: int = 3):
    query_vector = model.encode(query_text).tolist()
    conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")
    
    try:
        with conn:
            with conn.cursor() as cur:
                sql = """
                SELECT title, content
                FROM document_chunks
                WHERE allowed_roles && %s
                ORDER BY embedding <=> %s::vector ASC
                LIMIT %s
                """
                
                cur.execute(sql, (user_roles, query_vector, tok_k))
                return cur.fetchall()
    finally:
        conn.close()

def generate_answer(query_text: str, retrieved_docs: list[tuple]):
    if not retrieved_docs:
        return "I do not have access to any documents that answer this question."
    
    context_str = ""
    for title, content in retrieved_docs:
        context_str += (f"\n --- Source: {title} ---\n {content}\n")
        
    system_prompt = """ You are an entreprise AI assistant. Answer the user question strictly using the provided context below.Always cite the document title in your answer. If the information is not present in the context say you don't know."""
    
    user_prompt = (f"Context:\n {context_str}\n Question: {query_text}")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            data = json.dumps({
                "model": "inclusionai/ling-3.0-flash:floor",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            })
    )
    
    data = response.json()
    return data["choices"][0]["message"]["content"]

def ask_assitant(query: str, user_roles: list[str]):
    print(f"\n User Role(s): {user_roles}")
    print(f"Question: '{query}'")
    
    docs = retrieve_context(query, user_roles)
    print(f"Retrieved {len(docs)} authorized document(s): {[doc[0] for doc in docs]}")
    
    answer = generate_answer(query, docs)
    print("\n\tAssitant Answer:")
    print(answer)
    print("\n\t========================")
    
if __name__ == "__main__":
    test_question = "Waht is the role policy regardeing employee laptop hardware and accessories ?"
    
    ask_assitant(test_question, user_roles=["Employee"])

'''
 ~/De/RAG  main !2 ?2  uv run python rag_pipeline.py           1 ✘  7s  RAG   3.14    04:45:37 
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights: 100%|██████████████████████████████████████████████| 103/103 [00:00<00:00, 8454.11it/s]

 User Role(s): ['Employee']
Question: 'Waht is the role policy regardeing employee laptop hardware and accessories ?'
Retrieved 3 authorized document(s): ['Equipment Allocation Policy', 'IT Usage Guidelines', 'Remote Work Policy']

        Assitant Answer:
According to the **Equipment Allocation Policy**, the role policy regarding employee laptop hardware andaccessories is as follows:

- **Laptop Provision:** All employees are entitled to a company-issued laptop with a minimum specification of **16GB RAM** and a **512GB SSD**, valued at **$1,800 per unit**.
- **Additional Peripherals:** Managers may authorize up to **two additional peripherals** per team member, capped at **$500 total**.
- **Equipment Return:** Equipment must be returned within **14 days of separation**, or a replacement fee of **$1,200** will be deducted from the final paycheck.

        ========================

'''
