from pathlib import Path
import csv


def run_agent(prompt):
    """Return titles of movies tagged with the Action genre."""
    path = Path(__file__).resolve().parent / "movies.csv"

    with path.open(newline="", encoding="utf-8-sig") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames:
            return ""

        columns = {name.strip().lower(): name for name in reader.fieldnames}
        title_column = columns.get("title")
        genres_column = columns.get("genres")
        if not title_column or not genres_column:
            return ""

        titles = []
        for row in reader:
            genres = (row.get(genres_column) or "").split()
            if any(genre.casefold() == "action" for genre in genres):
                title = (row.get(title_column) or "").strip()
                if title:
                    titles.append(title)

    return "\n".join(titles)


if __name__ == "__main__":
    print(run_agent("which movies are action"))
