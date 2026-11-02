import csv


def run_agent(query):
    """Return the title and overview for every movie tagged Family in control.csv."""
    with open("control.csv", newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        headers = reader.fieldnames or []

    normalized = {header.strip().lower(): header for header in headers}
    title_column = normalized.get("title")
    overview_column = normalized.get("overview")
    genres_column = normalized.get("genres")

    if not title_column or not overview_column or not genres_column:
        raise ValueError("control.csv must contain title, overview, and genres columns")

    family_movies = []
    for row in rows:
        genres = (row.get(genres_column) or "").strip()
        # Match the Family genre as a complete token, not as a substring.
        if "family" not in genres.casefold().split():
            continue
        family_movies.append(
            f"Name: {row.get(title_column, '') or ''}\n"
            f"Description: {row.get(overview_column, '') or ''}"
        )

    return "\n\n".join(family_movies) if family_movies else "I don't know."


if __name__ == "__main__":
    query = "Find movies for family, combining their Name and Description."
    print(run_agent(query))
