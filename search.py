import psycopg2
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def search_knowledge_base(query_text: str, user_roles: list[str], top_k: int = 3):
    query_vector = model.encode(query_text).tolist()
    
    conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")
    
    try:
        with conn:
            with conn.cursor() as cur:
                sql = """
                SELECT 
                    id, 
                    title, 
                    allowed_roles, 
                    content,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM document_chunks
                WHERE allowed_roles && %s
                ORDER BY embedding <=> %s::vector ASC
                LIMIT %s;
                """
                
                cur.execute(sql, (query_vector, user_roles, query_vector, top_k))
                results = cur.fetchall()
                return results
            
    except Exception as e:
        print(f"An error occured {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_query = "What is the policy for laptops and computer equipment ?"
    
    print(f"=== Searching as 'Employee' for: '{test_query}' ===")
    matches = search_knowledge_base(test_query, user_roles=["Employee"], top_k=2)
    
    for row in matches:
        memo_id, title, roles, content, score = row
        print(f"\n[Match found | Similarity : {score:.4f}]")
        print(f"Title : {title}")
        print(f"Allowed roles : {roles}")
        print(f"Content : \n{content}\n")