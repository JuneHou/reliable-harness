from tqdm import tqdm
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

def run_agent():

    embeddings = OpenAIEmbeddings()

    for db_collection_name in tqdm(["class1-sub2-chap3", "class2-sub3-chap4"]):
        documents = []
        doc_ids = []

        for doc_index in range(3):
            cl, sub, chap = db_collection_name.split("-")
            content = f"This is {db_collection_name}-doc{doc_index}"
            doc = Document(page_content=content, metadata={"chunk_num": doc_index, "chapter":chap, "class":cl, "subject":sub})
            documents.append(doc)
            doc_ids.append(str(doc_index))


        db = Chroma.from_documents(
            collection_name=db_collection_name,
            documents=documents, ids=doc_ids,
            embedding=embeddings, 
            persist_directory="./data")
        
        db.persist()
        
    initial_content = "This is an initial document content"
    document_id = "doc1"


    original_doc = Document(page_content=initial_content, metadata={"page": "0"})

    
    new_db = Chroma.from_documents(
        collection_name="test_collection",
        documents=[original_doc],
        embedding=embeddings,  
        ids=[document_id],
    )

    return db._collection.get()


if __name__ == "__main__":
    result = run_agent()
    print(result)
    