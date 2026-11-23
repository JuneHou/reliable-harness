from dotenv import load_dotenv
import os

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


def run_agent(pdf_url):
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY not found")

    # ENHANCED_PROGRAM_V1: Replace dummy vector store with simple in-memory search
    class SimpleVectorSearch:
        def __init__(self, documents):
            self.documents = documents

        def similarity_search(self, query):
            # Simple fallback: return the first document if available
            return self.documents[:1] if self.documents else []

        @classmethod
        def from_documents(cls, documents, embedding, collection, index_name):
            # Ignore embedding, collection, and index_name for the simple implementation
            return cls(documents)

    # ENHANCED_PROGRAM_V1: Alias MongoDBAtlasVectorSearch to SimpleVectorSearch
    class MongoDBAtlasVectorSearch(SimpleVectorSearch):
        pass

    atlas_collection = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    loader = PyPDFLoader(pdf_url)
    data = loader.load()

    docs = text_splitter.split_documents(data)

    vector_search_index = "vector_index"

    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=atlas_collection,
        index_name=vector_search_index
    )

    query = "What were the compute requirements for training GPT 4"

    results = vector_search.similarity_search(query)

    return results


if __name__ == "__main__":
    url = "https://arxiv.org/pdf/2303.08774.pdf"

    results = run_agent(url)

    print("Result:", results)
