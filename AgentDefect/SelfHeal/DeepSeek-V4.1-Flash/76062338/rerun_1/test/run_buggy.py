import os
from typing import Any, List, Mapping, Optional
from dotenv import load_dotenv
from langchain.llms.base import LLM
from langchain.llms.openai import OpenAI
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain_experimental.tools import PythonAstREPLTool

load_dotenv()


class wrapper(LLM):
    llm: OpenAI
    log: str
    @property
    def _llm_type(self) -> str:
        return "custom"
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        reply = self.llm(prompt)
        f = open(self.log, 'a')
        f.write('\n{\n' + prompt + '\n}{\n' + reply + '\n}\n' + '.'*100)
        f.close()
        return reply
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"llm": self.llm}
    

def setup_components():
  
    llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )

    wllm = wrapper(llm=llm, log='output.log')

    tools = [PythonAstREPLTool()]
    
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    return wllm, tools, memory


def create_agent(wllm, tools, memory):
    agent = initialize_agent(
        tools,
        wllm,
        agent="conversational-react-description",
        verbose=True,
        memory=memory
    )
    return agent


def run_agent(prompt):
    
    try:
        wllm, tools, memory = setup_components()
        
    except Exception as e:
        return None
    
    try:
        agent = create_agent(wllm, tools, memory)
        
    except Exception as e:
        
        return None
    
    try:
        response = agent(prompt)
        return response
    except Exception as e:
        return None


if __name__ == "__main__":

    prompt = "What is 5-7?"
    
    response = run_agent(prompt)
    
    print(response)
    print(type(response), response["output"])