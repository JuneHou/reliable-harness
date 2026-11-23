import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()


config = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
}

class configs:
    EMBEDDINGS_MODEL = "text-embedding-3-small"


class MockPDFFile:
    def __init__(self, filepath, filename):
        self.filepath = filepath
        self.filename = filename


def read_docs(pdf_file):
    pdf_loader = PyPDFLoader(pdf_file.filepath)
    pdf_documents = pdf_loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(pdf_documents)
    
    return documents


def generate_and_store_embeddings(documents, pdf_file, user_id):
    client = chromadb.PersistentClient(path="./trained_db")
    collection = client.get_or_create_collection("PDF_Embeddings", embedding_function=embedding_functions.OpenAIEmbeddingFunction(api_key=config["OPENAI_API_KEY"], model_name=configs.EMBEDDINGS_MODEL))
    now = datetime.now()

    
    metadata = {"source": pdf_file.filename, "user": str(user_id), 'created_at': 
                          now.strftime("%d/%m/%Y %H:%M:%S")}
    ids = [str(uuid.uuid4()) for _ in range(len(documents))]

    try:
        vectordb = Chroma.from_documents(
                    documents,         
                    embedding=OpenAIEmbeddings(openai_api_key=config["OPENAI_API_KEY"], 
                    model=configs.EMBEDDINGS_MODEL),
                    persist_directory='./trained_db',
                    collection_name = collection.name, 
                    client = client,
                    ids = ids,
                    collection_metadata = {item: value for (item, value) in metadata.items()}
                )
        vectordb.persist()
        
    except Exception as err:
        print(f"An error occured: {err=}, {type(err)=}")
        return {"answer": "An error occured while generating embeddings. Please check terminal for more details."}
    return vectordb




def run_agent(pdf_path, user_id):
   
    pdf_file = MockPDFFile(pdf_path, os.path.basename(pdf_path))
    
   
    documents = read_docs(pdf_file) 
    print(f"    ✓ Loaded {len(documents)} document chunks")
    
   
    vectordb = generate_and_store_embeddings(documents, pdf_file, user_id)
    
    if isinstance(vectordb, dict):
       
        return None, pdf_file.filename
    
    
    return vectordb, pdf_file.filename


if __name__ == "__main__":

    pdf_path = None
    user_id = "test_user_123"
    
   
    if os.path.exists("docs"):
        for file in os.listdir("docs"):
            if file.endswith(".pdf"):
                pdf_path = os.path.join("docs", file)
                break
    
    if not pdf_path:
        print("No PDF file found in docs folder")
        exit(1)
    
    
    vectordb, filename = run_agent(pdf_path, user_id)
    
    if vectordb is None:
        print("Agent failed to create embeddings")
        exit(1)
    
    
    result = vectordb.get(where={"source": filename})
    print(len(result))
    print(len(result['ids']))
   
   