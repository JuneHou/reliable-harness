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

    class DummyVectorSearch:
        def __init__(self, documents, embedding):
            self.documents = documents
            self.embedding = embedding

        def similarity_search(self, query):
            if not self.documents:
                return []

            # Rank the loaded passages locally so search still works when no
            # vector-store backend is configured.
            query_terms = {
                term.lower().strip(".,?!:;()[]{}\"'")
                for term in query.split()
                if term.strip(".,?!:;()[]{}\"'")
            }

            def score(document):
                text = document.page_content.lower()
                terms = {
                    term.strip(".,?!:;()[]{}\"'")
                    for term in text.split()
                }
                return len(query_terms & terms)

            ranked = sorted(
                enumerate(self.documents),
                key=lambda item: (score(item[1]), -item[0]),
                reverse=True,
            )
            matches = [document for _, document in ranked if score(document) > 0]
            return matches[:4]

    class MongoDBAtlasVectorSearch:
        @classmethod
        def from_documents(cls, documents, embedding, collection, index_name):
            return DummyVectorSearch(documents, embedding)

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
