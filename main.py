from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rag_pipeline import rag_pipeline
import subprocess

app = FastAPI()

origins = [
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def handle_query(request: QueryRequest):
    query_text = request.query

    answer = rag_pipeline(query_text)

    if "An error occurred" in answer:
        raise HTTPException(status_code=500, detail=answer)

    return {"response": answer}

@app.post("/trigger-load-files")
def trigger_load_files():
    try:
        # Run the script as a subprocess
        result = subprocess.run(["python", "load_files.py"], check=True, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.stderr}

@app.get("/")
async def root():
    return {"message": "API is running"}
