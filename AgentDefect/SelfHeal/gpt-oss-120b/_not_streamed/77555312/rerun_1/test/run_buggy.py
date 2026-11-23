import os
from langchain.llms import OpenAI
import bs4
import langchain
from langchain import hub
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
import dotenv
dotenv.load_dotenv()

def run_agent(query):
    loader = UnstructuredFileLoader(
        'paper2.pdf'
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    retrieved_docs = retriever.get_relevant_documents(
        query
    )

    return retrieved_docs

if __name__ == "__main__":
    query = "What is Toggle?"
    result = run_agent(query)
    print(result)