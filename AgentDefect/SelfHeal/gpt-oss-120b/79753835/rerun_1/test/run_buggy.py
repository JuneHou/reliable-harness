from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from transformers import AutoTokenizer
import os



def create_embedding_model(_chunk_size=None):
    print('loading embeddings...')
    if os.path.exists('./embeddings/models--BAAI--bge-m3'):
        _emb_model_name = "BAAI/bge-m3"
        _embed_model = HuggingFaceEmbedding(model_name=_emb_model_name, max_length=_chunk_size,
                                            cache_folder='./embeddings')
    else:
        os.makedirs("./embeddings", exist_ok=True)
        _emb_model_name = "BAAI/bge-m3"
        _embed_model = HuggingFaceEmbedding(model_name=_emb_model_name, max_length=_chunk_size,
                                            cache_folder='./embeddings')
    print('embeddings loaded')
    return _embed_model

def run_agent(text: str):
    chunk_size = 512
    embed_model = create_embedding_model(_chunk_size=chunk_size)

    token_counter = TokenCountingHandler()
    callback_manager = CallbackManager([token_counter])

    Settings.embed_model = embed_model
    Settings.callback_manager = callback_manager

    embedding_vector = Settings.embed_model.get_text_embedding(text)
    embedding_tokens = token_counter.total_embedding_token_count

    model_name = "BAAI/bge-m3"
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    tokenized_text = tokenizer(text)
    token_count = len(tokenized_text['input_ids'])
    return embedding_tokens, token_count

if __name__ == "__main__":
    text = "Random words. This is a test! A very exciting test, indeed."
    embedding_tokens, token_count = run_agent(text)
    print(f"The embedding model broke the text into: {embedding_tokens} tokens")
    print(f"The tokenizer broke the text into {token_count} tokens")