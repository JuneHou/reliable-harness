"""Draft evaluation inputs from published tasks and case assets.

Drafts stay unfrozen and hidden from the repair agent. They are not chosen
because a repair succeeded: no baseline repair has run.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from pathlib import Path

from motivation_pilot.inventory import REVIEW_PACKET

PUBLIC_ROLE = "public_reproducer"
RELATED_ROLE = "related"
REGRESSION_ROLE = "regression"


def _public_query(source: str) -> str:
    match = re.search(r'run_agent\(\s*"([^"]+)"\s*\)', source)
    if match:
        return match.group(1)
    match = re.search(r'query = "([^"]+)"', source)
    if match:
        return match.group(1)
    return ""


def _csv_rows(archive: zipfile.ZipFile, case_id: str, filename: str) -> list[dict]:
    key = f"AgentDefect/{case_id}/{filename}"
    if key not in archive.namelist():
        return []
    text = archive.read(key).decode("utf-8", errors="replace")
    return list(csv.DictReader(io.StringIO(text)))


def _titles(rows: list[dict], token: str) -> list[str]:
    return sorted(row["title"] for row in rows if token in row.get("genres", "").split())


def _title_overviews(rows: list[dict], token: str) -> list[dict]:
    return [
        {"title": row["title"], "overview": row.get("overview", "")}
        for row in sorted(rows, key=lambda item: item["title"])
        if token in row.get("genres", "").split()
    ]


def _genre_tokens(rows: list[dict]) -> list[str]:
    return sorted({token for row in rows for token in row.get("genres", "").split() if token})


def _related_from_catalog(rows: list[dict], skip: str, with_overview: bool) -> list[dict]:
    drafts = []
    for token in _genre_tokens(rows):
        if token == skip:
            continue
        expected = _title_overviews(rows, token) if with_overview else _titles(rows, token)
        if not expected:
            continue
        if with_overview:
            text = f"Find movies whose genres include {token}. Return each title with its description."
        else:
            text = f"Return all the {token.lower()} movie names"
        drafts.append({
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": text,
            "expected": expected,
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": f"genres column token {token}",
        })
        if len(drafts) == 2:
            break
    return drafts


def _excel_related(archive: zipfile.ZipFile, case_id: str) -> list[dict]:
    key = f"AgentDefect/{case_id}/excel_file.xlsx"
    if key not in archive.namelist():
        return []
    try:
        import pandas as pd
    except ImportError:
        return []
    blob = archive.read(key)
    try:
        frame = pd.read_excel(io.BytesIO(blob))
    except Exception:
        return []
    drafts = []
    for column in ("Sentiment", "Location"):
        if column not in frame.columns:
            continue
        values = [("" if value != value else str(value)) for value in frame[column].tolist()]
        drafts.append({
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": f"Read excel_file.xlsx and report the {column} value of each row, in order.",
            "expected": values,
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": f"excel_file.xlsx column {column}",
        })
    return drafts


def _building_related() -> list[dict]:
    """Expected phrases are the sentences stored in the case source, not a repair result."""
    return [
        {
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": "What are cars made out of?",
            "expected": ["Cars are made out of metal", "Cars are made out of plastic"],
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": "embedded notes in run_buggy.py",
        },
        {
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": "Which building materials do the notes name?",
            "expected": [
                "Buildings are made out of brick",
                "Buildings are made out of wood",
                "Buildings are made out of stone",
            ],
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": "embedded notes in run_buggy.py",
        },
    ]


def _animal_related() -> tuple[list[dict], dict]:
    related = [
        {
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": "The animal game has already been explained. The word is dog. Answer yes or no.",
            "expected": "yes",
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": "the published game rule: say whether the word is an animal",
        },
        {
            "role": RELATED_ROLE,
            "origin": "authored",
            "text": "In the same animal game, the word is table. Answer yes or no.",
            "expected": "no",
            "review_status": "pending",
            "frozen": False,
            "visible_to_repair_agent": False,
            "regression_verified": False,
            "source": "the published game rule: say whether the word is an animal",
        },
    ]
    regression = {
        "role": REGRESSION_ROLE,
        "origin": "authored",
        "text": "In the same animal game, the word is horse. Answer yes or no.",
        "expected": "yes",
        "review_status": "pending",
        "frozen": False,
        "visible_to_repair_agent": False,
        "regression_verified": False,
        "source": "published conversation uses horse; original-program pass is not yet observed",
    }
    return related, regression


def draft_tasks(config: dict) -> list[dict]:
    archive_path = Path(config["archive"])
    drafted = []
    with zipfile.ZipFile(archive_path) as archive:
        for case_id in REVIEW_PACKET:
            buggy = archive.read(f"AgentDefect/{case_id}/run_buggy.py").decode("utf-8", errors="replace")
            public = _public_query(buggy)
            if case_id == "78366661":
                public = "Search https://arxiv.org/pdf/2303.08774.pdf for how much compute GPT-4 training used, and return the matching passages."
            elif case_id == "78838421":
                public = "Give 10 quotes from this articles related to love?"
            elif case_id == "79343179":
                public = "Load the Excel file located at excel_file.xlsx and assign the result to a variable named df."
            elif case_id == "77099194":
                public = "Return all the action movies names"
            inputs = [{
                "role": PUBLIC_ROLE,
                "origin": "published",
                "text": public,
                "expected": None,
                "review_status": "pending",
                "frozen": False,
                "visible_to_repair_agent": True,
                "regression_verified": False,
                "source": "run_buggy.py entry",
            }]
            related: list[dict] = []
            regression = None
            if case_id == "77099194":
                rows = _csv_rows(archive, case_id, "movies.csv")
                inputs[0]["expected"] = _titles(rows, "Action")
                related = _related_from_catalog(rows, "Action", with_overview=False)
            elif case_id == "78383658":
                rows = _csv_rows(archive, case_id, "control.csv")
                inputs[0]["expected"] = _title_overviews(rows, "Family")
                related = _related_from_catalog(rows, "Family", with_overview=True)
            elif case_id == "79343179":
                related = _excel_related(archive, case_id)
            elif case_id == "77178370":
                inputs[0]["text"] = "What are buildings made of?"
                inputs[0]["expected"] = ["Buildings are made out of brick"]
                inputs[0]["source"] = "published test task and embedded notes"
                related = _building_related()
            elif case_id == "79149108":
                inputs[0]["text"] = (
                    "We are gonna play a game in which I'm gonna say some words and you have to "
                    "tell me if the word represents an animal. Just tell me yes or no."
                )
                inputs[0]["source"] = "published test game instruction"
                related, regression = _animal_related()
            if len(related) < 2:
                evidential_role = "public_reproducer_only"
                related = []
                regression = None
            else:
                evidential_role = "public_plus_authored_heldout"
            inputs.extend(related)
            if regression is not None:
                inputs.append(regression)
            drafted.append({
                "archive_folder": case_id,
                "evidential_role": evidential_role,
                "frozen": False,
                "inputs": inputs,
            })
    return [_review_case(item) for item in drafted]


def _scoring_rule(case_id: str, role: str) -> str:
    if case_id in {"77099194", "78383658"}:
        return "Compare the answer with the expected title set. Count every expected title that is missing, and every other catalog title that was added."
    if case_id == "77178370" and role == "public_reproducer":
        return "The answer must include the building materials named in the notes: brick, wood, and stone. Do not pass or fail on the word brick alone. Car materials are not building materials."
    if case_id == "77178370":
        return "The answer must include the phrases stored in the program notes for that question."
    if case_id == "79343179" and role != "public_reproducer":
        return "The answer must give the expected value of each row, in order. Mentioning the column name is not enough."
    if case_id == "79343179":
        return "The loaded table must keep all four rows and the six columns. The public task is to load the sheet, not to answer a new question."
    if case_id == "78366661":
        return "The search result must contain matching passages. An empty list fails. Do not split this repair into extra alternatives."
    return "Score only this published question. This case cannot support a claim about transfer to other questions."


def _review_case(item: dict) -> dict:
    """Record the review of each draft. Accepted questions are frozen. The study is not."""
    reasons = {
        "76897509": "The published question is kept. No second question was added, because the papers do not state another expected answer in the case files.",
        "78366661": "The published job is to search one outside PDF and return matching passages. The case has no second document, so no extra question was kept.",
        "77178370": "The extra questions use the same notes already stored in the program: cars, and the named building materials. They were not chosen after seeing a repair.",
        "78838421": "The published question about love quotes is kept. The paper does not list the quotes, so no extra question with a known answer was added.",
        "79343179": "The published program loads excel_file.xlsx into a table. Sentiment and Location are kept because they are columns in that table, including the rows the loader drops, and the expected answer is the exact value of each row in order. Column names and a row count were set aside because they do not check those lost row values.",
        "77099194": "The extra questions ask for every title of another genre in the same spreadsheet. The expected titles are the rows with that genre tag, which is stricter than the published test.",
        "79149108": "Dog and table follow the published yes-or-no animal rule. Horse is the published example and is not treated as already shown to work.",
        "78383658": "Family, Action, and Adventure titles and descriptions come from the spreadsheet. Name means the title column, and description means the overview column.",
    }
    item["review_reason"] = reasons[item["archive_folder"]]
    for task in item["inputs"]:
        task["review_status"] = "accepted"
        task["frozen"] = True
        task["review_reason"] = item["review_reason"]
        task["scoring_rule"] = _scoring_rule(item["archive_folder"], task["role"])
    item["frozen"] = False
    return item
