from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import httpx
import os
from sqlalchemy import text
import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

def run_sql_query(db: Session, sql: str):
    """
    Safely execute a SQL query and return results formatted as a Markdown table.
    Uses pandas for clean formatting. Only allows SELECT statements.
    """
    if not sql.strip().lower().startswith("select"): raise ValueError("Only SELECT queries are allowed for safety")
    # Execute query
    result = db.execute(text(sql)).fetchall()
    if not result: return "No results found."
    # Convert to DataFrame
    df = pd.DataFrame(result, columns=result[0]._mapping.keys())
    # Convert to Markdown
    return df.to_markdown(index=False)


Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

class Query(BaseModel):
    message: str
    model: str = "llama3"

FUNCTION_SPEC = """
You have access to the following tool:

FUNCTION: run_sql_query
DESCRIPTION: Execute a SQL query on the database and return the result.
PARAMETERS:
- sql (string): The SQL query to execute.

If the user asks something that requires database access:
- Reply ONLY in JSON format: {"function": "run_sql_query", "sql": "<SQL_QUERY>"}
- Do NOT write natural text.
- The SQL must return concise results.
- If a query was already issued, you can reuse that result.

If not needed, reply normally, without highliting the previous functions and adding that this answer does not necessitate database access.
"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chat")
async def chat(req: Query, db: Session = Depends(get_db)):
    # Inject the function specification into the prompt
    modified_prompt = FUNCTION_SPEC + "\n\n" + req.message
    payload = {"model": req.model, "prompt": modified_prompt, "stream": False}
    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
        response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
        response.raise_for_status()
    bot_response = response.json().get("response", "").strip()
    # Check if the response is requesting to invoke the SQL function
    if bot_response.startswith("{") and '"function": "run_sql_query"' in bot_response:
        try:
            func_call = eval(bot_response)
            sql = func_call.get("sql")
            # Execute SQL
            result = run_sql_query(db, sql)
            payload = {"model": req.model, "prompt": "This is the result of the previous query, in case following prompts need it without running the query again.\n\n" + str(result), "stream": False}
            async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
                response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)
                response.raise_for_status()
            bot_response = response.json().get("response", "").strip()
            return {"response": "\n" + str(result)}
        except Exception as e:
            print(e)
            return {"error": str(e)}
    return {"response": bot_response}
