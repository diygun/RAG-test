import json
import psycopg2
from sentence_transformers import SentenceTransformer

# db connection
conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")

# the db wroker, execute the sql commands
cur = conn.cursor()

cur.execute("SELECT version();")

db_version = cur.fetchone()
print("Connected to the db !")
print("Db version : ", db_version[0])

cur.close()
conn.close()

