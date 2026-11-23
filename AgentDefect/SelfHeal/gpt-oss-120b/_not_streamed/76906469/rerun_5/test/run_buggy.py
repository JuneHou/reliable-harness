from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.agents import load_tools
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in environment or .env file")

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0,
    openai_api_key=api_key
)

tools = load_tools(["llm-math", "wikipedia"], llm=llm)
memory = ConversationBufferMemory(memory_key="chat_history")

agent_test = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    memory=memory,
    verbose=False
)

def run_agent(prompt: str) -> str:
    return agent_test.run(prompt)


if __name__ == "__main__":
    result1 = run_agent("what is the capital of France?")
    print(result1)
    result2 = run_agent("what is the last question I asked?")
    print(result2)
