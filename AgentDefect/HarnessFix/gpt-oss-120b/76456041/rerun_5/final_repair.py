import os
import warnings
from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import CSVLoader
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI  # ENHANCED_PROGRAM_V1: use ChatOpenAI for ChatCompletion compatibility
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

warnings.filterwarnings('ignore')

load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def run_agent(queries):
    results = []    
   
    files = ['drivers.csv','drivers_full.csv']

    for file in files:
        print("=====================================")
        print(file)
        print("=====================================")
        with get_openai_callback() as cb:

            loader = CSVLoader(file_path=file,encoding='utf-8')
            docs = loader.load()

            from langchain.embeddings.openai import OpenAIEmbeddings

            embeddings = OpenAIEmbeddings()

            # create the vectorestore to use as the index
            db = Chroma.from_documents(docs, embeddings)
            # expose this index in a retriever interface
            retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":1000})

            for query in queries:
                qa_stuff = RetrievalQA.from_chain_type(
                    llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"), # ENHANCED_PROGRAM_V1: switched to ChatOpenAI,
                    chain_type="map_reduce", 
                    retriever=retriever,
                    verbose=True
                )

                print(query)
                try:
                    result = qa_stuff.run(query)  # ENHANCED_PROGRAM_V1: safe LLM call
                except Exception as e:
                    print(f"LLM invocation failed: {e}")
                    result = "MODEL_ERROR"
                results.append(result)

                print(result)
                
            print(cb)
    return results

if __name__ == "__main__":
    queries = [
        "Tell me the name of every driver who is German"     
    ]
    res = run_agent(queries)
