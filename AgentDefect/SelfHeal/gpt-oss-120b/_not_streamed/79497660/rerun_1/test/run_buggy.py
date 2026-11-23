from llama_index.core import VectorStoreIndex, Document
from llama_index.vector_stores.postgres import PGVectorStore
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_vector_store(request):
    host = "localhost"
    password = "password"
    port = 5432
    user = "postgres"
    
    vector_store = PGVectorStore.from_params(
        database=request.tenant,
        host=host,
        password=password,
        port=port,
        user=user,
        table_name="vectorstore",
        embed_dim=1536,
        hnsw_kwargs={
            "hnsw_m": 16,
            "hnsw_ef_construction": 64,
            "hnsw_ef_search": 40,
            "hnsw_dist_method": "vector_cosine_ops",
        },
    )
    
    return vector_store

def run_agent(request):
    vector_store = create_vector_store(request)
    
    documents = [
        Document(text="Sample document 1", metadata={"external_id": "ext_001"}),
        Document(text="Sample document 2", metadata={"external_id": "ext_002"}),
    ]
    
    index = VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store
    )
    
    return index

if __name__ == "__main__":
    class Request:
        tenant = "test_db"
    
    request = Request()
    index = run_agent(request)
    print("Vector store created and documents indexed")
    print("Issue: external_id is stored in metadata JSON column")
    print("Need: external_id as a separate column in the table")