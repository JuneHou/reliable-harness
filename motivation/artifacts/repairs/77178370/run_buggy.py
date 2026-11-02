import os
from dotenv import load_dotenv, find_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables from .env file.
load_dotenv(find_dotenv())


def run_agent(user_input):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key

    custom_template = """
Answer the question using only the supplied context. Include all relevant facts
from the context, and do not use unrelated facts. If the context does not answer
the question, say you don't know.

Chat History:
{chat_history}
Follow Up Input: {question}
"""
    question_prompt = PromptTemplate.from_template(custom_template)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    embeddings = OpenAIEmbeddings()

    docs = [
        "Buildings are made out of brick",
        "Buildings are made out of wood",
        "Buildings are made out of stone",
        "Buildings are made out of atoms",
        "Buildings are made out of building materials",
        "Cars are made out of metal",
        "Cars are made out of plastic",
    ]
    vectorstore = FAISS.from_texts(docs, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": len(docs)},
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        condense_question_prompt=question_prompt,
        memory=memory,
    )

    result = qa({"question": user_input})
    return result["answer"]


if __name__ == "__main__":
    user_input = "What are buildings made of?"
    result = run_agent(user_input)
    print("\n=== User Query Result ===")
    print(f"Question: {user_input}")
    print(f"Answer: {result}")
