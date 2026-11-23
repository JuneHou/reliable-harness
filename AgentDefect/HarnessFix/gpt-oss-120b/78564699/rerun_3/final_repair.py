import json
import os
from llama_index.llms.llama_cpp import LlamaCPP


def run_agent(query):
    MODEL_URL = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_0.gguf"
    MODEL_PATH = None

    paths_file = "./paths.json"
    if os.path.exists(paths_file):
        with open(paths_file, "r") as f:
            paths = json.load(f)
            if "llama-2-13b-chat" in paths:
                MODEL_URL = None
                MODEL_PATH = paths["llama-2-13b-chat"]

    llm = LlamaCPP(
        model_url=MODEL_URL,
        model_path=MODEL_PATH,
        temperature=0.1,
        max_new_tokens=256,
        context_window=3900,
        model_kwargs={"n_gpu_layers": 0},  
        verbose=True,
    )

    response = llm.complete(query)
    # ENHANCED_PROGRAM_V1: extract answer text from CompletionResponse
    # Extract answer text from the LlamaCPP CompletionResponse
    if hasattr(response, "text"):
        answer = response.text
    elif isinstance(response, dict) and "choices" in response:
        answer = response["choices"][0].get("text", "")
    else:
        answer = str(response)  # defensive fallback

    return answer.strip()  # ENHANCED_PROGRAM_V1: return extracted answer string

if __name__ == "__main__":
    query = "What is the capital of France?"
    response = run_agent(query)
    print(response)
