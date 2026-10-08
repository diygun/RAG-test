from sentence_transformers import SentenceTransformer

try:
    print("Loading local model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    sample_text = "Employees recieve a laptop upon onboarding."
    
    embedding = model.encode(sample_text)
    embedding_list = embedding.tolist()
    
    print("Embedding generated successfully !")
    print("\tType: ", type(embedding_list))
    print("\tDimensions: ", len(embedding_list))
    print("\tFirst 5 values: ", embedding_list[:5])
except Exception as e:
    print(f"An error occured while generating the embedding: {e}")
    