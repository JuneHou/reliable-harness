import asyncio

async def run_agent(texts):
    import os
    from time import time

    import openai
    from dotenv import load_dotenv, find_dotenv
    from langchain.chains import LLMChain
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate

    _ = load_dotenv(find_dotenv())
    openai.api_key = os.getenv('OPENAI_API_KEY')

    llm = ChatOpenAI(temperature=0)

    prompt = ChatPromptTemplate.from_template(
        'Classify the text based on the Common European Framework of Reference '
        'for Languages (CEFR). Give a single value: {text}',
    )
    chain = LLMChain(llm=llm, prompt=prompt)

    start = time()
    res_aa = await chain.aapply(texts)
    print(res_aa)
    print(f"aapply time taken: {time() - start:.2f} seconds")
    print()
    return res_aa  # ENHANCED_PROGRAM_V1: make run_agent async and await aapply




if __name__ == "__main__":
    texts = [
        {'text': 'Hallo, ich bin 25 Jahre alt.'},
        {'text': 'Wie geht es dir?'},
        {'text': 'In meiner Freizeit, spiele ich gerne Fussball.'}
    ]
    result = asyncio.run(run_agent(texts))
    print("\nReturned result:", result)
