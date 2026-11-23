
from langchain_ollama import ChatOllama

def run_agent(input_text):
    llm = ChatOllama(
        model="qwen2.5:14b", temperature=0.7, top_p=0.95, num_ctx=2048, repeat_penalty=1.2,
        timeout=120,
    )
    response = llm.invoke(input_text)
    return response.content

if __name__ == '__main__':
    run_agent("Please tell me a lighthearted joke")