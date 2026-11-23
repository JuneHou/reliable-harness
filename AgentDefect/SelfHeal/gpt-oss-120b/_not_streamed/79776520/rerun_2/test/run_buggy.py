import os
from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


def initialize_agent():
    load_dotenv()

    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file")
    simple_search=TavilySearch(max_result=2)
    tools = [simple_search]

    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=google_api_key
    )

    memory = MemorySaver()
    agent_executor = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=memory
    )

    config = {"configurable": {"thread_id": "agent003"}}
    return agent_executor, memory, config


def run_agent(agent_executor, memory, config, user_input):
    state = memory.get(config)

    if state and "channel_values" in state and "messages" in state["channel_values"]:
        history = state["channel_values"]["messages"]
        full_context = {"messages": history + [HumanMessage(user_input)]}
    else:
        full_context = {"messages": [HumanMessage(user_input)]}

    for step in agent_executor.stream(
        full_context,
        config,
        stream_mode="values"
    ):
        final_message = step["messages"][-1]
    return final_message.content


def main():
    agent_executor, memory, config = initialize_agent()
    response1 = run_agent(agent_executor, memory, config, "Hi! I am Bob!")
    response2 = run_agent(agent_executor, memory, config, "What's my name?")
    print(response1)
    print(response2)


if __name__ == "__main__":
    main()
