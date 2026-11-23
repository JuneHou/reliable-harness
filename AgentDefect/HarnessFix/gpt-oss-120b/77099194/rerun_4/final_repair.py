from dotenv import load_dotenv

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI

load_dotenv()
def run_agent(prompt):
    
    embeddings = OpenAIEmbeddings()

    csvloader = CSVLoader("movies.csv")
    csvdocuments=csvloader.load()

    search = Chroma.from_documents(csvdocuments, embeddings)


    chain = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.3), 
                                    retriever=search.as_retriever(search_kwargs={"k": 10}),  # ENHANCED_PROGRAM_V1: increase retrieval depth to capture all relevant movies
                                    return_source_documents=True)
    result = chain({"question": prompt, 'chat_history': ""}, return_only_outputs=True)
    return result["answer"]

if __name__ == '__main__':
    print(run_agent("which movies are action"))