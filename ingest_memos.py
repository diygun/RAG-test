import json
import psycopg2
from sentence_transformers import SentenceTransformer

try:
    print("Loading emdedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Reading memos.json")
    with open("memos.json", "r", encoding="utf-8") as f:
        memos = json.load(f)

    conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")

    insert_sql = """
    INSERT INTO document_chunks
    (id, title, department, allowed_roles, content, test_query, expected_answer, embedding)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    with conn:
        with conn.cursor() as cur:
            print(f"Ingesting {len(memos)} records into PostgreSQL.")
            for memo in memos:
                vector = model.encode(memo["content"]).tolist()
                
                cur.execute(insert_sql,(
                    memo["id"],
                    memo["title"],
                    memo["department"],
                    memo["allowed_roles"],
                    memo["content"],
                    memo["test_query"],
                    memo["expected_answer"],
                    vector
                ))
                
            cur.execute("SELECT COUNT(*) FROM document_chunks;")
            total_records = cur.fetchone()[0]
            print(f"Done! Total records now in database : {total_records}")

except Exception as e:
    print(f"An error occured during ingestion: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()
        print("Db connection closed.")
