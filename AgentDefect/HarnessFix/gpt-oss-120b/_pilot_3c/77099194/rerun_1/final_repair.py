try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import re  # ENHANCED_PROGRAM_V1: import regex for year detection

def run_agent(prompt):
    
    embeddings = OpenAIEmbeddings()

    csvloader = CSVLoader("movies.csv")
    csvdocuments = csvloader.load()

    search = Chroma.from_documents(csvdocuments, embeddings)

    # Helper to create a retriever with broader context and optional year filter
    def make_retriever(search_obj, query: str):  # ENHANCED_PROGRAM_V1: dynamic retriever based on query
        """Return a retriever that fetches up to 10 documents.

        If the user query contains a four‑digit year (e.g., "1999"), the retriever
        applies a metadata filter on the year field so that only documents from
        that year are considered. This improves answers for year‑specific queries
        while preserving original behaviour for other queries.
        """
        year_match = re.search(r"\b(19|20)\d{2}\b", query)
        if year_match:
            try:
                year = int(year_match.group(0))
                return search_obj.as_retriever(search_kwargs={"k": 10, "filter": {"year": year}})
            except Exception:
                return search_obj.as_retriever(search_kwargs={"k": 10})
        return search_obj.as_retriever(search_kwargs={"k": 10})

    chain = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=0.3),
        retriever=make_retriever(search, prompt),  # ENHANCED_PROGRAM_V1: use expanded retriever
        return_source_documents=True,
    )
    result = chain({"question": prompt, 'chat_history': ""}, return_only_outputs=True)
    return result["answer"]

if __name__ == '__main__':
    print(run_agent("which movies are action"))
