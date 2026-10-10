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
    
    sensitive_query = "Waht is the confidential acquistion startegy and target price ?"
    print(f"==> Query : {sensitive_query}")
    
    print("\n[TEST 1] Running query as 'Employee'...")
    employee_results = search_knowledge_base(sensitive_query, user_roles=["Employee"], top_k=2)
    
    leaked = False
    
    for row in employee_results:
        memo_id, title, roles, content, score = row
        print(f"==> Returned: '{title}' | Allowed Roles: {roles} | Score: {score:.3f}")
        if "Employee" not in roles:
            leaked = True
    
    if not leaked:
        print("\t RESULT: Success ! No leak.")
    else:
        print("\t RESULT: Failed ! Documents leaked.")
    
    
    print("\n[TEST 1] Running query as 'Employee'...")
    executive_results = search_knowledge_base(sensitive_query, user_roles=["Executive"], top_k=2)
    
    leaked = False
    
    for row in executive_results:
        memo_id, title, roles, content, score = row
        print(f"==> Returned: '{title}' | Allowed Roles: {roles} | Score: {score:.3f}")
        if "Executive" in roles and "Employee" not in roles:
            restrictions_applied = True
    
    if not leaked:
        print("\t RESULT: Success ! Confidential memo retrieved as expected.")
    else:
        print("\t RESULT: Failed ! No restriction memo found.")