import os
from dotenv import load_dotenv
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import NLTKTextSplitter
from langchain.vectorstores import Chroma
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.schema import Document
import nltk

def run_agent(query,store_location="./store_location"):

    nltk.download("punkt")

    hf_embed_path = "./hf_cache"

    docs = [
        Document(page_content="Artificial Intelligence (AI) is technology that enables computers and machines to simulate human intelligence."),
        Document(page_content="Machine learning (ML) is a type of Artificial Intelligence (AI) that teaches computers to find patterns in large datasets and make decisions or predictions without being explicitly programmed for every scenario, learning and improving from experience, much like humans do."),
        Document(page_content="RAG most commonly refers to Retrieval-Augmented Generation, an AI technique that improves large language models (LLMs) by letting them access and use external, up-to-date information (like documents or databases) to generate more accurate, context-aware, and factual answers, preventing hallucinations and tailoring responses to specific knowledge bases without needing costly retraining.")
    ]

    embedding_function = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        cache_folder=hf_embed_path
    )

    child_splitter = NLTKTextSplitter(chunk_size=400)

    vectorstore = Chroma(
        collection_name="full_documents",
        embedding_function=embedding_function,
        persist_directory="./chroma_db_child"
    )

    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter
    )

    retriever.add_documents(docs)

    vector_db = Chroma(
        collection_name="full_documents",
        embedding_function=embedding_function,
        persist_directory="./chroma_db_child"
    )

    matching_doc = vector_db.max_marginal_relevance_search(query, k=3)
    return matching_doc

if __name__ == "__main__":
    query = "What is RAG?"
    result = run_agent(query)
    print(result)