from flask import Flask, render_template, request
from ollama import chat
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
import tiktoken

app = Flask(__name__)

MODEL = "llama3.2"
MODEL_MAX_TOKENS = 128000
messages = []

llm = ChatOllama(
    model=MODEL,
    temperature=1.1,
    stream=True
)

def get_number_of_tokens(messages):
    try:
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        total_tokens = 0
        for role, content in messages:
            total_tokens += len(encoding.encode(str(content)))
        return total_tokens
    except:
       
        total_chars = sum(len(str(content)) for role, content in messages)
        return total_chars // 4

@app.route('/ask_gpt', methods=['POST'])
def ask_gpt():
    messages.append(("user", request.form['text']))
    number_of_tokens = get_number_of_tokens(messages)
    while(number_of_tokens >= MODEL_MAX_TOKENS):
        del(messages[1])
    
    ai_msg = llm.invoke(messages)
    return ai_msg.content

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)