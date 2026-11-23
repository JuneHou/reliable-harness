import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

load_dotenv()

def get_output_parser():
    # ENHANCED_PROGRAM_V1: add assertions response schema to match test expectations
    assertions_schema = ResponseSchema(
        name="assertions",
        description="A list of objects each containing 'identifier' and 'text' strings."
    )
    # Define the parser with only the assertions schema
    output_parser = StructuredOutputParser.from_response_schemas([assertions_schema])
    return output_parser

def predict_result(msg, PROMPT_TEMPLATE):
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2000,
    )

    output_parser = get_output_parser()
    format_instructions = output_parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_template(template=PROMPT_TEMPLATE)
    message = prompt.format_messages(msg=msg, format_instructions=format_instructions)
    response = model.invoke(message)

    response_as_dict = output_parser.parse(response.content)
    # ENHANCED_PROGRAM_V1: wrap legacy identifier/text into assertions if present
    if isinstance(response_as_dict, dict) and "identifier" in response_as_dict and "text" in response_as_dict:
        response_as_dict = {"assertions": [{"identifier": response_as_dict["identifier"], "text": response_as_dict["text"]}]}
    return response_as_dict

if __name__ == "__main__":
    test_msg = "ObjectNotFoundException AnyOf(AllOf(withId:identifier1, withText:text1),AllOf(withId:identifier2, withText:text1),AllOf(withId:identifier3, withText:text1))"
    PROMPT_TEMPLATE = """ 
    You are an android developer. 
    Parse this error message and provide a JSON object with an \"assertions\" field. Each entry must contain \"identifier\" and \"text\". 
    --------
    Error message is {msg}
    --------
    {format_instructions}
    """
    result = predict_result(test_msg, PROMPT_TEMPLATE)
    print(result)
