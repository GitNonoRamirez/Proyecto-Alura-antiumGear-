from fastapi import FastAPI
from pydantic import BaseModel
from app.agent import get_agent   # 👈 Import corregido

app = FastAPI()
agent = get_agent()

class Question(BaseModel):
    query: str

@app.post("/ask")
def ask_question(question: Question):
    result = agent(question.query)
    return {"answer": result.content}
