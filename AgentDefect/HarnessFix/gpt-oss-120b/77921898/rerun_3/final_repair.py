import os
from dotenv import load_dotenv, find_dotenv
from glob import glob
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader


_ = load_dotenv(find_dotenv())

def run_agent(user_input, document_paths=None, persist_directory="chroma_db"):
   
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    os.environ['OPENAI_API_KEY'] = openai_api_key
    
    
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

    # ENHANCED_PROGRAM_V1: Prevent overwriting a populated Chroma vectorstore.
    # When document_paths are provided we build a vectorstore from those documents.
    # The original code mistakenly overwrote this populated store with a fresh empty
    # instance, causing retrieval to return no documents. We now only create the
    # empty store when no documents are supplied.
    if document_paths:
        # Build a vectorstore from the provided documents.
        all_texts = []
        for doc_path in document_paths:
            loader = TextLoader(doc_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            all_texts.extend(texts)
        docsearch = Chroma.from_documents(
            all_texts, embeddings, persist_directory=persist_directory
        )
    else:
        # No documents supplied – create an empty persistent store.
        docsearch = Chroma(persist_directory, embedding_function=embeddings)
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
