import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

load_dotenv()  

def get_output_parser():
    # ENHANCED_PROGRAM_V1: define a single response schema named `assertions` `assertions`
    assertions_schema = ResponseSchema(
        name="assertions",
        description="A JSON array of objects, each with fields identifier (string) and text (string)."
    )
    output_parser = StructuredOutputParser.from_response_schemas([assertions_schema])
    return output_parser


def predict_result(msg, PROMPT_TEMPLATE):
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
    return response_as_dict

# ENHANCED_PROGRAM_V1: expose the required run_agent interface
def run_agent(msg):
    # Wrapper that uses a default prompt template to parse the given message.
    # Returns the dictionary produced by predict_result.
    PROMPT_TEMPLATE = """You are an android developer.
Parse this error message and provide the identifiers & texts mentioned in the error message as a JSON array under the key `assertions`
--------
Error message is {msg}
--------
{format_instructions}
Example output:
{"assertions": [{"identifier": "id1", "text": "text1"}, {"identifier": "id2", "text": "text2"}]}
"""
    return predict_result(msg, PROMPT_TEMPLATE)


if __name__ == "__main__":
    test_msg = "ObjectNotFoundException AnyOf(AllOf(withId:identifier1, withText:text1),AllOf(withId:identifier2, withText:text1),AllOf(withId:identifier3, withText:text1))"
    result = run_agent(test_msg)
    print(result)
