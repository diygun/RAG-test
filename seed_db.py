import json
import psycopg2
from sentence_transformers import SentenceTransformer

# db connection
conn = psycopg2.connect("postgresql://rag_user:rag_password@localhost:5432/rag_db")