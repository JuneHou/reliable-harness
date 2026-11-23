from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.globals import set_verbose
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment or .env file")

set_verbose(True)

def run_agent(topic: str) -> str:
    model = ChatOpenAI(openai_api_key=api_key)
    output_parser = StrOutputParser()
    prompt_template = "tell me a joke about {topic}"
    prompt = ChatPromptTemplate.from_template(prompt_template)
    chain = prompt | model | output_parser
    return chain.invoke({"topic": topic})

if __name__ == "__main__":
    result = run_agent("ice cream")
    print("Generated output:", result)
