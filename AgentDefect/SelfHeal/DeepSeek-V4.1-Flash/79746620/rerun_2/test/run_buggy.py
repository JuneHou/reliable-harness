from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from dotenv import load_dotenv


def run_agent(query):
    # Load environment variables from .env file
    load_dotenv()
    
    # Set up embedding model (will use OPENAI_API_KEY from .env)
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
    
    # Create node with None in metadata
    node_01 = TextNode(
        text="This document has None in the metadata",
        id_="node_01",
        metadata={"start_date": None},
    )
    
    # Create index
    doc_index = VectorStoreIndex([node_01])
    
    # Debug: Check what's actually stored
    print("Index nodes:")
    print([node.metadata for node in doc_index.docstore.docs.values()])
    print()
    
    # Try to filter by None value
    filter_null_start_date = MetadataFilter(
        key="start_date", 
        operator=FilterOperator.EQ, 
        value=None
    )
    filters = MetadataFilters(filters=[filter_null_start_date])
    retriever = doc_index.as_retriever(filters=filters, similarity_top_k=1)
    nodes = retriever.retrieve(query)
    
    # Show results
    print("Retrieved nodes:")
    print([(node.node_id, node.metadata) for node in nodes])
    print()
    
    return nodes


if __name__ == "__main__":
    query = "this"
    print(f"Query: '{query}'")
    print("-" * 50)
    
    response = run_agent(query)
    
    if not response:
        print("\nResult: No nodes retrieved (None is not filterable)")
    else:
        print(f"\nResult: Found {len(response)} node(s)")