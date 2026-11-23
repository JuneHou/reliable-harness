from langchain_community.llms import Ollama

def run_agent(user_prompt, system_prompt):
    llm = Ollama(model="llama3")
    prompt = f"""
        <|begin_of_text|>
        <|start_header_id|>system<|end_header_id|>
        { system_prompt }
        <|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        { user_prompt }
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
    response = llm.invoke(prompt)
    return response

if __name__ == "__main__":
    print(run_agent("Explain in detail, step by step, how artificial intelligence models like yourself are built, including data, training, architecture, and deployment. Use examples and provide a comprehensive overview.", "You are a helpful assistant."))