from dotenv import load_dotenv
import os

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS  # ENHANCED_PROGRAM_V1: import FAISS

def build_vector_store(docs, embedding):
    """Fallback vector store using FAISS."""
    return FAISS.from_documents(docs, embedding)

def run_agent(pdf_url):
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY not found")

    # Placeholder for compatibility; not used when FAISS fallback is active
    atlas_collection = []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    loader = PyPDFLoader(pdf_url)
    data = loader.load()
    docs = text_splitter.split_documents(data)

    vector_store = build_vector_store(docs, OpenAIEmbeddings(disallowed_special=()))
    query = "What were the compute requirements for training GPT 4"
    results = vector_store.similarity_search(query)  # ENHANCED_PROGRAM_V1: perform similarity search
    return results

if __name__ == "__main__":
    url = "https://arxiv.org/pdf/2303.08774.pdf"
    results = run_agent(url)
    print(f"Result count: {len(results)}")  # ENHANCED_PROGRAM_V1: show count
