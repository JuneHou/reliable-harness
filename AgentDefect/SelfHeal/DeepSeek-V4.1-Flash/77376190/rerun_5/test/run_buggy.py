import os
from dotenv import load_dotenv, find_dotenv
import openai
import gradio as gr
from llama_index.core import SimpleDirectoryReader, GPTListIndex, GPTVectorStoreIndex, PromptHelper, load_index_from_storage, Settings
from llama_index.llms.openai import OpenAI

_ = load_dotenv(find_dotenv())


os.environ['REQUESTS_CA_BUNDLE'] = ''  

def run_agent(user_input, docs_path='docs'):
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    os.environ["OPENAI_API_KEY"] = openai_api_key
    openai.api_key = openai_api_key
    
    def createVecorIndex(path):
        max_input = 4096
        tokens = 512
        chunk_size = 600
        max_chunk_overlap = 0.1
        
        
        Settings.llm = OpenAI(temperature=0.3, model='gpt-3.5-turbo', max_tokens=tokens)
        Settings.chunk_size = chunk_size
        Settings.chunk_overlap = int(chunk_size * max_chunk_overlap)
        
        #load data
        docs = SimpleDirectoryReader(path).load_data()
        #create vector index
        vectorIndex = GPTVectorStoreIndex.from_documents(docs)
        vectorIndex.storage_context.persist(persist_dir='vectorIndex.json')
        return vectorIndex
    
    vectorIndex = createVecorIndex('docs')
    
    def chatbot(input_index):
        query_engine = vectorIndex.as_query_engine()
        response = query_engine.query(input_index)
        return response.response
   
    result = chatbot(user_input)
    
    return result

if __name__ == "__main__":
  
    user_input = "What is the main topic of the documents?"
    result = run_agent(user_input)
    print("\n=== User Query Result ===")
    print(f"Question: {user_input}")
    print(f"Answer: {result}")
    
    