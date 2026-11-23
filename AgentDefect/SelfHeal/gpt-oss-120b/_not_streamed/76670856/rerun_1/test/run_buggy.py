from dotenv import load_dotenv
from pathlib import Path
import json
import os
import sys

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma
from langchain.document_loaders import JSONLoader

load_dotenv()

def run_agent(queries):

  data_dir = Path("data")
  data_dir.mkdir(exist_ok=True)

  review_file = data_dir / "review.json"

  if not review_file.exists():
      payload = {
          "reviews": [
              {"text": "Great hotel, excellent service and comfortable rooms."},
              {"text": "I had a terrible experience at this hotel. The room was dirty and the staff was rude."},
              {"text": "Highly recommended! The hotel has a beautiful view and the staff is friendly."},
              {"text": "Average hotel. The room was okay, but nothing special."},
              {"text": "I absolutely loved my stay at this hotel. The amenities were top notch."},
              {"text": "Disappointing experience. The hotel was overpriced for the quality provided."},
              {"text": "The hotel exceeded my expectations. The room was spacious and clean."},
              {"text": "Avoid this hotel at all costs! The customer service was horrendous."},
              {"text": "Fantastic hotel with a great location. I would definitely stay here again."},
              {"text": "Not a bad hotel, but there are better options available in the area."}
          ]
      }
      review_file.write_text(json.dumps(payload, indent=2))



  # Enable to save to disk & reuse the model (for repeated queries on the same data)
  PERSIST = False

  query = None
  if len(sys.argv) > 1:
    query = sys.argv[1]


  if PERSIST and os.path.exists("persist"):
    print("Reusing index...\n")
    vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
    index = VectorStoreIndexWrapper(vectorstore=vectorstore)
  else:

    loader = JSONLoader("data/review.json", jq_schema=".reviews[]", content_key='text') # Use this line if you only need data.json

    if PERSIST:
      index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
    else:
      index = VectorstoreIndexCreator().from_loaders([loader])

  chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    retriever=index.vectorstore.as_retriever()
  )

  chat_history = []
  results = []
  for query in queries:
    if query in ['quit', 'q', 'exit']:
      sys.exit()
    result = chain({"question": query, "chat_history": chat_history})
    print(result['answer'])
    results.append(result['answer'])
    chat_history.append((query, result['answer']))
    query = None
  return results