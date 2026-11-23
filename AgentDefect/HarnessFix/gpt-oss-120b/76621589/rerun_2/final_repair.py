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
    res_a = chain.apply(texts)
    print(res_a)
    print(f"apply time taken: {time() - start:.2f} seconds")
    print()

    start = time()
    # ENHANCED_PROGRAM_V1: await async LLMChain call to avoid unawaited coroutine
    res_aa = await chain.aapply(texts)
    print(res_aa)
    print(f"aapply time taken: {time() - start:.2f} seconds")
    
    return res_aa



if __name__ == "__main__":
    texts = [
        {'text': 'Hallo, ich bin 25 Jahre alt.'},
        {'text': 'Wie geht es dir?'},
        {'text': 'In meiner Freizeit, spiele ich gerne Fussball.'}
    ]
    
    result = asyncio.run(run_agent(texts))
    print("\nReturned result:", result)
