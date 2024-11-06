from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
import os
from rag_pipeline import rag_pipeline
import subprocess

app = FastAPI()

# Allow all origins for CORS (useful for development; tighten this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

# Replace these values with your actual Render database credentials
db_user = "peliculas"
db_password = "8VB3hiOxJDVI8PrIMcloMWWq1CBbE8nz"
db_database = "peliculas_h8in"
db_host = "dpg-cslbs1jv2p9s7383l90g-a"  # Hostname from Render
db_port = "5432"

DATABASE_URL = f"postgresql://peliculas:8VB3hiOxJDV1P8rlMcIoMWWq1CBbE8nz@dpg-cslbs1jv2p9s7383l90g-a/peliculas_h81n"
engine = create_engine(DATABASE_URL)

# SQL initialization script for PGVector extension and script_embeddings table
init_script = """
    CREATE EXTENSION IF NOT EXISTS vector;
    
    CREATE TABLE IF NOT EXISTS script_embeddings (
        id SERIAL PRIMARY KEY,
        script_name VARCHAR(255),
        chunk_id INT,
        content TEXT,
        embedding VECTOR(768)  
    );
"""

def initialize_database():
    """Initialize the database with required extensions and tables."""
    with engine.connect() as conn:
        conn.execute(text(init_script))

# Run database initialization on startup
@app.on_event("startup")
async def startup_event():
    initialize_database()

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
        result = subprocess.run(["python", "load_documents.py"], check=True, capture_output=True, text=True)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "output": e.stderr}

@app.get("/")
async def root():
    return {"message": "API is running"}
