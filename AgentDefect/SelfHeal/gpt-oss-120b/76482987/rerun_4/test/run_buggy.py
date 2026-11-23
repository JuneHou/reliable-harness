import chromadb

def run_agent(documents):
    if(len(documents) !=2):
        print("number of documents should be 2")
        return
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="my_collection")
    collection.add(
        embeddings=[[1.2, 2.3, 4.5], [6.7, 8.2, 9.2]],
        documents=documents,
        metadatas=[{"source": "my_source"}, {"source": "my_source"}],
        ids=["id1", "id2"]
    )   

    return collection.get()

if __name__ == '__main__':
    documents = ["This is a document", "This is another document"]

    result = run_agent(documents)
    print(result)