import pandas as pd
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain.tools import tool
from langchain_community.tools import ShellTool
from langchain_openai import ChatOpenAI
from langchain_experimental.utilities import PythonREPL
from langchain import hub
import dotenv

dotenv.load_dotenv()


@tool
def load_excel_response(filepath: str):
    """Load an Excel file and return its table with the original column names."""
    return pd.read_excel(filepath).reset_index(drop=True)


def run_agent(user_prompt, file_name="data.json"):
    llm = ChatOpenAI(model="gpt-4o-mini")
    python_repl = PythonREPL()
    shell_tool = ShellTool()

    repl_tool = Tool(
        name="python_repl",
        description="Run Python commands in a REPL environment.",
        func=python_repl.run,
    )

    tools_list = [load_excel_response, repl_tool, shell_tool]
    prompt = hub.pull("hwchase17/react")

    shell_agent = create_react_agent(llm=llm, tools=tools_list, prompt=prompt)
    agent_executor = AgentExecutor(agent=shell_agent, tools=tools_list, verbose=True)

    response = agent_executor.invoke({"input": user_prompt})
    return response


if __name__ == "__main__":
    path = "excel_file.xlsx"
    user_prompt = (
        f"Load the Excel file located at {path} and assign the result "
        "to a variable named df."
    )
    result = run_agent(user_prompt)
    print(result)
