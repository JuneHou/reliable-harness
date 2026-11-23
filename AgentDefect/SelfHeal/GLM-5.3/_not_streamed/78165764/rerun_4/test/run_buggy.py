from fastapi import FastAPI
from dotenv import load_dotenv
import os
import pandas as pd
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def run_agent(query):

    model = ChatOpenAI(
        temperature=0.1,
        model="gpt-3.5-turbo",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    products = pd.read_csv("./data/products.csv")

    vectorstore = FAISS.from_texts(
        products["text"].astype(str).tolist(),
        embedding=OpenAIEmbeddings()
    )

    retriever = vectorstore.as_retriever()

    app = FastAPI(
        title="LangChain Server",
        version="1.0",
        description="Spin up a simple api server using LangChain's Runnable interfaces",
    )

    ANSWER_TEMPLATE = """Answer the question based on the following context:
    {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(ANSWER_TEMPLATE)

    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | model
        | StrOutputParser()
    )

    result = chain.invoke(query)
    
    return result

if __name__ == "__main__":
    query = "What is the highest budget movie?"
    print(run_agent(query))
