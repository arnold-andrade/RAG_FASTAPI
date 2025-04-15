from fastapi import FastAPI, Request
from pydantic import BaseModel
from agentV2 import rag_response
import uvicorn

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask_doc")
def ask_doc(request: QueryRequest):
    query = request.question
    answer = rag_response(query)
    return {"user_question": query, "answer": answer}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)


