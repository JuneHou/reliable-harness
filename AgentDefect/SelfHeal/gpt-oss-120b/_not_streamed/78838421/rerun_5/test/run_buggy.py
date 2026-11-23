import logging
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_agent(question):
    local_path = "./paper1.pdf"
    try:
        # Local PDF file uploads
        if local_path:
            loader = UnstructuredPDFLoader(file_path=local_path)
            data = loader.load()
            logging.info("Loading of PDF is done")
        else:
            logging.error("Upload a PDF file")
            raise ValueError("No PDF file uploaded")
        
        # Preview first page
        logging.info(f"First page content preview: {data[0].page_content[:500]}...")
        
        # Split and chunk 
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
        logging.info("Text splitter created")
        chunks = text_splitter.split_documents(data)
        logging.info(f"Created {len(chunks)} chunks")
        
        logging.info("Creating Vector db")
        try:
            embedding_model = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
            print("Embedding", embedding_model)
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embedding_model,
                collection_name="local-rag"
            )
            logging.info("Local db created successfully")
        except Exception as e:
            logging.error(f"Error creating vector db: {e}")
              
        
        if vector_db:
            logging.info("Vector db verification successful")
        else:
            logging.error("Vector db creation failed")
            # raise ValueError("Vector db creation failed")
        
        # LLM from Ollama
        local_model = "llama3"
        llm = ChatOllama(model=local_model)
        logging.info("LLM model loaded")
        
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate five
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
        )
        logging.info("Query prompt created")
        
        retriever = MultiQueryRetriever.from_llm(
            vector_db.as_retriever(), 
            llm,
            prompt=QUERY_PROMPT
        )
        logging.info("Retriever created")
        
        # RAG prompt
        template = """Answer the question based ONLY on the following context:
{context}
    Question: {question}
    """
        prompt = ChatPromptTemplate.from_template(template)
        logging.info("RAG prompt created")
        
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        logging.info("Chain created")
        
        response = chain.invoke(question)
        print(response)
        logging.info("Chain invoked")
        logging.info(f"Response: {response}")
        
        return response
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None




if __name__ == "__main__":
    question = "What are the 5 pillars of global cooperation?"
    response = run_agent(question)
    print(f"\nFinal Output: {response}")