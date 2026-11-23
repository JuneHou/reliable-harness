import os
import random
from dotenv import load_dotenv, find_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

_ = load_dotenv(find_dotenv())
set_llm_cache(InMemoryCache())

OPENAI_API_KEY_POOL = [
    os.getenv('OPENAI_API_KEY'),
]

def get_random_key(key_pool):
    return random.choice([k for k in key_pool if k is not None])


def run_agent(query, pdf_paths):
    all_texts = []
    embeddings = OpenAIEmbeddings(openai_api_key=get_random_key(OPENAI_API_KEY_POOL))
    
    for pdf_path in pdf_paths:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        for text in texts:
            text.metadata["source"] = pdf_path
        
        all_texts.extend(texts)
    
    db = Chroma.from_documents(all_texts, embeddings)
    
    qa = ConversationalRetrievalChain.from_llm(
        OpenAI(openai_api_key=get_random_key(OPENAI_API_KEY_POOL), cache=True, temperature=0),
        VectorStoreRetriever(vectorstore=db),
        verbose=True,
        return_source_documents=True)

    filter = {'source': 'paper2.pdf'} #it means the information from paper2.pdf should be used to answer the query.
    #if it answers from paper2.pdf, then the filtering is working correctly.

    result = qa({"question": query, "chat_history": [], "filter": filter})
    
    return result


if __name__ == "__main__":
    query = "What is Theia"
    pdf_paths = ["paper1.pdf", "paper2.pdf"]
    result = run_agent(query, pdf_paths)
    
    print(result['answer'])