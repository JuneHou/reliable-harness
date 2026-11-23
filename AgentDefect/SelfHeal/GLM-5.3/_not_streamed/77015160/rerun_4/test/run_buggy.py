from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment or .env file")



def run_agent() :
    llm = ChatOpenAI(openai_api_key=api_key, temperature=0)

    docs = ["This is a test document about France.", "Another document about Germany."]
    metadatas = [{"source": "doc1"}, {"source": "doc2"}]

    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    db = FAISS.from_texts(docs, embeddings, metadatas=metadatas)

    chain = RetrievalQAWithSourcesChain.from_chain_type(
        llm,
        chain_type="stuff",
        retriever=db.as_retriever()
    )

    return chain

if __name__ == "__main__":
    print(run_agent())
    

