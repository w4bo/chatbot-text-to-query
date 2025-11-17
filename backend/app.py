from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],         # or restrict to frontend: ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
