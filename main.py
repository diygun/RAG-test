from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from rag_pipeline import retrieve_context, generate_answer

app = FastAPI(title="Entreprise RBAC RAG API")

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(
    payload: QueryRequest,
    x_user_role: str = Header(default="Employee", description="Simulated user role : Employee, Manager, Executive")
):
    allowed_system_roles = ["Employee", "Manager", "Executive"]
    if x_user_role not in allowed_system_roles:
        raise HTTPException(status_code=403, detail=f"Invalide role. Must be one of {allowed_system_roles}")
    
    docs = retrieve_context(payload.question, user_roles=[x_user_role])
    
    answer = generate_answer(payload.question, docs)
    
    return QueryResponse(
        answer= answer,
        sources= [doc[0] for doc in docs]
    )
    