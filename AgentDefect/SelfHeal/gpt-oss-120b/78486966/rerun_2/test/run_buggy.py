from langchain_text_splitters import CharacterTextSplitter


def run_agent(text_raw):
    text_splitter = CharacterTextSplitter(
        chunk_size=30,
        chunk_overlap=5
    )
    chunks=text_splitter.split_text(text_raw)
    return chunks


if __name__ == "__main__":
    text_raw = """
Water is life's matter and matrix, mother, and medium. There is no life without water.
Save water, secure the future.
Conservation is the key to a sustainable water supply.
Every drop saved today is a resource for tomorrow.
Let's work together to keep our rivers flowing and our oceans blue.
"""
    chunks = run_agent(text_raw)
    print(chunks)
    print(f'\n\n {len(chunks)}')