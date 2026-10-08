import psycopg2

conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

cur.execute("DROP TABLE IF EXISTS document_chunks;")

cur.execute("""
CREATE TABLE document_chunks (
    id INT PRIMARY KEY,
    title TEXT NOT NULL,
    department TEXT NOT NULL,
    allowed_roles TEXT[] NOT NULL,
    content TEXT NOT NULL,
    test_query TEXT NOT NULL,
    expected_answer TEXT NOT NULL,
    embedding vector(384)
);
""")

conn.commit()

print("Table 'document_chunks cretaed with vector(348) support !'")

cur.close()
conn.close()