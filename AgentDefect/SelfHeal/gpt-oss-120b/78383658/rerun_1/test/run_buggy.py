import os
from dotenv import load_dotenv

from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

load_dotenv()

def run_agent(query):
    loader = CSVLoader(file_path="control.csv")
    data = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(data)
    vectorstore = Chroma.from_documents(documents=chunks, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()
    template = """You are an assistant for question-answering tasks.

    Use the following pieces of retrieved context to answer the question.

    If you don't know the answer, just say that you don't know.

    Use three sentences maximum and keep the answer concise.

    Question: {question}

    Context: {context}

    Answer:

    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo",verbose=True)

    rag_chain = (  {"context": retriever,  "question": RunnablePassthrough()}      | prompt      | llm     | StrOutputParser()  )

    output = rag_chain.invoke(query)
    return output

if __name__ == "__main__":
    query = "Find movies for family, combining their Name and Description."
    result = run_agent(query)
    print(result)