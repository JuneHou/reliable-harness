import os
from dotenv import load_dotenv, find_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain 
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
_ = load_dotenv(find_dotenv())

def run_agent(user_input):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    os.environ['OPENAI_API_KEY'] = openai_api_key
    
    custom_template = """
This is conversation with a human. Answer the questions you get based on the knowledge you have.
If you don't know the answer, just say that you don't, don't try to make up an answer.
Chat History:
{chat_history}
Follow Up Input: {question}
"""
    CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",  # Name of the language model
        temperature=0  # Parameter that controls the randomness of the generated responses
    )
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
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever,
        condense_question_prompt=CUSTOM_QUESTION_PROMPT,
        memory=memory
    )
    query = "what are cars made of?"
    result = qa({"question": query})
    result= retriever.get_relevant_documents(query)
    
    return result
   

if __name__ == "__main__":
    user_input = "What are buildings made of?"
    result = run_agent(user_input)
    print("\n=== User Query Result ===")
    print(f"Question: {user_input}")
    print(f"Answer: {result}")