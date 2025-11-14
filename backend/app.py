from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os

app = FastAPI()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

class Query(BaseModel):
    message: str
    model: str = "llama3"

@app.post("/chat")
async def chat(req: Query):
    payload = {
        "model": req.model,
        "prompt": req.message,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)

    return {"response": response.json().get("response", "")}
