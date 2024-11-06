import requests
from sqlalchemy import create_engine, text  
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from db_config import db_user, db_password, db_database, db_host, db_port
from time import time, sleep

embed_url = "http://tormenta.ing.puc.cl/api/embed"

def get_embeddings(text_content):
    payload = {
        "model": "nomic-embed-text",
        "input": text_content
    }
    response = requests.post(embed_url, json=payload)
    response.raise_for_status()  
    embeddings = response.json()["embeddings"][0] 
    return embeddings

# Replace these values with your actual Render database credentials
db_user = "peliculas"
db_password = "8VB3hiOxJDV1P8rlMcIoMWWq1CBbE8nz"
db_database = "peliculas_h8in"
db_host = "dpg-cslbs1jv2p9s7383l90g-a"  # Hostname from Render
db_port = "5432"

connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"

engine = create_engine(connection_string)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=50,
    length_function=len,  
)

requests_per_second = 10
request_count = 0
start_time = time()

input_folder = "cleaned_scripts"
with engine.connect() as conn:
    with conn.begin():  
        for i, filename in enumerate(os.listdir(input_folder)):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as file:
                text_content = file.read()
                chunks = splitter.split_text(text_content)
                for j, chunk in enumerate(chunks):
                    if request_count >= requests_per_second:
                        elapsed = time() - start_time
                        if elapsed < 1:
                            sleep(1 - elapsed)
                        start_time = time()
                        request_count = 0

                    embedding = get_embeddings(chunk)
                    insert_data = {
                        "script_name": filename,
                        "chunk_id": j,
                        "content": chunk,
                        "embedding": embedding
                    }

                    conn.execute(
                        text("""
                        INSERT INTO script_embeddings (script_name, chunk_id, content, embedding)
                        VALUES (:script_name, :chunk_id, :content, :embedding)
                        """),
                        insert_data
                    )
                    print(f"Inserted chunk {j} from {filename}")
                    request_count += 1

print("Documents successfully loaded into the vector database.")
