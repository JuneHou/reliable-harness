import os
import warnings
from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import CSVLoader
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
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
                    llm=OpenAI(temperature=0,batch_size=20), 
                    chain_type="map_reduce", 
                    retriever=retriever,
                    verbose=True
                )

                print(query)
                result = qa_stuff.run(query)
                results.append(result)

                print(result)
                
            print(cb)
    return results

if __name__ == "__main__":
    queries = [
        "Tell me the name of every driver who is German"     
    ]
    res = run_agent(queries)