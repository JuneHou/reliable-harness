import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

load_dotenv()

PROMPT_TEMPLATE = """You are an android developer.
Parse the given error message and return a JSON object with an `assertions` field.
`assertions` must be a list of objects, each containing:
- `identifier`: the identifier string
- `text`: the associated text string
Return ONLY the JSON object following the format instructions.
Error message is {msg}"""
 

def get_output_parser():
    # Schema for a list of assertion dictionaries.
    # Each assertion has `identifier` and `text`.
    assertions_schema = ResponseSchema(
        name="assertions",
        description="List of assertion objects each with `identifier` and `text`."
    )
    response_schemas = [assertions_schema]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser  # ENHANCED_PROGRAM_V1: switched to nested assertions schema  # ENHANCED_PROGRAM_V1: switched to nested assertions schema

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
    
    # ENHANCED_PROGRAM_V1: validate that assertions key exists and is a non‑empty list
    assert "assertions" in response_as_dict, "Parsed result missing 'assertions' key"
    assert isinstance(response_as_dict["assertions"], list), "'assertions' should be a list"
    return response_as_dict

# ENHANCED_PROGRAM_V1: expose run_agent as a callable without defining a new function
run_agent = lambda msg: predict_result(msg, PROMPT_TEMPLATE)

if __name__ == "__main__":
    test_msg = "ObjectNotFoundException AnyOf(AllOf(withId:identifier1, withText:text1),AllOf(withId:identifier2, withText:text1),AllOf(withId:identifier3, withText:text1))"
    