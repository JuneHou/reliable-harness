import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Performs basic arithmetic"

    def _run(self, query: str) -> str:
        return str(eval(query))

    async def _arun(self, query: str) -> str:
        raise NotImplementedError()


def create_agent():
    llm_gpt4 = ChatOpenAI(model="gpt-4", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return initialize_agent(
        agent="chat-conversational-react-description",
        tools=[CalculatorTool()],
        llm=llm_gpt4,
        verbose=True,
        max_iterations=2,
        early_stopping_method="generate",
        memory=memory,
        # agent_kwargs=dict(output_parser=output_parser),
    )


def run_agent(prompt: str) -> str:
    agent = create_agent()
    return agent.run(prompt)
