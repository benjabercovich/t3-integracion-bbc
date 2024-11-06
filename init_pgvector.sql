-- init_pgvector.sql

-- Enable the PGVector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the table with an embedding vector column
CREATE TABLE IF NOT EXISTS script_embeddings (
    id SERIAL PRIMARY KEY,
    script_name VARCHAR(255),
    chunk_id INT,
    content TEXT,
    embedding VECTOR(768)  
);
