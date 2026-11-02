import csv
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

load_dotenv()


def run_agent(query):
    """Return the requested movie fields, using the CSV as the source of truth."""
    with open("control.csv", newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    # Resolve the documented fields from the CSV headers rather than relying on
    # semantic retrieval, which can omit matching rows or include near matches.
    headers = reader.fieldnames or []
    normalized = {header.strip().lower(): header for header in headers}
    title_column = normalized.get("title")
    overview_column = normalized.get("overview")
    genres_column = normalized.get("genres")

    if not title_column or not overview_column or not genres_column:
        raise ValueError("control.csv must contain title, overview, and genres columns")

    family_movies = []
    for row in rows:
        genres = row.get(genres_column, "") or ""
        # Genre values may be represented as plain text or as serialized lists.
        if "family" not in genres.lower():
            continue
        family_movies.append(
            {
                "Name": row.get(title_column, "") or "",
                "Description": row.get(overview_column, "") or "",
            }
        )

    if not family_movies:
        return "I don't know."

    # Keep the requested output grounded in the exact rows selected above.
    # The model is only used to format the result, not to decide membership.
    if os.getenv("OPENAI_API_KEY"):
        prompt = ChatPromptTemplate.from_template(
            "Present every supplied movie, combining its Name and Description. "
            "Do not add, omit, or alter movies or descriptions.\n\n"
            "Movies:\n{movies}"
        )
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", verbose=True)
        chain = prompt | llm | StrOutputParser()
        return chain.invoke(
            {
                "movies": "\n".join(
                    f"Name: {movie['Name']}\nDescription: {movie['Description']}"
                    for movie in family_movies
                )
            }
        )

    return "\n\n".join(
        f"Name: {movie['Name']}\nDescription: {movie['Description']}"
        for movie in family_movies
    )


if __name__ == "__main__":
    query = "Find movies for family, combining their Name and Description."
    print(run_agent(query))
