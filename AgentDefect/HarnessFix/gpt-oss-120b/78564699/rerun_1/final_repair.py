import json
import os
from llama_index.llms.llama_cpp import LlamaCPP


def run_agent(query):
    """Run the LLM agent on the given query and return the textual answer.

    The LlamaCPP backend returns a ``CompletionResponse``; we extract the
    ``text`` field to satisfy the harness contract that expects a ``str``.
    """
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

    # ENHANCED_PROGRAM_V1: Extract answer text from CompletionResponse
    if not hasattr(response, "text"):
        raise TypeError(
            f"Expected CompletionResponse to have a 'text' attribute, got {type(response)}"
        )
    answer = response.text

    return answer.strip()
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

    return response

if __name__ == "__main__":
    query = "What is the capital of France?"
    response = run_agent(query)
    print(response)