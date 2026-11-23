import os
import warnings
from dotenv import load_dotenv, find_dotenv
from langchain.document_loaders import CSVLoader
from langchain.callbacks import get_openai_callback
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
import json, re
try:
    import json5
except ImportError:
    json5 = None
import logging
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

warnings.filterwarnings('ignore')

load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")



# ENHANCED_PROGRAM_V1: Custom exception for parsing failures
class ParsingError(Exception):
    pass

# ENHANCED_PROGRAM_V1: Robust JSON extraction supporting json5 fallback
def _extract_json(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        raise ParsingError("No JSON block found in response")
    candidate = match.group(0)
    try:
        if json5:
            return json5.loads(candidate)
        else:
            return json.loads(candidate)
    except Exception as e:
        raise ParsingError(f"JSON parsing failed: {e}")

# ENHANCED_PROGRAM_V1: Persistence retry helper
def _run_with_persistence(qa_chain, query: str, max_tries: int = 3) -> str:
    persistence_instruction = (
        "IMPORTANT: If you cannot produce a valid JSON answer, please try again using the same context. "
        "Keep trying until you can output a well‑formed JSON object."
    )
    for attempt in range(1, max_tries + 1):
        # Append instruction on retries (skip on first attempt)
        prompt = query if attempt == 1 else f"{query}\n\n{persistence_instruction}"
        response = qa_chain.run(prompt)
        try:
            _ = _extract_json(response)  # validate
            return response
        except ParsingError:
            if attempt == max_tries:
                raise
            # otherwise continue to next attempt
    # Should not reach here
    return response

# ENHANCED_PROGRAM_V1: Structured JSON logger
agent_logger = logging.getLogger("agent_logger")
if not agent_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    agent_logger.addHandler(handler)
    agent_logger.setLevel(logging.INFO)

# ENHANCED_PROGRAM_V1: Simple memory scope placeholder (no-op for now)
class MemoryScope:
    def __enter__(self):
        # In a full implementation, clone vectorstore here
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original state if needed
        return False


def run_agent(queries):
    results = []
    files = ['drivers.csv','drivers_full.csv']
    for file in files:
        agent_logger.info(json.dumps({'event':'file_start','file':file}))
        with get_openai_callback() as cb:
            loader = CSVLoader(file_path=file,encoding='utf-8')
            docs = loader.load()
            embeddings = OpenAIEmbeddings()
            db = Chroma.from_documents(docs, embeddings)
            retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":1000})
            for query in queries:
                qa_stuff = RetrievalQA.from_chain_type(
                    llm=ChatOpenAI(temperature=0, model_name=os.getenv('OPENAI_MODEL_NAME', 'gpt-3.5-turbo')),
                    chain_type="map_reduce",
                    retriever=retriever,
                    verbose=True
                )
                agent_logger.info(json.dumps({'event':'query_start','query':query}))
                result = _run_with_persistence(qa_stuff, query)
                results.append(result)
                agent_logger.info(json.dumps({'event':'query_result','result':result}))
            agent_logger.info(json.dumps({'event':'callback','details':str(cb)}))
    return results
if __name__ == "__main__":
    queries = [
        "Tell me the name of every driver who is German"     
    ]
    res = run_agent(queries)
