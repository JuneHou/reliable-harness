import os
from dotenv import load_dotenv, find_dotenv
from glob import glob
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader

_ = load_dotenv(find_dotenv())

# ENHANCED_PROGRAM_V1: robust Chroma initialization with retries
def _init_chroma(persist_dir, embeddings, max_retries=3):
    """Initialize a Chroma vectorstore with exponential back‑off retries."""
    import time
    for attempt in range(1, max_retries + 1):
        try:
            return Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        except Exception:
            if attempt == max_retries:
                raise
            time.sleep(2 ** (attempt - 1))

def run_agent(user_input, document_paths=None, persist_directory="chroma_db"):
    """Retrieve relevant documents for *user_input*.

    This function builds a vectorstore from *document_paths* when provided,
    otherwise it loads an existing persisted store. It never aborts
    prematurely; if retrieval fails an exception is raised so the caller
    can handle it.
    """
    # Ensure the OpenAI key is available for the embeddings model
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment")
    os.environ['OPENAI_API_KEY'] = openai_api_key

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # Build or load the vectorstore
    if document_paths:
        all_texts = []
        for doc_path in document_paths:
            loader = TextLoader(doc_path)
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = splitter.split_documents(documents)
            all_texts.extend(texts)
        docsearch = Chroma.from_documents(all_texts, embeddings, persist_directory=persist_directory)
    else:
        # Load existing persisted store with retry logic
        docsearch = _init_chroma(persist_directory, embeddings)

    # Retrieve relevant documents
    retriever = docsearch.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(user_input)
    print(f"Number of documents retrieved: {len(docs)}")
    return docs

if __name__ == "__main__":
    # Example usage
    document_paths = glob("docs/*.txt")
    query = "What is machine learning?"
    docs = run_agent(query, document_paths)
    print("\n=== User Query Result ===")
    print(f"Query: {query}")
    print(f"Number of relevant documents: {len(docs)}")
    for i, doc in enumerate(docs):
        print(f"\n--- Document {i+1} ---")
        print(doc.page_content)
