import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def run_agent(prompt: str) -> str:   
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(openai_api_key=api_key)
    
    response = llm.invoke(prompt)
    return response

if __name__ == "__main__":
    user_prompt = "How can LangSmith help with testing?"
    answer = run_agent(user_prompt)
    print("LLM response:", answer)
