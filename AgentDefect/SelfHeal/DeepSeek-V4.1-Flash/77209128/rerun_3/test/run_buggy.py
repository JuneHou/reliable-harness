import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, JSON, Integer
from llama_index.core import SQLDatabase, VectorStoreIndex, Settings
from llama_index.core.objects import SQLTableNodeMapping, SQLTableSchema, ObjectIndex
from llama_index.core.query_engine import SQLTableRetrieverQueryEngine
from llama_index.llms.openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

pg_uri = os.environ.get('DATABASE_URL', 'sqlite:///test.db')

metadata_dict = {
    "page_call_phone_clicks_logged_in_unique": "Number of people who logged into Facebook and clicked the Call Now button. Ex: 2"
}

class SqlQueryEngine:
    
    def __init__(self):
        self.schema = []
    
    def query_engine(self):
        engine = create_engine(pg_uri)
        metadata_obj = MetaData()
        # Convert the metadata dictionary to a JSON string
        metadata_json = json.dumps(metadata_dict)
        # create snapshot SQL table
        table_name = "snapshots"
        snapshots_table = Table(
            table_name,
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("data", JSON, comment=metadata_json),
        )
        
        metadata_obj.create_all(engine)
        
        sql_database = SQLDatabase(engine)
        nodes = SQLTableNodeMapping(sql_database)
        
        self.schema = []
        for table_name in metadata_obj.tables.keys():
            self.schema.append(SQLTableSchema(table_name=table_name))
        
        # We dump the table schema information into a vector index. The vector index is stored
        # within the context builder for future use.
        index = ObjectIndex.from_objects(self.schema, nodes, VectorStoreIndex)
        llm = OpenAI(temperature=0.9, model="gpt-3.5-turbo")
        #depricated for new version
        # llm_predictor = LLMPredictor(llm=llm)
        # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
        Settings.llm = llm
        
        query_engine = SQLTableRetrieverQueryEngine(
            sql_database,
            index.as_retriever(similarity_top_k=1),
        )
        
        return query_engine

def run_agent(query: str):
    print("Initializing SQL Query Engine...")
    sql_engine = SqlQueryEngine()
    query_engine = sql_engine.query_engine()
    print("Query engine created successfully!")
    
    print(f"\nExecuting query: {query}")
    response = query_engine.query(query)
    print(f"Response: {response}")
    
    return sql_engine, response


if __name__ == "__main__":
    
    query = "What does the page_call_phone_clicks_logged_in_unique field mean in the data column?"
    sql_engine, response = run_agent(query)
    
    for schema_item in sql_engine.schema:
        print(f"\nTable: {schema_item.table_name}")
        if hasattr(schema_item, 'context_str') and schema_item.context_str:
            print(f"  context_str: {schema_item.context_str}")
            print("  Status: Metadata context is SET")
        else:
            print("  context_str: None")
            print("  Status: Metadata context is NOT SET")
