from pathlib import Path
import csv
import re


def run_agent(prompt):
    """Return movie titles whose genres include Action."""
    path = Path(__file__).resolve().parent / "movies.csv"

    with path.open(newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames:
            return ""

        # Match column names without depending on capitalization or spacing.
        columns = {name.strip().lower(): name for name in reader.fieldnames}
        title_column = columns.get("title")
        genres_column = columns.get("genres")
        if not title_column or not genres_column:
            return ""

        titles = []
        for row in reader:
            genres = row.get(genres_column, "") or ""
            if "action" in {genre.strip().lower() for genre in genres.split("|")}:
                title = (row.get(title_column) or "").strip()
                if title:
                    titles.append(title)

    return "\n".join(titles)


if __name__ == "__main__":
    print(run_agent("which movies are action"))
