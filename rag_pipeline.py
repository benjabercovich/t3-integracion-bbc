import requests
import json
from sqlalchemy import create_engine, text
from langchain_postgres import PGVector
from db_config import db_user, db_password, db_database, db_host, db_port

VECTOR_DB_NAME = "script_embeddings"
embed_url = "http://tormenta.ing.puc.cl/api/embed"
llm_url = "http://tormenta.ing.puc.cl/api/chat"  

# Replace these values with your actual Render database credentials
db_user = "peliculas"
db_password = "8VB3hiOxJDVI8PrIMcloMWWq1CBbE8nz"
db_database = "peliculas_h8in"
db_host = "dpg-cslbs1jv2p9s7383l90g-a"  # Hostname from Render
db_port = "5432"

connection_string = f"postgresql://peliculas:8VB3hiOxJDV1P8rlMcIoMWWq1CBbE8nz@dpg-cslbs1jv2p9s7383l90g-a/peliculas_h81n"
# connection_string = f"postgresql+psycopg2://{db_user}:{db_password}@pgvector_db:{db_port}/{db_database}"
engine = create_engine(connection_string)

vectorstore = PGVector(
    embeddings=None,
    collection_name=VECTOR_DB_NAME,
    connection=connection_string,
    use_jsonb=True,
)

def retrieve_context(query, top_k=5):
    with engine.connect() as conn:
        response = requests.post(embed_url, json={"model": "nomic-embed-text", "input": query})
        response.raise_for_status()
        query_embedding = response.json()["embeddings"][0]

        results = conn.execute(
            text("""
            SELECT script_name, chunk_id, content, embedding
            FROM script_embeddings
            ORDER BY embedding <-> (:query_embedding)::vector
            LIMIT :top_k;
            """),
            {"query_embedding": query_embedding, "top_k": top_k}
        ).fetchall()  

        context_fragments = [row[2] for row in results]  
        return "\n".join(context_fragments)


def generate_answer(query, context):
    messages = [
        {"role": "system", "content": f"You are a movie expert assistant. Use the following context to answer questions:\n\n{context}"},
        {"role": "user", "content": query}
    ]
    
    payload = {
        "model": "integra-LLM",
        "messages": messages,
        "temperature": 6,
        "num_ctx": 2048,
        "repeat_last_n": 10,
        "top_k": 18
    }

    try:
        # Stream the response
        response = requests.post(llm_url, json=payload, timeout=120, stream=True)
        response.raise_for_status()
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                # Parse each line as JSON
                message_data = json.loads(line.decode("utf-8"))
                
                # Check if 'content' exists in 'message'
                if 'message' in message_data and 'content' in message_data['message']:
                    full_content += message_data['message']['content']
                
                # If done is True, the response is complete
                if message_data.get("done", False):
                    break

        return full_content.strip() if full_content else "No response received from the model."

    except ValueError as e:
        print(f"JSON decoding error: {e}")
        print("Response content that caused the error:", response.text)
        return "An unexpected response format was received from the LLM API."

    except requests.exceptions.RequestException as e:
        print(f"Error with the LLM API: {e}")
        return "An error occurred while processing your request. Please try again later."


# Main RAG function to handle the full process
def rag_pipeline(query):
    try:
        # Step 1: Retrieve context
        context = retrieve_context(query)

        # Step 2: Generate response using the LLM
        answer = generate_answer(query, context)
        
        return answer

    except requests.exceptions.RequestException as e:
        print(f"Error with the LLM API: {e}")
        return "An error occurred while processing your request. Please try again later."

    except Exception as e:
        print(f"Unexpected error: {e}")
        return "An error occurred. Please contact support."

# Testing the RAG pipeline with a sample query
# if __name__ == "__main__":
#     query = "What is the plot of Star Trek?"
#     answer = rag_pipeline(query)
#     print("Answer:", answer)
