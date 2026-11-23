import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from glob import glob
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

def _get_or_create_docsearch(all_texts, embeddings, persist_directory):
    """
    Return a Chroma vector store:
    * If a persisted store exists, load it.
    * Otherwise create it from `all_texts` and persist for future runs.
    """
    persist_path = Path(persist_directory)
    if persist_path.exists() and any(persist_path.iterdir()):
        # Existing persisted index – load it.
        return Chroma(persist_directory=str(persist_path), embedding_function=embeddings)
    else:
        # No index yet – build from supplied documents.
        return Chroma.from_documents(
            all_texts,
            embeddings,
            persist_directory=str(persist_path),
        )



_ = load_dotenv(find_dotenv())

def run_agent(user_input, document_paths=None, persist_directory="chroma_db"):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    os.environ['OPENAI_API_KEY'] = openai_api_key

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    if document_paths:
        all_texts = []
        for doc_path in document_paths:
            loader = TextLoader(doc_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            all_texts.extend(texts)

        docsearch = _get_or_create_docsearch(all_texts, embeddings, persist_directory)
    else:
        # No documents supplied – try to load any existing persisted store.
        docsearch = _get_or_create_docsearch([], embeddings, persist_directory)

    retriever = docsearch.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(user_input)
    print(f"Number of documents retrieved: {len(docs)}")
    return docs
if __name__ == "__main__":

    document_paths = glob("docs/*.txt")
    query = "What is machine learning?"
    docs = run_agent(query, document_paths)
    
    print("\n=== User Query Result ===")
    print(f"Query: {query}")
    print(f"Number of relevant documents: {len(docs)}")
    
    for i, doc in enumerate(docs):
        print(f"\n--- Document {i+1} ---")
        print(doc.page_content)  
