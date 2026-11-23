import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

load_dotenv()  

def get_output_parser():
    missing_id = ResponseSchema(name="identifier", description="This is missing identifier.")
    missing_text = ResponseSchema(name="text", description="This is missing text.")
    missing_assertions = ResponseSchema(name="assertions", description="List of assertion dictionaries.")

    response_schemas = [missing_id, missing_text, missing_assertions]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser


def predict_result(msg,PROMPT_TEMPLATE):
    model = ChatOpenAI(
        model="gpt-4o-mini", 
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=2000
    )

    output_parser = get_output_parser()
    format_instructions = output_parser.get_format_instructions()
    
    prompt = ChatPromptTemplate.from_template(template=PROMPT_TEMPLATE)
    message = prompt.format_messages(msg=msg, format_instructions=format_instructions)
    response = model.invoke(message)

    response_as_dict = output_parser.parse(response.content)
    # ENHANCED_PROGRAM_V1: validate presence of assertions key
    def _validate_parsed_output(res: dict):
        if "assertions" not in res:
            raise ValueError("Parsed output missing required \"assertions\" field.")
    _validate_parsed_output(response_as_dict)
    return response_as_dict



if __name__ == "__main__":
    test_msg = "ObjectNotFoundException AnyOf(AllOf(withId:identifier1, withText:text1),AllOf(withId:identifier2, withText:text1),AllOf(withId:identifier3, withText:text1))"
    PROMPT_TEMPLATE = """ 
    You are an android developer. 
    Parse this error message and provide me identifiers & texts mentioend in error message. 
    --------
    Error message is {msg}
    --------
    {format_instructions}
    """
    result = predict_result(test_msg,PROMPT_TEMPLATE)
    print(result)
    
