"""AgentDefect motivation pilot extension exp-2026-10-22.

Among the existing complete repairs, which persistent component changes are
required, removable or dependent, and does measuring that change the repair we
would keep. Plan: ~/.claude/plans/back-to-agent-defect-deep-blossom.md

    PYTHONPATH=src python -m motivation_pilot.extension map|manifest|selftest|live|compare|report
"""

from __future__ import annotations

import argparse
import ast
import builtins
import csv
import hashlib
import inspect
import io
import itertools
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from motivation_pilot import instrument
from motivation_pilot import pilot_run as pr
from motivation_pilot.cli import load_config

EXP_ID = "exp-2026-10-22"
ROOT = pr.ROOT
REPO = ROOT.parent
OUT = ROOT / "artifacts" / "agentdefect_extension" / EXP_ID
NUMBERS = ROOT / "NUMBERS.md"
ORACLE = ROOT / "artifacts" / "frozen_oracles_v2.json"  # v2 per oracle_corrections.json, Jun 2026-10-22
HISTORICAL = "cb39baa"
REPETITIONS = 3
EXPECTED_SETTINGS = {"subject_model": "gpt-6-luna", "subject_temperature": 0, "reasoning_effort": "none", "repetitions": 3}
EMBED_PRICE = 0.10 / 1_000_000  # text-embedding-ada-002, assumed and unverified
COMPLETED = ("completed_pass", "behavioral_failure", "interface_runtime_failure")
CASE_ORDER = ["76906469", "79343179", "78366661", "77178370", "77099194", "78383658"]
CONTROLS = ["76897509", "78838421", "79149108"]
LEAKED = {
    "77178370": {"baseline": "Leaked, audit only"},
    "78383658": {"attempt_1": "Leaked, audit only", "attempt_2": "Leaked by lineage"},
}
TURNS = ["what is the capital of France?", "what is the last question I asked?"]
PDF_URL = "https://arxiv.org/pdf/2303.08774.pdf"
LOADER_COLUMNS = ["UserName", "ScreenName", "Location", "TweetAt", "OriginalTweet", "Sentiment"]

# Inputs and scoring as in pilot_run.evaluate and pilot_run.local_checks.
BUILDINGS = [
    ("buildings", "public_reproducer", "What are buildings made of?", ["brick", "wood", "stone"], ["metal", "plastic"]),
    ("cars", "related", "What are cars made out of?", ["metal", "plastic"], []),
    ("materials", "related", "Which building materials do the notes name?", ["brick", "wood", "stone"], []),
]
MOVIES = {
    "77099194": ("movies.csv", [
        ("action", "public_reproducer", "Return all the action movies names", "Action"),
        ("adventure", "related", "Return all the adventure movie names", "Adventure"),
        ("animation", "related", "Return all the animation movie names", "Animation"),
    ]),
    "78383658": ("control.csv", [
        ("family", "public_reproducer", "Find movies for family, combining their Name and Description.", "Family"),
        ("action", "related", "Find movies whose genres include Action. Return each title with its description.", "Action"),
        ("adventure", "related", "Find movies whose genres include Adventure. Return each title with its description.", "Adventure"),
    ]),
}

# ---------------------------------------------------------------- actions (Appendix A)

N_EDITS = [
    ('def run_agent(pdf_url):', 'def run_agent(pdf_url, query="What were the compute requirements for training GPT 4"):'),
    ('    query = "What were the compute requirements for training GPT 4"\n\n', ''),
    ('    text_splitter = RecursiveCharacterTextSplitter(\n        chunk_size=1000,\n        chunk_overlap=100\n    )\n\n', ''),
    ('    data = loader.load()\n',
     '    data = loader.load()\n    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)\n'),
]
P1_EDITS = [
    ('from langchain.text_splitter import RecursiveCharacterTextSplitter\n',
     'from langchain.text_splitter import RecursiveCharacterTextSplitter\nfrom langchain.vectorstores import Chroma\n'),
    ('    class DummyVectorSearch:\n        def similarity_search(self, query):\n            return []\n\n'
     '    class MongoDBAtlasVectorSearch:\n        @classmethod\n        def from_documents(cls, documents, embedding, collection, index_name):\n'
     '            return DummyVectorSearch()\n\n    atlas_collection = []\n\n', ''),
    ('    vector_search_index = "vector_index"\n\n', ''),
    ('    vector_search = MongoDBAtlasVectorSearch.from_documents(\n        documents=docs,\n'
     '        embedding=OpenAIEmbeddings(disallowed_special=()),\n        collection=atlas_collection,\n'
     '        index_name=vector_search_index\n    )',
     '    vector_search = Chroma.from_documents(\n        documents=docs,\n        embedding=OpenAIEmbeddings()\n    )'),
]
P2_EDITS = [('chunk_overlap=100', 'chunk_overlap=150')]

P_CORE_EDITS = [
    ('from langchain.chains import ConversationalRetrievalChain \n', 'from langchain.chains import RetrievalQA\n'),
    ('from langchain.prompts import PromptTemplate\n',
     'from langchain.prompts import PromptTemplate\nfrom langchain.agents import AgentExecutor, Tool, initialize_agent\n'
     'from langchain.agents.types import AgentType\n'),
    ('    custom_template = """\nThis is conversation with a human. Answer the questions you get based on the knowledge you have.\n'
     'If you don\'t know the answer, just say that you don\'t, don\'t try to make up an answer.\nChat History:\n{chat_history}\n'
     'Follow Up Input: {question}\n"""\n    CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)\n', ''),
    ('    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)\n',
     '    memory = ConversationBufferMemory(memory_key="chat_history", input_key=\'input\', return_messages=True, output_key=\'output\')\n'),
    ('    qa = ConversationalRetrievalChain.from_llm(\n        llm,\n        retriever,\n        condense_question_prompt=CUSTOM_QUESTION_PROMPT,\n'
     '        memory=memory\n    )\n    query = "what are cars made of?"\n    result = qa({"question": query})\n'
     '    result= retriever.get_relevant_documents(query)\n    \n    return result\n',
     '    qa = RetrievalQA.from_chain_type(\n            llm=llm,\n            chain_type="stuff",\n            retriever=vectorstore.as_retriever(),\n'
     '            verbose=True,\n            return_source_documents=True\n        )\n    tools = [\n            Tool(\n'
     '                name="doc_search_tool",\n                func=qa,\n                description=(\n'
     '                   "This tool is used to retrieve information from the knowledge base"\n                )\n            )\n        ]\n'
     '    agent = initialize_agent(\n            agent = AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,\n            tools=tools,\n'
     '            llm=llm,\n            memory=memory,\n            return_source_documents=True,\n            return_intermediate_steps=True\n'
     '            )\n    user_result = agent(user_input)\n    return user_result\n'),
]
P_SYS_EDITS = [
    ('    llm = ChatOpenAI(\n',
     '    system_message = """\n"You are the XYZ bot."\n"This is conversation with a human. Answer the questions you get based on the knowledge you have."\n'
     '"If you don\'t know the answer, just say that you don\'t, don\'t try to make up an answer."\n"""\n    llm = ChatOpenAI(\n'),
    ('            return_intermediate_steps=True\n            )',
     '            return_intermediate_steps=True,\n            agent_kwargs={"system_message": system_message}\n            )'),
]
K_EDITS = [('{"k": 1}', '{"k": 12}')]
U2_NEW = ('    template = """You are an assistant for question answering tasks.\n\nUse the following retrieved context to answer the question.\n\n'
          'If the information is not present, return an empty list.\n\nQuestion: {question}\n\nContext: {context}\n"""')
U1_EDITS = [
    ('from langchain.schema.output_parser import StrOutputParser\n',
     'from langchain.output_parsers import StructuredOutputParser, ResponseSchema\n'),
    ('    retriever = vectorstore.as_retriever()\n',
     '    retriever = vectorstore.as_retriever()\n    response_schema = ResponseSchema(\n        name="results",\n'
     '        description=\'\'\'A list of objects like:\n        [{"title": "", "genre": "", "budget": ""}]\'\'\'\n    )\n'
     '    output_parser = StructuredOutputParser.from_response_schemas(\n        [response_schema]\n    )\n'
     '    format_instructions = output_parser.get_format_instructions()\n'),
    ('Context: {context}\n', 'Context: {context}\n\n{format_instructions}\n'),
    ('{"context": retriever,  "question": RunnablePassthrough()}',
     '{"context": retriever,  "question": RunnablePassthrough(), "format_instructions": lambda _: format_instructions}'),
    ('| StrOutputParser()', '| output_parser'),
]
LOADER_LINE = "    df = pd.read_excel(filepath, skiprows=2, names=['responses']).reset_index(drop=True)\n"
L3_LINE = "    df = df.select_dtypes(include=['object'])\n"
DV_EDITS = [
    ('    """Load an Excel file and return a transformed DataFrame."""\n    df = pd.read_excel(filepath).reset_index(drop=True)\n'
     '    return df # df.to_json()',
     '    """Load an Excel file and return its table with the original column names."""\n'
     '    return pd.read_excel(filepath).reset_index(drop=True)'),
]

COMPONENTS = {
    "76906469": {"A": ["memory_representation"], "B": ["agent_control"]},
    "79343179": {"L1": ["loader"], "L2": ["loader"], "L3": ["loader"], "DV": ["loader"]},
    "78366661": {"N": ["execution_control", "document_splitting"], "P1": ["vector_store"], "P2": ["document_splitting"],
                 "R": ["vector_store"]},
    "77178370": {"E1": ["execution_control"], "P_core": ["prompt", "memory", "chain_control", "execution_control", "tools"],
                 "P_sys": ["prompt"]},
    "77099194": {"K": ["retrieval"], "W1": ["model_client", "data_loading", "retrieval", "chain_control"],
                 "W2": ["model_client", "data_loading", "retrieval", "chain_control"]},
    "78383658": {"U1": ["output_parsing", "prompt", "chain_control"], "U2": ["prompt"]},
}
ANCHORS = {
    "76906469": {"model_client": "lines 13 to 17", "tools": "line 19", "memory_representation": "line 20", "agent_control": "lines 22 to 29"},
    "79343179": {"loader": "load_excel_response, lines 12 to 17"},
    "78366661": {"vector_store": "lines 16 to 23 and 39 to 44", "document_splitting": "lines 27 to 30",
                 "document_loading": "lines 32 to 35", "execution_control": "lines 9 and 46"},
    "77178370": {"prompt": "lines 18 to 25", "retrieval": "lines 30 to 41", "memory": "line 42", "chain_control": "lines 43 to 48",
                 "execution_control": "lines 49 to 53", "tools": "added by the published fix"},
    "77099194": {"model_client": "lines 13 and 21", "data_loading": "lines 15 to 16", "retrieval": "lines 18 and 22",
                 "chain_control": "lines 21 to 25"},
    "78383658": {"data_loading": "lines 16 to 19", "retrieval": "lines 20 to 21", "prompt": "lines 22 to 38",
                 "output_parsing": "line 41", "chain_control": "lines 41 to 44"},
}
NON_BEHAVIOURAL = {"N", "DV"}
PRECONDITIONS = {"B": ["A"], "P_sys": ["P_core"]}
SYMBOLS = {
    "P_sys": ["system_message"],
    "P_core": ["RetrievalQA", "initialize_agent", "AgentType", "doc_search_tool", "user_result"],
    "U1": ["format_instructions", "output_parser", "response_schema", "StructuredOutputParser", "ResponseSchema"],
    "P1": ["Chroma"],
}
VIOLATION_PATTERNS = {"B": "should be a list of base messages"}
FOOTPRINT = {"A": (1, 1), "B": (1, 1), "L1": (1, 1), "L2": (1, 1), "L3": (1, 0), "DV": (3, 2), "N": (2, 1), "P1": (5, 2),
             "P2": (1, 1), "E1": (4, 2), "P_core": (9, 9), "P_sys": (1, 2), "K": (1, 1), "U1": (3, 6), "U2": (1, 1),
             "W1": None, "W2": None}
REORDERS = {"N"}
KEYWORD = {"L1": "skiprows", "L2": "names"}

# Plan Appendix C.
INITIAL = {
    "76906469": ("AB", "historical table, AB the only arm with successes (240)"),
    "79343179": ("baseline", "pilot loader check passed"),
    "78366661": ("baseline", "pilot nonempty_result 3/3"),
    "77178370": ("published", "baseline leaked, audit failed its public run, published passed its one public run"),
    "77099194": ("attempt_2", "pilot public 3/3, the pilot's selection rule first public success"),
    "78383658": (None, "attempts leaked, published failed its one public run"),
}

PROBE = {
    "76906469": {"order": ["memory", "chat_request", "network_attempt", "agent_parsers", "tools"],
                 "default": {"expected": ["memory", "chat_request", "network_attempt", "agent_parsers"], "optional": ["tools"], "removed": []}},
    "79343179": {"order": ["loader"], "default": {"expected": ["loader"], "optional": [], "removed": []}},
    "78366661": {"order": ["embeddings", "network_attempt", "direct_search"],
                 "default": {"expected": [], "optional": [], "removed": ["embeddings", "network_attempt", "direct_search"]},
                 "N+P1": {"expected": ["embeddings", "network_attempt", "direct_search"], "optional": [], "removed": []},
                 "published": {"expected": ["embeddings", "network_attempt", "direct_search"], "optional": [], "removed": []}},
    "77178370": {"order": ["embeddings", "network_attempt", "memory", "retrieval", "chat_request", "agent_parsers", "tools"],
                 "default": {"expected": ["embeddings", "network_attempt", "memory", "retrieval", "chat_request"], "optional": [],
                             "removed": ["agent_parsers"]},
                 "P_core": {"expected": ["embeddings", "network_attempt", "memory", "chat_request", "agent_parsers"],
                            "optional": ["tools", "retrieval"], "removed": []},
                 "published": {"expected": ["embeddings", "network_attempt", "memory", "chat_request", "agent_parsers"],
                               "optional": ["tools", "retrieval"], "removed": []}},
    "77099194": {"order": ["embeddings", "network_attempt", "retrieval", "chat_request"],
                 "default": {"expected": ["embeddings", "network_attempt", "retrieval", "chat_request"], "optional": [], "removed": []},
                 "attempt_1": {"expected": [], "optional": [], "removed": ["embeddings", "network_attempt", "retrieval", "chat_request"]},
                 "attempt_2": {"expected": [], "optional": [], "removed": ["embeddings", "network_attempt", "retrieval", "chat_request"]}},
    "78383658": {"order": ["embeddings", "network_attempt", "retrieval", "chat_request", "parsers"],
                 "default": {"expected": ["embeddings", "network_attempt", "retrieval", "chat_request", "parsers"], "optional": [], "removed": []}},
}

# Plan Appendix B, keyed by (case, change); "B_diag" covers both B diagnostics.
HYPOTHESES = {
    ("76906469", "A"): ("both fail", ["memory_before type from str to list"], ["turn 2 request lacks the turn 1 question in both"],
                        "A's turn 2 request holds 'capital of France'", "historical table"),
    ("76906469", "B"): ("required_in_context", ["turn 2 request holds turn 1 messages under AB"], ["memory_before type list in both"],
                        "AB passes while its turn 2 request lacks the turn 1 question", "historical table, AB 240 success"),
    ("76906469", "B_diag"): ("B stops at the memory and prompt boundary", [], ["zero backend_attempt"], "any backend_attempt under B",
                             "smoke record"),
    ("79343179", "L1"): ("required", ["loader_output rows rise and London and UK appear"], ["column names"], "unchanged row count",
                         "pilot baseline passed"),
    ("79343179", "L2"): ("required", ["column names become the six names"], ["row count"], "unchanged column names", "pilot baseline passed"),
    ("79343179", "L3"): ("removable", ["nothing when every column is object dtype"], ["columns", "rows", "values"],
                         "a column set change while every dtype is object", "none"),
    ("79343179", "DV"): ("removable", ["nothing"], ["every loader_output field"], "any field change", "none"),
    ("78366661", "N"): ("neither recovers", ["nothing"], ["zero passages", "zero embedding events"], "any change", "none"),
    ("78366661", "P1"): ("required", ["passages from zero to above zero", "embedding events appear"], ["chunk count"],
                         "zero passages under P1", "pilot original zero passages"),
    ("78366661", "P2"): ("removable", ["chunk count 361 to 366"], ["passage count stays zero without P1"], "passages without P1",
                         "PDF measured 2026-10-22"),
    ("77178370", "E1"): ("public not 3/3", ["retrieval query becomes the asked question", "building notes retrieved"], ["condense prompt"],
                         "car notes still retrieved", "pilot audit missed stone once"),
    ("77178370", "P_core"): ("P_core adequate", ["tool_call to doc_search_tool appears", "building notes retrieved"], ["retriever settings"],
                             "a pass with no tool call and no building note in any request", "pilot published public pass once"),
    ("77178370", "P_sys"): ("removable", ["the system message text in the request"], ["retrieved notes", "tool calls"],
                            "retrieved notes differ between the sides", "none"),
    ("77099194", "K"): ("published adequate", ["retrieved documents from 1 to 12 per question"], ["prompt template"],
                        "unchanged retrieval count", "pilot published public pass once"),
    ("77099194", "W1"): ("inadequate on related", ["retrieval boundary removed_or_rerouted"], [], "retrieval events under W1",
                         "pilot attempt_1 public failed"),
    ("77099194", "W2"): ("inadequate on related", ["retrieval boundary removed_or_rerouted"], [], "retrieval events under W2",
                         "pilot attempt_2 related 0/3"),
    ("78383658", "U1"): ("not adequate", ["request holds format instructions", "parser input JSON-like", "parser output dict"],
                         ["retrieved documents", "other request wording"], "retrieved documents differ between the sides",
                         "pilot published missed Harry Potter once"),
    ("78383658", "U2"): ("not adequate", ["request holds 'return an empty list' and lacks 'three sentences maximum'"],
                         ["retrieved documents", "parser class"], "retrieved documents differ, or the parser class changes",
                         "pilot published missed Harry Potter once"),
}

# ---------------------------------------------------------------- helpers


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def archive_text(case: str, name: str) -> str:
    with zipfile.ZipFile(pr.ARCHIVE) as archive:
        return archive.read(f"AgentDefect/{case}/{name}").decode("utf-8")


def git_show(path: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{HISTORICAL}:{path}"], capture_output=True, text=True, check=True).stdout


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"expected one occurrence, found {count}: {old[:60]!r}")
    return source.replace(old, new, 1)


def apply_edits(source: str, edits: list[tuple[str, str]]) -> str:
    for old, new in edits:
        source = replace_once(source, old, new)
    return source


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def safe_id(text: str) -> str:
    return text.replace("+", "_")


# ---------------------------------------------------------------- configurations


def _case_actions(case: str, original: str) -> dict[str, list[tuple[str, str]]]:
    if case == "76906469":
        repairs = json.loads(git_show("repair_family_pilot/artifacts/manifests/provisional_candidate.json"))["repairs"]
        return {r["repair_id"]: [(r["old"], r["new"])] for r in repairs}
    if case == "78366661":
        return {"N": N_EDITS, "P1": P1_EDITS, "P2": P2_EDITS}
    if case == "77178370":
        return {"E1": [(pr.AUDIT_OLD, pr.AUDIT_NEW)], "P_core": P_CORE_EDITS, "P_sys": P_SYS_EDITS}
    if case == "77099194":
        return {"K": K_EDITS}
    if case == "78383658":
        start = original.index('    template = """')
        end = original.index('"""', start + len('    template = """')) + 3
        return {"U2": [(original[start:end], U2_NEW)], "U1": U1_EDITS}
    return {}


ACTION_ORDER = {"76906469": ["A", "B"], "78366661": ["N", "P1", "P2"], "77178370": ["E1", "P_core", "P_sys"],
                "77099194": ["K"], "78383658": ["U2", "U1"]}


def compose(original: str, edits: dict, case: str, chosen: list[str]) -> str:
    source = original
    for action in ACTION_ORDER[case]:
        if action in chosen:
            source = apply_edits(source, edits[action])
    return source


def loader_variant(original: str, chosen: list[str]) -> str:
    line = ("    df = pd.read_excel(filepath" + ("" if "L1" in chosen else ", skiprows=2")
            + ("" if "L2" in chosen else ", names=['responses']") + ").reset_index(drop=True)\n")
    source = replace_once(original, LOADER_LINE, line)
    if "L3" in chosen:
        source = replace_once(source, L3_LINE, "")
    return source


def build_configurations(case: str) -> dict[str, dict]:
    """Every configuration of Appendix A for one case: source text, actions and route file."""
    original = archive_text(case, "run_buggy.py")
    fixed = archive_text(case, "run_fixed.py")
    repairs = pr.REPAIRS / case
    configs: dict[str, dict] = {"original": {"source": original, "actions": [], "route_file": f"archive {case}/run_buggy.py"}}
    if case == "79343179":
        for size in (1, 2, 3):
            for chosen in itertools.combinations(["L1", "L2", "L3"], size):
                configs["".join(chosen)] = {"source": loader_variant(original, list(chosen)), "actions": list(chosen), "route_file": None}
        configs["baseline"] = {"source": (repairs / "run_buggy.py").read_text(encoding="utf-8"), "actions": ["L1", "L2", "L3", "DV"],
                               "route_file": "artifacts/repairs/79343179/run_buggy.py"}
        configs["published"] = {"source": fixed, "actions": ["L1", "L2"], "route_file": f"archive {case}/run_fixed.py"}
        return configs
    edits = _case_actions(case, original)
    if case == "76906469":
        for name, chosen in (("A", ["A"]), ("B", ["B"]), ("AB", ["A", "B"])):
            configs[name] = {"source": compose(original, edits, case, chosen), "actions": chosen, "route_file": None}
    elif case == "78366661":
        configs["baseline"] = {"source": (repairs / "run_buggy.py").read_text(encoding="utf-8"), "actions": ["R"],
                               "route_file": "artifacts/repairs/78366661/run_buggy.py"}
        for name, chosen in (("N", ["N"]), ("N+P1", ["N", "P1"]), ("N+P2", ["N", "P2"])):
            configs[name] = {"source": compose(original, edits, case, chosen), "actions": chosen, "route_file": None}
        configs["published"] = {"source": fixed, "actions": ["N", "P1", "P2"], "route_file": f"archive {case}/run_fixed.py"}
    elif case == "77178370":
        configs["audit_E1"] = {"source": compose(original, edits, case, ["E1"]), "actions": ["E1"], "route_file": None}
        configs["P_core"] = {"source": compose(original, edits, case, ["P_core"]), "actions": ["P_core"], "route_file": None}
        configs["published"] = {"source": fixed, "actions": ["P_core", "P_sys"], "route_file": f"archive {case}/run_fixed.py"}
    elif case == "77099194":
        for name, action in (("attempt_1", "W1"), ("attempt_2", "W2")):
            configs[name] = {"source": (repairs / f"{name}.py").read_text(encoding="utf-8"), "actions": [action],
                             "route_file": f"artifacts/repairs/77099194/{name}.py"}
        configs["published"] = {"source": fixed, "actions": ["K"], "route_file": f"archive {case}/run_fixed.py"}
    elif case == "78383658":
        configs["U1"] = {"source": compose(original, edits, case, ["U1"]), "actions": ["U1"], "route_file": None}
        configs["U2"] = {"source": compose(original, edits, case, ["U2"]), "actions": ["U2"], "route_file": None}
        configs["published"] = {"source": fixed, "actions": ["U2", "U1"], "route_file": f"archive {case}/run_fixed.py"}
    return configs


def comparisons() -> list[dict]:
    """Plan Appendix A.6. Each row compares C (without) and C+m (with)."""
    rows = []

    def add(case, change, context, without, with_, declared="admissible_candidate"):
        rows.append({"comparison_id": f"{case}:{change}|{'+'.join(context) or 'empty'}", "case": case, "change": change,
                     "context": context, "without": without, "with": with_, "declared_class": declared})

    add("76906469", "A", [], "original", "A")
    add("76906469", "B", ["A"], "A", "AB")
    add("76906469", "A", ["B"], "B", "AB", "diagnostic")
    add("76906469", "B", [], "original", "B", "diagnostic")
    names = ["L1", "L2", "L3"]
    for change in names:
        others = [n for n in names if n != change]
        for size in (0, 1, 2):
            for context in itertools.combinations(others, size):
                without = "".join(context) or "original"
                with_ = "".join(sorted(list(context) + [change]))
                add("79343179", change, list(context), without, with_)
    add("79343179", "DV", ["L1", "L2", "L3"], "L1L2L3", "baseline", "admissible_candidate_neutrality")
    add("78366661", "N", [], "original", "N", "admissible_candidate_neutrality")
    add("78366661", "P1", ["N"], "N", "N+P1")
    add("78366661", "P1", ["N", "P2"], "N+P2", "published")
    add("78366661", "P2", ["N"], "N", "N+P2")
    add("78366661", "P2", ["N", "P1"], "N+P1", "published")
    add("77178370", "E1", [], "original", "audit_E1")
    add("77178370", "P_core", [], "original", "P_core")
    add("77178370", "P_sys", ["P_core"], "P_core", "published")
    add("77099194", "K", [], "original", "published")
    add("77099194", "W1", [], "original", "attempt_1")
    add("77099194", "W2", [], "original", "attempt_2")
    add("78383658", "U1", [], "original", "U1")
    add("78383658", "U1", ["U2"], "U2", "published")
    add("78383658", "U2", [], "original", "U2")
    add("78383658", "U2", ["U1"], "U1", "published")
    return rows


ALTERNATIVE_ROUTES = [("78366661", "baseline", "published"), ("79343179", "baseline", "published"),
                      ("77178370", "audit_E1", "published"), ("77099194", "attempt_2", "published")]

# ---------------------------------------------------------------- AST checks


def _without_main(tree: ast.Module) -> list[ast.stmt]:
    return [s for s in tree.body if not (isinstance(s, ast.If) and isinstance(s.test, ast.Compare)
                                         and getattr(s.test.left, "id", "") == "__name__")]


def statements(source: str, scope: str = "module") -> list[str]:
    """Statement dumps: module level and the run_agent body, or the loader function."""
    tree = ast.parse(source)
    if scope == "loader":
        fn = next(s for s in tree.body if isinstance(s, ast.FunctionDef) and s.name == "load_excel_response")
        return [ast.dump(s) for s in fn.body]
    out = []
    for node in _without_main(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run_agent":
            out.append("ARGS " + ast.dump(node.args))
            out.extend(ast.dump(s) for s in node.body)
        else:
            out.append(ast.dump(node))
    return out


def same_ast(a: str, b: str, scope: str = "module") -> bool:
    return statements(a, scope) == statements(b, scope)


def footprint(a: str, b: str, scope: str = "module") -> dict:
    sa, sb = statements(a, scope), statements(b, scope)
    ca, cb = Counter(sa), Counter(sb)
    removed, added = sum((ca - cb).values()), sum((cb - ca).values())
    common_a = [s for s in sa if s in cb]
    common_b = [s for s in sb if s in ca]
    return {"removed": removed, "added": added, "order_changed": common_a != common_b}


def read_excel_keywords(source: str) -> set[str]:
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "read_excel":
            return {k.arg for k in node.keywords}
    return set()


def undefined_names(source: str) -> list[str]:
    tree = ast.parse(source)
    defined = set(dir(builtins)) | {"__file__", "__name__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            defined.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.arg):
            defined.add(node.arg)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                defined.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            defined.add(node.name)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    return sorted(used - defined)


def imported_modules(source: str) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def coherence(config: dict) -> dict:
    missing = undefined_names(config["source"])
    unmet = sorted({need for action in config["actions"] for need in PRECONDITIONS.get(action, []) if need not in config["actions"]})
    label = "coherent" if not missing and not unmet else "incompatible_fragment"
    return {"label": label, "undefined_names": missing, "unmet_preconditions": unmet}


def decomposition_checks(case: str, configs: dict) -> dict:
    """Reconstruction of each route file and the footprint of every comparison."""
    original = configs["original"]["source"]
    result = {"reconstruction": [], "comparisons": {}}
    if case == "79343179":
        published = configs["published"]["source"]
        baseline = configs["baseline"]["source"]
        rebuilt = apply_edits(configs["L1L2L3"]["source"], DV_EDITS)
        result["reconstruction"] = [
            {"route": "published", "rebuilt_from": ["L1", "L2"], "scope": "loader",
             "equal": same_ast(configs["L1L2"]["source"], published, "loader")},
            {"route": "baseline", "rebuilt_from": ["L1", "L2", "L3", "DV"], "scope": "loader",
             "equal": same_ast(rebuilt, baseline, "loader")},
        ]
    elif case in ("78366661", "77178370", "77099194", "78383658"):
        edits = _case_actions(case, original)
        full = configs["published"]["actions"]
        rebuilt = compose(original, edits, case, full)
        result["reconstruction"] = [{"route": "published", "rebuilt_from": full, "scope": "module",
                                     "equal": same_ast(rebuilt, configs["published"]["source"])}]
    else:
        result["reconstruction"] = [{"route": "AB", "rebuilt_from": ["A", "B"], "scope": "module", "equal": True,
                                     "note": "AB is defined by the two historical edits"}]
    for row in [r for r in comparisons() if r["case"] == case]:
        scope = "loader" if case == "79343179" else "module"
        a, b = configs[row["without"]]["source"], configs[row["with"]]["source"]
        fp = footprint(a, b, scope)
        declared = FOOTPRINT[row["change"]]
        ok = declared is None or (fp["removed"], fp["added"]) == declared
        if fp["order_changed"] and row["change"] not in REORDERS:
            ok = False
        if row["change"] in KEYWORD:
            ok = ok and (read_excel_keywords(a) - read_excel_keywords(b)) == {KEYWORD[row["change"]]} \
                and not (read_excel_keywords(b) - read_excel_keywords(a))
        result["comparisons"][row["comparison_id"]] = {**fp, "declared": declared, "isolated": ok}
    return result


# ---------------------------------------------------------------- checks and qualification


def frozen_entries() -> list[dict]:
    return json.loads(ORACLE.read_text(encoding="utf-8"))


def case_inputs(case: str) -> list[dict]:
    if case == "76906469":
        return [{"input_id": "conversation", "role": "public_reproducer", "mode": "agent", "turns": TURNS, "text": TURNS[-1],
                 "checks": ["turn2_france"], "timeout": 180}]
    if case == "79343179":
        return [{"input_id": "loader", "role": "public_reproducer", "mode": "loader", "text": "excel_file.xlsx",
                 "checks": ["loader_table", "loader_sentiment", "loader_location"], "timeout": 60}]
    if case == "78366661":
        return [{"input_id": "pdf", "role": "public_reproducer", "mode": "agent", "text": PDF_URL, "checks": ["nonempty_result"],
                 "timeout": 240}]
    if case == "77178370":
        return [{"input_id": i, "role": role, "mode": "agent", "text": q, "checks": [i], "timeout": 180} for i, role, q, _, _ in BUILDINGS]
    _, questions = MOVIES[case]
    return [{"input_id": i, "role": role, "mode": "agent", "text": q, "checks": [i], "timeout": 180} for i, role, q, _ in questions]


def _notes(case: str) -> list[str]:
    tree = ast.parse(archive_text(case, "run_buggy.py"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "docs":
            return [elt.value for elt in node.value.elts]
    return []


def _excel_values() -> dict:
    import pandas as pd
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "excel_file.xlsx"
        with zipfile.ZipFile(pr.ARCHIVE) as archive:
            path.write_bytes(archive.read("AgentDefect/79343179/excel_file.xlsx"))
        frame = pd.read_excel(path)
    return {"columns": [str(c) for c in frame.columns], "rows": int(len(frame)),
            "Sentiment": ["" if v != v else str(v) for v in frame["Sentiment"]],
            "Location": ["" if v != v else str(v) for v in frame["Location"]]}


def contract(case: str) -> list[dict]:
    """Every check of the case with its frozen source, required flag and the Q1 and Q4 results."""
    entries = {e["archive_folder"]: e for e in frozen_entries()}
    entry = entries.get(case)
    frozen_inputs = entry["inputs"] if entry else []
    oracle_version = sha256_file(ORACLE)
    rows = []

    def frozen_for(role, text_prefix):
        for item in frozen_inputs:
            if item["role"] == role and (text_prefix is None or item["text"].startswith(text_prefix)):
                return item
        return None

    def add(check_id, input_id, role, required, rule, frozen, q4, expected, scope="full_program", note="", q1_source=None):
        q1 = bool(frozen) and frozen.get("review_status") == "accepted" and str(frozen.get("frozen")) == "True"
        if q1_source:
            q1 = True
        rows.append({
            "check_id": check_id, "case": case, "input_id": input_id,
            "category": {"public_reproducer": "original", "related": "related", "descriptive": "descriptive"}[role],
            "source_of_requirement": frozen.get("source") if frozen else ("archive test.py line 14" if case == "76906469" else None),
            "input": frozen.get("text") if frozen else None, "expected": expected, "rule": rule,
            "validity_status": frozen.get("review_status") if frozen else "no_frozen_entry",
            "required_for_adequacy": required, "execution_scope": scope, "oracle_version": oracle_version,
            "q1_frozen_accepted": q1 if role != "descriptive" else None, "q1_source": q1_source or ("frozen_oracles_v2.json" if frozen else None),
            "q4_expected_matches_assets": q4, "note": note,
        })

    if case == "76906469":
        add("turn2_france", "conversation", "public_reproducer", True, "turn 2 answer lowercased contains 'france', limited_endpoint",
            None, None, "france", note="limited_endpoint; no entry in frozen_oracles.json",
            q1_source="archive AgentDefect/76906469/test.py line 14, the published test; Jun \"Accept the published test\" (2026-10-22)")
    elif case == "79343179":
        excel = _excel_values()
        f_pub = frozen_for("public_reproducer", None)
        add("loader_table", "loader", "public_reproducer", True, "columns in order and 4 rows", f_pub,
            excel["columns"] == LOADER_COLUMNS and excel["rows"] == 4, {"columns": LOADER_COLUMNS, "rows": 4}, "loader_only")
        f_s = frozen_for("related", "Read excel_file.xlsx and report the Sentiment")
        add("loader_sentiment", "loader", "related", True, "Sentiment values in row order", f_s,
            bool(f_s) and f_s.get("expected") == excel["Sentiment"], f_s.get("expected") if f_s else None, "loader_only")
        f_l = frozen_for("related", "Read excel_file.xlsx and report the Location")
        add("loader_location", "loader", "related", True, "Location values in row order", f_l,
            bool(f_l) and f_l.get("expected") == excel["Location"], f_l.get("expected") if f_l else None, "loader_only")
    elif case == "78366661":
        add("nonempty_result", "pdf", "public_reproducer", True, "returned list longer than zero", frozen_for("public_reproducer", None),
            None, None, "reproduction_only",
            "a nonempty passage list establishes the reproduction endpoint only; passage relevance is not established")
    elif case == "77178370":
        notes = _notes(case)
        for input_id, role, question, required, forbidden in BUILDINGS:
            frozen = frozen_for(role, question)
            recomputed = sorted(n for n in notes if n.split()[-1].lower() in required)
            q4 = bool(frozen) and sorted(frozen.get("expected") or []) == recomputed
            add(input_id, input_id, role, True, f"_score_buildings required {required} forbidden {forbidden}", frozen, q4,
                recomputed, note="frozen expected " + json.dumps(frozen.get("expected") if frozen else None))
    else:
        filename, questions = MOVIES[case]
        rows_csv = pr._rows(case, filename)
        for input_id, role, question, token in questions:
            frozen = frozen_for(role, question)
            recomputed = pr._genre_titles(rows_csv, token)
            stored = [e["title"] if isinstance(e, dict) else e for e in (frozen.get("expected") or [])] if frozen else []
            add(input_id, input_id, role, True, f"_score_titles against _genre_titles of {filename} token {token}", frozen,
                sorted(stored) == recomputed, recomputed)
        if case == "78383658":
            add("public_overview_fragments", "family", "descriptive", False, "_public_movie_score overview fragments", None, None, None,
                note="descriptive, never part of adequacy")
    return rows


def score(case: str, check_id: str, payload: dict) -> dict:
    """Score one completed run on one check."""
    results = payload.get("results") or []
    text = results[-1]["text"] if results else ""
    if check_id == "turn2_france":
        answer = results[1]["text"] if len(results) > 1 else ""
        return {"passed": "france" in answer.lower(), "answer": answer[:500]}
    if check_id.startswith("loader_"):
        loader = payload.get("loader") or {}
        if check_id == "loader_table":
            return {"passed": loader.get("columns") == LOADER_COLUMNS and loader.get("rows") == 4,
                    "columns": loader.get("columns"), "rows": loader.get("rows")}
        key = "sentiment" if check_id == "loader_sentiment" else "location"
        expected = ["Neutral", "Positive", "Positive", "Positive"] if key == "sentiment" else ["London", "UK", "Vagabonds", ""]
        return {"passed": loader.get(key) == expected, "values": loader.get(key)}
    if check_id == "nonempty_result":
        count = results[-1].get("count") if results else None
        if count is None:
            count = 0 if not text else 1
        return {"passed": count > 0, "count": count}
    if case == "77178370":
        _, _, _, required, forbidden = next(b for b in BUILDINGS if b[0] == check_id)
        return {**pr._score_buildings(text, required, forbidden), "answer": text[:500]}
    if check_id == "public_overview_fragments":
        return {"overview_fragments": pr._public_movie_score("78383658", text).get("overview_fragments")}
    filename, questions = MOVIES[case]
    token = next(q[3] for q in questions if q[0] == check_id)
    rows = pr._rows(case, filename)
    catalog = sorted({row["title"] for row in rows})
    return {**score_titles_v2(text, pr._genre_titles(rows, token), catalog), "answer": text[:500], "scorer": SCORER_VERSION}


# Title scorer v2 (Jun "Versioned fix, rescore", 2026-10-22). v1 is pilot_run._score_titles, unchanged.
TYPOGRAPHY = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " ",
              **{c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"}}
SCORER_VERSION = "titles_v2"


def normalize_text(text: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKC", text).translate(str.maketrans(TYPOGRAPHY))


def score_titles_v2(answer: str, expected: list[str], catalog: list[str]) -> dict:
    """pilot_run._score_titles after typographic normalization of answer and titles."""
    low = normalize_text(answer).lower()
    missing = [title for title in expected if normalize_text(title).lower() not in low]
    added = [title for title in catalog if normalize_text(title).lower() in low and title not in expected]
    return {"missing": missing, "added": added, "passed": not missing and not added}


# ---------------------------------------------------------------- classification

INFRA = ("APIConnectionError", "RateLimitError", "InternalServerError", "APITimeoutError")
NETWORK = ("ConnectionError", "URLError", "gaierror", "ConnectTimeout", "ReadTimeout", "HTTPError", "Timeout")


def classify(raw: dict, events: list[dict], config: dict, original: str) -> tuple[str, str | None]:
    """Run status and failure stage, from the child's own report and its trace."""
    if raw.get("timeout"):
        return "unresolved_timeout", None
    info = raw.get("result")
    if info is None:
        return "evaluator_failure", "no_child_result_line"
    if info.get("loaded_sha256") and info["loaded_sha256"] != sha256_text(config["source"]):
        return "application_failure", "loaded_source_differs"
    if raw.get("returncode") == 0 and info.get("ok"):
        return "completed", None
    phase = info.get("mp_failed_phase") or "unknown"
    if phase == "prelude":
        return "instrumentation_failure", "prelude"
    exception_seq = next((e["seq"] for e in reversed(events) if e["kind"] == "exception"), None)
    if any(e["kind"] == "probe_error" and (exception_seq is None or e["seq"] < exception_seq) for e in events):
        return "instrumentation_failure", "probe_error"
    if phase in ("flatten", "emit"):
        return "evaluator_failure", phase
    mro = info.get("error_mro") or []
    if "ImportError" in mro:
        missing = (info.get("missing_module") or "").split(".")[0]
        added = {m.split(".")[0] for m in imported_modules(config["source"])} - {m.split(".")[0] for m in imported_modules(original)}
        if missing and missing in added:
            return "interface_runtime_failure", "candidate_import"
        return "environment_blocked", f"missing_module:{missing}"
    if "OpenAIError" in mro and any(name in mro for name in INFRA):
        return "infrastructure_failure", "model_api"
    if "OpenAIError" not in mro and any(name in mro for name in NETWORK):
        return "environment_blocked", "network"
    return "interface_runtime_failure", info.get("last_boundary") or phase


# ---------------------------------------------------------------- manifest


def manifest_paths() -> dict:
    return {"manifest": OUT / "experiment_manifest.json", "selftest": OUT / "selftest.json", "runs": OUT / "runs.jsonl"}


def schedule(configs_by_case: dict) -> list[dict]:
    """Jun's order: 76906469 probed, then unprobed, existing routes, then the remaining configurations."""
    cells = []

    def add(case, config, probe=True):
        for item in case_inputs(case):
            for rep in range(1, REPETITIONS + 1):
                cells.append({"case": case, "configuration": config, "input_id": item["input_id"], "repetition": rep, "probe": probe})

    for config in ("original", "A", "B", "AB"):
        add("76906469", config)
    for config in ("original", "AB"):
        add("76906469", config, probe=False)
    routes = {"79343179": ["original", "baseline", "published"], "78366661": ["original", "baseline", "published"],
              "77178370": ["original", "audit_E1", "published"], "77099194": ["original", "attempt_1", "attempt_2", "published"],
              "78383658": ["original", "published"]}
    for case in CASE_ORDER[1:]:
        for config in routes[case]:
            add(case, config)
    for case in CASE_ORDER[1:]:
        for config in configs_by_case[case]:
            if config not in routes[case]:
                add(case, config)
    return cells


def estimated_cost() -> dict:
    chat_in, chat_out, embed_tokens = 81_621, 6_465, 550_000
    return {"chat_input_tokens": chat_in, "chat_output_tokens": chat_out, "embedding_tokens": embed_tokens,
            "chat_dollars": round(chat_in * pr.PRICE_IN + chat_out * pr.PRICE_OUT, 4),
            "embedding_dollars": round(embed_tokens * EMBED_PRICE, 4),
            "basis": "per-run tokens of pilot_results.json and the cb39baa smoke record; PDF and CSV sizes measured 2026-10-22; "
                     "prices are the pilot constants and an assumed ada-002 price, unverified"}


def cmd_manifest() -> int:
    configs_by_case, report = {}, {}
    hypotheses = []
    for case in CASE_ORDER:
        configs = build_configurations(case)
        configs_by_case[case] = configs
        checks = decomposition_checks(case, configs)
        case_dir = OUT / "cases" / case
        coh = {name: coherence(cfg) for name, cfg in configs.items()}
        write_json(case_dir / "configurations.json", [
            {"configuration_id": name, "changes": cfg["actions"],
             "component_set": sorted({c for a in cfg["actions"] if a not in NON_BEHAVIOURAL for c in COMPONENTS[case].get(a, [])}),
             "coherence": coh[name], "coherence_rationale": "parses, every used name defined, declared preconditions met"
             if coh[name]["label"] == "coherent" else "declared precondition or name missing",
             "interface_preconditions": {a: PRECONDITIONS.get(a, []) for a in cfg["actions"]},
             "checks": [c for item in case_inputs(case) for c in item["checks"]],
             "execution_scope": "loader_only" if case == "79343179" else "full_program", "repetitions": REPETITIONS,
             "route_file": cfg["route_file"], "source_sha256": sha256_text(cfg["source"]), "source_text": cfg["source"]}
            for name, cfg in configs.items()])
        write_json(case_dir / "components.json", [
            {"component_id": comp, "responsibility": comp.replace("_", " "), "anchors": anchor,
             "input_output_contract": "as read from the archive source at the anchor",
             "observable_boundaries": PROBE[case]["order"]} for comp, anchor in ANCHORS[case].items()])
        write_json(case_dir / "actions.json", [
            {"change_id": action, "behavioural": action not in NON_BEHAVIOURAL, "component_ids": comps,
             "provenance": _provenance(case, action), "preconditions": PRECONDITIONS.get(action, []),
             "coupled_changes": [], "symbols": SYMBOLS.get(action, []), "declared_footprint": FOOTPRINT.get(action),
             "base_identity": sha256_text(configs["original"]["source"])}
            for action, comps in COMPONENTS[case].items()])
        write_json(case_dir / "contract.json", contract(case))
        write_json(case_dir / "probe_spec.json", {name: {**PROBE[case].get(name, PROBE[case]["default"]), "order": PROBE[case]["order"]}
                                                  for name in configs})
        write_json(case_dir / "decomposition.json", checks)
        report[case] = {"configurations": len(configs), "coherence": {n: c["label"] for n, c in coh.items()},
                        "reconstruction": [r["equal"] for r in checks["reconstruction"]],
                        "isolated": all(v["isolated"] for v in checks["comparisons"].values())}
    for row in comparisons():
        key = (row["case"], "B_diag") if row["declared_class"] == "diagnostic" else (row["case"], row["change"])
        endpoint, change, stay, contradiction, prior = HYPOTHESES[key]
        hypotheses.append({"comparison_id": row["comparison_id"], "endpoint_prediction": endpoint, "should_change": change,
                           "should_stay": stay, "contradicting_observation": contradiction, "prior_exposure": prior, "exploratory": True})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hypotheses.jsonl").write_text("".join(json.dumps(h) + "\n" for h in hypotheses), encoding="utf-8")
    cells = schedule(configs_by_case)
    config = load_config(ROOT / "configs" / "study.yaml")
    write_json(OUT / "experiment_manifest.json", {
        "experiment_id": EXP_ID, "written": datetime.now(timezone.utc).isoformat(),
        "effective_settings_expected": EXPECTED_SETTINGS,
        "settings_in_study_yaml": {k: config.get(k) for k in EXPECTED_SETTINGS},
        "retries": "none; max_retries=0 on every chat model and embedding client",
        "schedule": cells, "scheduled_executions": len(cells),
        "model_enabled_episodes": sum(1 for c in cells if c["case"] != "79343179"),
        "loader_episodes": sum(1 for c in cells if c["case"] == "79343179"),
        "configurations": sum(len(c) for c in configs_by_case.values()), "comparisons": len(comparisons()),
        "hypotheses": len(hypotheses), "estimated_cost": estimated_cost(), "checks": report,
    })
    print(json.dumps({"configurations": sum(len(c) for c in configs_by_case.values()), "scheduled_executions": len(cells),
                      "hypotheses": len(hypotheses), "cases": report}, indent=2))
    return 0


PROVENANCE = {
    "A": "historical_repair", "B": "historical_repair",
    "L1": "published_fix and baseline_attempt_1", "L2": "published_fix and baseline_attempt_1",
    "L3": "baseline_attempt_1", "DV": "baseline_attempt_1",
    "N": "published_fix", "P1": "published_fix", "P2": "published_fix", "R": "baseline_attempt_1",
    "E1": "evaluator_audit", "P_core": "published_fix", "P_sys": "published_fix",
    "K": "published_fix", "W1": "baseline_attempt_1", "W2": "baseline_attempt_2",
    "U1": "published_fix", "U2": "published_fix",
}


def _provenance(case: str, action: str) -> str:
    return PROVENANCE[action]


# ---------------------------------------------------------------- selftest

SELFTEST_BODIES = {
    "chat_request": r'''
import httpx
def handler(request):
    return httpx.Response(200, json={"id": "x", "object": "chat.completion", "created": 0, "model": "gpt-6-luna",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}})
llm = StudyChat(api_key="sk-test", http_client=httpx.Client(transport=httpx.MockTransport(handler)))
assert llm.max_retries == 0, llm.max_retries
llm.invoke("hello")
''',
    "network_attempt": r'''
import httpx, json as _json
calls = []
def failing(request):
    calls.append(1)
    return httpx.Response(500, json={"error": {"message": "boom", "type": "server_error"}})
bad = StudyChat(api_key="sk-test", http_client=httpx.Client(transport=httpx.MockTransport(failing)))
try:
    bad.invoke("hello")
except Exception as exc:
    print("expected failure", type(exc).__name__)
print(_json.dumps({"failing_calls": len(calls)}))
''',
    "memory": r'''
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory.load_memory_variables({})
memory.save_context({"input": "a"}, {"output": "b"})
''',
    "retrieval": r'''
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
FAISS.from_texts(["alpha", "beta"], FakeEmbeddings(size=8)).as_retriever().invoke("alpha")
''',
    "direct_search": r'''
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FakeEmbeddings
Chroma.from_texts(["alpha", "beta"], FakeEmbeddings(size=8)).similarity_search("alpha", k=1)
''',
    "embeddings": r'''
import httpx, json as _json
def handler(request):
    body = _json.loads(request.content)
    data = [{"object": "embedding", "index": i, "embedding": [0.0, 1.0]} for i, _ in enumerate(body["input"])]
    return httpx.Response(200, json={"object": "list", "data": data, "model": "text-embedding-ada-002",
                                     "usage": {"prompt_tokens": 1, "total_tokens": 1}})
from langchain_openai import OpenAIEmbeddings as NewEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings as OldEmbeddings
new = NewEmbeddings(api_key="sk-test", http_client=httpx.Client(transport=httpx.MockTransport(handler)), check_embedding_ctx_length=False)
assert new.max_retries == 0, new.max_retries
new.embed_documents(["x"]); new.embed_query("y")
import openai
old = OldEmbeddings(openai_api_key="sk-test", http_client=httpx.Client(transport=httpx.MockTransport(handler)),
                    async_client=openai.AsyncOpenAI(api_key="sk-test").embeddings)
assert old.max_retries == 0, old.max_retries
old.embed_documents(["x"]); old.embed_query("y")
''',
    "parsers": r'''
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
StrOutputParser().invoke("x"); StrOutputParser().parse("x")
structured = StructuredOutputParser.from_response_schemas([ResponseSchema(name="results", description="d")])
structured.invoke('```json\n{"results": "1"}\n```'); structured.parse('```json\n{"results": "1"}\n```')
''',
    "agent_parsers": r'''
from langchain.agents.chat.output_parser import ChatOutputParser
from langchain.agents.conversational_chat.output_parser import ConvoOutputParser
ChatOutputParser().parse("Thought: t\nFinal Answer: y")
ConvoOutputParser().parse('```json\n{"action": "Final Answer", "action_input": "y"}\n```')
''',
    "tools": r'''
from langchain_core.tools import Tool
Tool(name="echo_tool", func=lambda x: x, description="echo").run("q")
''',
}

SELFTEST_EXPECT = {
    "chat_request": [("StudyChat", "_get_request_payload", "request_prepared")],
    "network_attempt": [("httpx.Client", "send", "backend_attempt")],
    "memory": [("ConversationBufferMemory", "load_memory_variables", "memory_before"),
               ("ConversationBufferMemory", "save_context", "memory_after")],
    "retrieval": [("VectorStoreRetriever", "_get_relevant_documents", "retrieval")],
    "direct_search": [("Chroma", "similarity_search", "retrieval")],
    "embeddings": [(c, m, "embedding") for c in ("langchain_openai", "langchain_community") for m in ("embed_documents", "embed_query")],
    "parsers": [(c, m, "parser") for c in ("StrOutputParser", "StructuredOutputParser") for m in ("invoke", "parse")],
    "agent_parsers": [("ChatOutputParser", "parse", "parser"), ("ConvoOutputParser", "parse", "parser")],
    "tools": [("callback_handler", "on_tool_start", "tool_call"), ("callback_handler", "on_tool_end", "tool_call")],
    "loader": [("load_excel_response", "func", "loader_output")],
}


def _pair_seen(boundary: str, cls: str, method: str, kind: str, events: list[dict]) -> bool:
    for e in events:
        if e["kind"] != kind or e.get("boundary") != boundary:
            continue
        if kind == "embedding":
            if cls in (e.get("cls") or "") and e.get("method") == method:
                return True
        elif kind == "parser":
            if e.get("cls") == cls and e.get("method") == method:
                return True
        elif kind == "tool_call":
            if e.get("stage") == ("start" if method == "on_tool_start" else "end"):
                return True
        else:
            return True
    return False


def selftest_boundary(boundary: str, work: Path) -> dict:
    """Run one boundary's offline child and check that every class and method pair produced its event."""
    env = {**os.environ, "OPENAI_API_KEY": "sk-test", "ANONYMIZED_TELEMETRY": "False"}
    trace = work / f"{boundary}.jsonl"
    if boundary == "loader":
        original = archive_text("79343179", "run_buggy.py")
        raw = pr._run_module("79343179", "loader", "excel_file.xlsx", original, 60, trace_path=trace, boundaries=["loader"])
        returncode, stdout, stderr = raw["returncode"], raw["stdout"], raw["stderr"]
    else:
        script = pr._study_prelude() + instrument.NO_RETRY_PRELUDE + instrument.trace_prelude(trace, [boundary]) + SELFTEST_BODIES[boundary]
        proc = subprocess.run([sys.executable, "-c", script], cwd=work, env=env, capture_output=True, text=True, timeout=300)
        returncode, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    events = instrument.read_trace(trace)
    pairs = [{"cls": c, "method": m, "event": k, "seen": _pair_seen(boundary, c, m, k, events)} for c, m, k in SELFTEST_EXPECT[boundary]]
    extra = {}
    if boundary == "network_attempt":
        extra = instrument.last_json(stdout) or {}
        attempts = sum(1 for e in events if e["kind"] == "backend_attempt")
        extra["backend_attempt_events"] = attempts
        extra["single_attempt"] = extra.get("failing_calls") == 1 and attempts == 1
    ok = (returncode == 0 and all(p["seen"] for p in pairs) and not any(e["kind"] == "probe_unresolved" for e in events)
          and not any(e["kind"] == "probe_error" for e in events) and extra.get("single_attempt", True))
    return {"boundary": boundary, "ok": ok, "returncode": returncode, "pairs": pairs, **extra,
            "event_counts": dict(Counter(e["kind"] for e in events)),
            "installed": [f"{e['cls']}.{e['method']} from {e['resolved_from']}" for e in events if e["kind"] == "probe_installed"],
            "unresolved": [e for e in events if e["kind"] in ("probe_unresolved", "probe_error")],
            "stderr_tail": stderr[-600:] if not ok else ""}


def cmd_selftest() -> int:
    work = Path(tempfile.mkdtemp(prefix="ext-selftest-"))
    try:
        results = [selftest_boundary(boundary, work) for boundary in SELFTEST_EXPECT]
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)
    ok_all = all(r["ok"] for r in results)
    write_json(OUT / "selftest.json", {"ok": ok_all, "written": datetime.now(timezone.utc).isoformat(),
                                       "probe_version": sha256_file(Path(instrument.__file__)), "boundaries": results})
    for r in results:
        print(f"{r['boundary']:16s} ok={r['ok']} pairs={sum(p['seen'] for p in r['pairs'])}/{len(r['pairs'])}")
    return 0 if ok_all else 1


# ---------------------------------------------------------------- map


def cmd_map() -> int:
    instruction = OUT / "instruction_2026-10-22.md"
    if not instruction.exists():
        print(f"missing {instruction}; it is written once from the session transcript")
        return 1
    git = lambda *args: subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True).stdout.strip()
    files = {}
    for folder in ("src", "configs", "artifacts/repairs"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                files[str(path.relative_to(ROOT))] = sha256_file(path)
    reused = {}
    for name in ("_extract", "_study_prelude", "_flatten", "_run_module", "_score_titles", "_genre_titles", "_score_buildings",
                 "_public_movie_score", "_rows", "_titles", "_audit_building_source"):
        lines, start = inspect.getsourcelines(getattr(pr, name))
        reused[name] = f"pilot_run.py lines {start} to {start + len(lines) - 1}"
    write_json(OUT / "implementation_map.json", {
        "git_root": git("rev-parse", "--show-toplevel"), "head": git("rev-parse", "HEAD"),
        "dirty_entries": len(git("status", "--porcelain").splitlines()),
        "motivation_pilot_tracked": bool(git("ls-files", "motivation_pilot")),
        "archive": str(pr.ARCHIVE), "archive_sha256": sha256_file(pr.ARCHIVE),
        "interpreter": sys.executable, "files_sha256": files, "reused_functions": reused,
        "instruction_sha256": sha256_file(instruction),
        "entrypoint": "PYTHONPATH=src python -m motivation_pilot.extension <subcommand>",
    })
    with (ROOT / "artifacts" / "inventory.csv").open(newline="", encoding="utf-8") as handle:
        inventory = list(csv.DictReader(handle))
    (OUT / "inventory.jsonl").write_text("".join(json.dumps(row) + "\n" for row in inventory), encoding="utf-8")
    pilot = json.loads((ROOT / "artifacts" / "pilot_results.json").read_text(encoding="utf-8"))
    reasons = {row["case_id"]: row["reason"] for row in pilot["not_repaired"]}
    rows = []
    for case in CASE_ORDER + CONTROLS:
        row = {"case": case, "runs_in_extension": case in CASE_ORDER,
               "scope": "loader_only" if case == "79343179" else "full_program",
               "leaked_variants": LEAKED.get(case, {})}
        if case in reasons:
            row["status"] = "failure_not_reproduced"
            row["recorded_reason"] = reasons[case]
        elif case == "76906469":
            row["status"] = "historical_qualification"
        else:
            row["status"] = "qualified_in_pilot"
        rows.append(row)
    (OUT / "qualification.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    print(f"implementation_map.json, inventory.jsonl ({len(inventory)} rows), qualification.jsonl ({len(rows)} rows)")
    return 0


# ---------------------------------------------------------------- live


def _pip_freeze_hash() -> str:
    out = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout
    return sha256_text(out)


def _case_state(case: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        pr._extract(case, Path(tmp))
        return instrument.tree_sha256(Path(tmp))


def fingerprint_parts(cell: dict, config: dict, original: str, item: dict, shared: dict) -> dict:
    return {
        "configuration_sha256": sha256_text(config["source"]), "actions": config["actions"],
        "program_base_sha256": sha256_text(original), "initial_state": shared["case_state"][cell["case"]],
        "input": item.get("turns") or item["text"], "scope": "loader_only" if cell["case"] == "79343179" else "full_program",
        "model_settings": EXPECTED_SETTINGS, "dependencies": shared["pip_freeze"], "probe_version": shared["probe_version"],
        "oracle_version": shared["oracle_version"], "protocol": EXP_ID, "probe": cell["probe"], "repetition": cell["repetition"],
    }


def run_id(cell: dict) -> str:
    return f"{cell['case']}-{safe_id(cell['configuration'])}-{cell['input_id']}-r{cell['repetition']}-{'p' if cell['probe'] else 'u'}"


def execute(cell: dict, config: dict, original: str, item: dict, spec: dict, parts: dict) -> dict:
    rid = run_id(cell)
    trace = OUT / "traces" / f"{rid}.jsonl"
    trace.parent.mkdir(parents=True, exist_ok=True)
    if trace.exists():
        trace.unlink()
    wanted = spec["expected"] + spec["optional"] + spec["removed"]
    started = datetime.now(timezone.utc).isoformat()
    raw = pr._run_module(cell["case"], item["mode"], item["text"], config["source"], item["timeout"],
                         trace_path=trace if cell["probe"] else None, turns=item.get("turns"), probe=cell["probe"],
                         boundaries=wanted if cell["probe"] else None)
    events = instrument.read_trace(trace)
    status, stage = classify(raw, events, config, original)
    info = raw.get("result") or {}
    checks, descriptive = {}, {}
    contracts = {c["check_id"]: c for c in contract_cache(cell["case"])}
    if status == "completed":
        passed_all = True
        for check_id in item["checks"]:
            try:
                checks[check_id] = score(cell["case"], check_id, info)
            except Exception as exc:
                checks[check_id] = {"passed": None, "scorer_error": f"{type(exc).__name__}: {exc}"}
            passed_all = passed_all and bool(checks[check_id].get("passed"))
        for check_id, row in contracts.items():
            if row["category"] == "descriptive" and row["input_id"] == item["input_id"]:
                descriptive[check_id] = score(cell["case"], check_id, info)
        status = "completed_pass" if passed_all else "behavioral_failure"
    elif status == "interface_runtime_failure":
        checks = {check_id: {"passed": False, "interface_failure": True} for check_id in item["checks"]}
    derived = instrument.derive(events) if cell["probe"] else {}
    attempts = derived.get("backend_attempts", 0)
    model_input = (derived.get("request_messages") or [None])[0] if cell["probe"] else None
    if cell["case"] == "79343179":
        reason = "no_model_call_in_loader_scope"
    elif cell["probe"] and attempts == 0:
        reason = f"no_model_call_before_{stage}" if status not in COMPLETED[:2] else "no_model_call_observed"
    else:
        reason = None
    return {
        "run_id": rid, **cell, "actions": config["actions"], "scope": parts["scope"], "fingerprint": sha256_text(json.dumps(parts, sort_keys=True)),
        "fingerprint_parts": parts, "started_at": started, "elapsed": raw.get("elapsed"), "returncode": raw.get("returncode"),
        "timeout": raw.get("timeout"), "status": status, "failure_stage": stage,
        "error_type": info.get("error_type"), "error_message": (info.get("error_message") or "")[:1000],
        "missing_module": info.get("missing_module"), "loaded_sha256": info.get("loaded_sha256"),
        "initial_state_observed": raw.get("initial_state"), "checks": checks, "descriptive": descriptive,
        "answers": [r.get("text", "")[:2000] for r in info.get("results") or []], "loader": info.get("loader"),
        "tokens": {"prompt": info.get("prompt"), "completion": info.get("completion")}, "chat_requests": info.get("chat_requests"),
        "derived": {k: derived.get(k) for k in ("requests_prepared", "backend_attempts", "chat_attempts", "embedding_attempts",
                                                "failed_attempts")} if cell["probe"] else None,
        "embedding_characters": sum(e.get("characters") or 0 for e in derived.get("embeddings", [])) if cell["probe"] else None,
        "model_input": model_input, "model_input_reason": reason,
        "boundary_states": instrument.boundary_states(events, {**spec, "order": spec["order"]}) if cell["probe"] else None,
        "trace": str(trace.relative_to(OUT)) if cell["probe"] else None,
        "stdout_tail": raw.get("stdout", "")[-2000:], "stderr_tail": raw.get("stderr", "")[-4000:],
    }


_CONTRACTS: dict[str, list[dict]] = {}


def contract_cache(case: str) -> list[dict]:
    if case not in _CONTRACTS:
        path = OUT / "cases" / case / "contract.json"
        _CONTRACTS[case] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else contract(case)
    return _CONTRACTS[case]


def neutrality(runs: list[dict]) -> dict:
    out = {}
    for config in ("original", "AB"):
        sides = {}
        for probe in (True, False):
            rows = [r for r in runs if r["case"] == "76906469" and r["configuration"] == config and r["probe"] == probe]
            sides["probed" if probe else "unprobed"] = {
                "passes": sum(1 for r in rows if r["status"] == "completed_pass"),
                "model_requests": sum(r.get("chat_requests") or 0 for r in rows), "runs": len(rows)}
        sides["same"] = (sides["probed"]["passes"] == sides["unprobed"]["passes"]
                         and sides["probed"]["model_requests"] == sides["unprobed"]["model_requests"])
        out[config] = sides
    return out


def plan_cells(cells: list[dict], runs: list[dict], prepare) -> list[tuple]:
    """Resume rule: skip a cell whose recorded fingerprint matches, flag one whose fingerprint differs."""
    done = {(r["case"], r["configuration"], r["input_id"], r["repetition"], r["probe"]): r for r in runs}
    planned = []
    for cell in cells:
        item, cfg, parts = prepare(cell)
        key = (cell["case"], cell["configuration"], cell["input_id"], cell["repetition"], cell["probe"])
        if key in done and done[key]["fingerprint"] != sha256_text(json.dumps(parts, sort_keys=True)):
            planned.append(("mismatch", cell))
        else:
            planned.append(("skip" if key in done else "run", cell, item, cfg, parts))
    return planned


def cmd_live() -> int:
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; export it first.")
        return 6
    paths = manifest_paths()
    if not paths["manifest"].exists():
        print("experiment_manifest.json is missing; run map and manifest first.")
        return 7
    selftest = json.loads(paths["selftest"].read_text(encoding="utf-8")) if paths["selftest"].exists() else {"ok": False}
    if not selftest.get("ok") or selftest.get("probe_version") != sha256_file(Path(instrument.__file__)):
        print("selftest.json is missing, failing, or older than instrument.py; run selftest.")
        return 5
    config = load_config(ROOT / "configs" / "study.yaml")
    if any(config.get(k) != v for k, v in EXPECTED_SETTINGS.items()):
        print("configs/study.yaml differs from the prelude settings:", {k: config.get(k) for k in EXPECTED_SETTINGS})
        return 2
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    cells = manifest["schedule"]
    configs_by_case = {case: build_configurations(case) for case in CASE_ORDER}
    originals = {case: configs_by_case[case]["original"]["source"] for case in CASE_ORDER}
    shared = {"pip_freeze": _pip_freeze_hash(), "probe_version": sha256_file(Path(instrument.__file__)),
              "oracle_version": sha256_file(ORACLE),
              "case_state": {case: _case_state(case) for case in CASE_ORDER}}
    def prepare(cell):
        item = next(i for i in case_inputs(cell["case"]) if i["input_id"] == cell["input_id"])
        cfg = configs_by_case[cell["case"]][cell["configuration"]]
        return item, cfg, fingerprint_parts(cell, cfg, originals[cell["case"]], item, shared)

    planned = plan_cells(cells, read_jsonl(paths["runs"]), prepare)
    mismatches = [p[1] for p in planned if p[0] == "mismatch"]
    if mismatches:
        print("fingerprint differs from the recorded run for:", [run_id(c) for c in mismatches])
        return 4
    neutral_checked = False
    for entry in planned:
        cell = entry[1]
        if not neutral_checked and cell["case"] != "76906469":
            result = neutrality(read_jsonl(paths["runs"]))
            write_json(OUT / "probe_neutrality.json", result)
            neutral_checked = True
            if not all(v["same"] for v in result.values()):
                print("probe neutrality check failed:", json.dumps(result))
                return 3
        if entry[0] == "skip":
            continue
        if len(read_jsonl(paths["runs"])) >= manifest["scheduled_executions"]:
            print("execution limit reached")
            break
        _, cell, item, cfg, parts = entry
        spec = {**PROBE[cell["case"]].get(cell["configuration"], PROBE[cell["case"]]["default"]), "order": PROBE[cell["case"]]["order"]}
        record = execute(cell, cfg, originals[cell["case"]], item, spec, parts)
        with paths["runs"].open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {record['run_id']} {record['status']} {record.get('failure_stage') or ''}", flush=True)
    cmd_compare()
    cmd_report()
    return 0


# ---------------------------------------------------------------- compare


def outcome(runs: list[dict], case: str, config: str, check_id: str) -> dict:
    """pass, fail, unstable or unresolved over the three probed repetitions."""
    inputs = {i["input_id"] for i in case_inputs(case) if check_id in i["checks"]}
    rows = [r for r in runs if r["case"] == case and r["configuration"] == config and r["probe"] and r["input_id"] in inputs]
    by_rep = {r["repetition"]: r for r in rows}
    observed = [by_rep.get(rep) for rep in range(1, REPETITIONS + 1)]
    if any(r is None or r["status"] not in COMPLETED for r in observed):
        label = "unresolved"
    else:
        passes = sum(1 for r in observed if (r["checks"].get(check_id) or {}).get("passed"))
        label = "pass" if passes == REPETITIONS else "fail" if passes == 0 else "unstable"
    return {"label": label, "passes": sum(1 for r in rows if (r.get("checks", {}).get(check_id) or {}).get("passed")),
            "statuses": [r["status"] if r else "missing" for r in observed]}


def qualification(case: str, runs: list[dict]) -> dict:
    out = {}
    for row in contract_cache(case):
        if row["category"] == "descriptive":
            continue
        check_id = row["check_id"]
        scorer_errors = [r["run_id"] for r in runs if r["case"] == case and (r.get("checks", {}).get(check_id) or {}).get("scorer_error")]
        q1, q2 = bool(row["q1_frozen_accepted"]), not scorer_errors
        q4 = row["q4_expected_matches_assets"] is not False
        original = outcome(runs, case, "original", check_id)
        if not (q1 and q2 and q4):
            status = "oracle_invalid"
        elif row["category"] == "original" and original["label"] == "pass":
            status = "not_reproducing"
        elif row["category"] == "original" and original["label"] in ("unstable", "unresolved"):
            status = "unresolved"
        else:
            status = "qualified"
        out[check_id] = {"status": status, "q1": q1, "q2": q2, "q3_original": original["label"], "q4": row["q4_expected_matches_assets"]}
    return out


def adequacy(runs: list[dict], case: str, config: str, quals: dict) -> dict:
    labels = {check_id: outcome(runs, case, config, check_id)["label"] for check_id in quals}
    if all(quals[c]["status"] == "qualified" and labels[c] == "pass" for c in quals):
        value = "adequate"
    elif any(quals[c]["status"] == "qualified" and labels[c] == "fail" for c in quals):
        value = "inadequate"
    else:
        value = "unresolved"
    return {"adequacy": value, "checks": labels}


def _runtime_incoherent(runs: list[dict], case: str, config: str, removed: str) -> bool:
    patterns = SYMBOLS.get(removed, []) + ([VIOLATION_PATTERNS[removed]] if removed in VIOLATION_PATTERNS else [])
    for r in runs:
        if r["case"] == case and r["configuration"] == config and r["probe"] and r["status"] == "interface_runtime_failure":
            if any(p in (r.get("error_message") or "") for p in patterns):
                return True
    return False


def load_runs(directory: Path) -> list[dict]:
    """runs.jsonl as recorded, with checks and status read through rescored_checks.jsonl when it exists."""
    runs = read_jsonl(directory / "runs.jsonl")
    rescored = {row["run_id"]: row for row in read_jsonl(directory / "rescored_checks.jsonl")}
    for r in runs:
        row = rescored.get(r["run_id"])
        if row:
            r["checks_v1"], r["status_v1"] = r.get("checks"), r["status"]
            r["checks"], r["status"], r["scorer"] = row["checks"], row["status"], row["scorer"]
    return runs


def rescore_runs(directory: Path) -> dict:
    """Re-score every title check from the full final answer in the trace, without a model call."""
    rows, changed, flipped = [], 0, 0
    for r in read_jsonl(directory / "runs.jsonl"):
        if r["case"] not in MOVIES or not r.get("trace") or r["status"] not in ("completed_pass", "behavioral_failure"):
            continue
        finals = [e for e in instrument.read_trace(directory / r["trace"]) if e["kind"] == "final"]
        answer = finals[-1].get("answer") or "" if finals else ""
        filename, questions = MOVIES[r["case"]]
        token = next(q[3] for q in questions if q[0] == r["input_id"])
        csv_rows = pr._rows(r["case"], filename)
        check = {**score_titles_v2(answer, pr._genre_titles(csv_rows, token), sorted({row["title"] for row in csv_rows})),
                 "answer": answer[:500], "scorer": SCORER_VERSION}
        old = r["checks"].get(r["input_id"]) or {}
        checks = {**r["checks"], r["input_id"]: check}
        status = "completed_pass" if all((c or {}).get("passed") for c in checks.values()) else "behavioral_failure"
        changed += (old.get("missing"), old.get("added"), old.get("passed")) != (check["missing"], check["added"], check["passed"])
        flipped += status != r["status"]
        rows.append({"run_id": r["run_id"], "scorer": SCORER_VERSION, "checks": checks, "status": status,
                     "status_v1": r["status"], "rescored_at": datetime.now(timezone.utc).isoformat()})
    (directory / "rescored_checks.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return {"experiment": directory.name, "rescored": len(rows), "check_results_changed": changed, "statuses_changed": flipped}


def cmd_rescore() -> int:
    summary = [rescore_runs(directory) for directory in (OUT, R_DIR) if (directory / "runs.jsonl").exists()]
    log_path = ROOT / "artifacts" / "oracle_corrections.json"
    log = [entry for entry in json.loads(log_path.read_text(encoding="utf-8")) if entry.get("version") != SCORER_VERSION]
    log.append({
        "version": SCORER_VERSION, "date": date.today().isoformat(), "object": "title scorer of 77099194 and 78383658",
        "change": "NFKC normalization, curly quotes to straight quotes and Unicode hyphens to '-' in answer and titles before matching; "
                  "pilot_run._score_titles stays as v1",
        "reason": "answers wrote At World\u2019s End with a curly apostrophe, which the v1 substring match scored as missing",
        "decided_by": "Jun, answer \"Versioned fix, rescore\" (2026-10-22)",
        "after_outcomes": "yes; found on exp-2026-10-22-r answers after the live run",
        "applied_to": summary,
    })
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def admissibility(comp: dict, coh: dict, decomposition_entry: dict, quals: dict, side_runs: list[dict],
                  runtime_incoherent: bool) -> tuple[str, list[str]]:
    """Plan correction 1: matched conditions, intended source, declared difference only, qualified checks, coherent sides."""
    reasons = []
    for side in ("without", "with"):
        if coh[comp[side]] != "coherent":
            reasons.append(f"{side}_incompatible_fragment")
    if not decomposition_entry["isolated"]:
        reasons.append("not_isolated")
    if any(q["status"] != "qualified" for q in quals.values()):
        reasons.append("unqualified_required_check")
    if any(r["status"] == "application_failure" for r in side_runs):
        reasons.append("intended_source_not_loaded")
    parts = {}
    for r in side_runs:
        common = {k: v for k, v in r["fingerprint_parts"].items() if k not in ("configuration_sha256", "actions")}
        parts.setdefault((r["input_id"], r["repetition"]), set()).add(json.dumps(common, sort_keys=True))
    if any(len(v) > 1 for v in parts.values()):
        reasons.append("conditions_not_matched")
    if runtime_incoherent:
        reasons.append("runtime_incoherent")
    if not reasons:
        return "admissible", []
    fragment = any(r.endswith("incompatible_fragment") for r in reasons) or "runtime_incoherent" in reasons
    return ("interface_dependency_diagnostic" if fragment else "inadmissible_" + "+".join(reasons)), reasons


def contribution_verdict(parent: str, reduced: str) -> str:
    """Only after admissibility: parent adequacy first, then required, removable or unresolved."""
    if parent != "adequate":
        return "not_assessed_parent_not_adequate"
    if reduced == "inadequate":
        return "required_in_context"
    if reduced == "adequate":
        return "removable_in_context"
    return "unresolved_in_context"


def cmd_compare() -> int:
    runs = load_runs(OUT)
    rows, verdicts, decisions = [], {}, []
    for case in CASE_ORDER:
        configs = build_configurations(case)
        quals = qualification(case, runs)
        coh = {n: coherence(c)["label"] for n, c in configs.items()}
        decomposition = json.loads((OUT / "cases" / case / "decomposition.json").read_text(encoding="utf-8"))
        adeq = {n: adequacy(runs, case, n, quals) for n in configs}
        for comp in [c for c in comparisons() if c["case"] == case]:
            side_runs = [r for r in runs if r["case"] == case and r["probe"] and r["configuration"] in (comp["without"], comp["with"])]
            klass, reasons = admissibility(comp, coh, decomposition["comparisons"][comp["comparison_id"]], quals, side_runs,
                                           _runtime_incoherent(runs, case, comp["without"], comp["change"]))
            verdict = contribution_verdict(adeq[comp["with"]]["adequacy"], adeq[comp["without"]]["adequacy"]) if klass == "admissible" else None
            row = {**comp, "class": klass, "reasons": reasons, "verdict": verdict,
                   "without_adequacy": adeq[comp["without"]], "with_adequacy": adeq[comp["with"]],
                   "run_ids": sorted(r["run_id"] for r in side_runs), "footprint": decomposition["comparisons"][comp["comparison_id"]],
                   "mechanism": _mechanism(runs, case, comp)}
            rows.append(row)
            if verdict:
                verdicts.setdefault((case, comp["change"]), []).append(verdict)
        decisions.append(_decision(case, configs, coh, adeq, quals, rows))
    with (OUT / "comparisons.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, default=str) + "\n")
    with (OUT / "contribution_verdicts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["case", "change", "admissible_comparisons", "required", "removable", "unresolved", "parent_not_adequate",
                         "useful_observed", "conditionally_necessary_observed", "redundant_within_evaluated_contexts"])
        for case in CASE_ORDER:
            for change in COMPONENTS[case]:
                v = verdicts.get((case, change), [])
                if not v and not any(r["case"] == case and r["change"] == change for r in rows):
                    continue
                c = Counter(v)
                assessed = c["required_in_context"] + c["removable_in_context"] + c["unresolved_in_context"]
                writer.writerow([case, change, len(v), c["required_in_context"], c["removable_in_context"], c["unresolved_in_context"],
                                 c["not_assessed_parent_not_adequate"], c["required_in_context"] > 0,
                                 c["required_in_context"] > 0 and c["removable_in_context"] > 0,
                                 assessed > 0 and c["removable_in_context"] == assessed])
    (OUT / "decisions.jsonl").write_text("".join(json.dumps(d, default=str) + "\n" for d in decisions), encoding="utf-8")
    print(f"comparisons {len(rows)}, decisions {len(decisions)}")
    return 0


NOT_OBSERVATIONS = ("probe_installed", "probe_unresolved", "probe_error")


def observed_boundary_states(run: dict, events: list[dict]) -> dict:
    """Boundary states recomputed from the trace. The `boundary_states` field written during the live run
    counted `probe_installed` events as observations; only events of an executed boundary count."""
    spec = {**PROBE[run["case"]].get(run["configuration"], PROBE[run["case"]]["default"]), "order": PROBE[run["case"]]["order"]}
    return instrument.boundary_states([e for e in events if e["kind"] not in NOT_OBSERVATIONS], spec)


def _mechanism(runs: list[dict], case: str, comp: dict) -> dict:
    """Intermediate fields per side, read from repetition 1 of each input."""
    out = {}
    for side in ("without", "with"):
        for r in runs:
            if r["case"] == case and r["configuration"] == comp[side] and r["probe"] and r["repetition"] == 1:
                events = instrument.read_trace(OUT / r["trace"]) if r.get("trace") else []
                d = instrument.derive(events)
                out.setdefault(side, {})[r["input_id"]] = {
                    "status": r["status"], "backend_attempts": d["backend_attempts"],
                    "memory_types": [m["types"] for m in d["memory_before"]],
                    "retrieved_counts": [len(x.get("documents") or []) for x in d["retrieved"]],
                    "tool_calls": [t.get("name") for t in d["tool_calls"] if t.get("stage") == "start"],
                    "parser_classes": sorted({p["cls"] for p in d["parser_io"]}),
                    "embedding_texts": sum(e.get("count") or 0 for e in d["embeddings"]),
                    "loader": d["loader_output"] and {k: d["loader_output"].get(k) for k in ("columns", "rows")},
                    "boundary_states": observed_boundary_states(r, events),
                }
    return out


def _decision(case: str, configs: dict, coh: dict, adeq: dict, quals: dict, rows: list[dict]) -> dict:
    initial, basis = INITIAL[case]
    leaked = LEAKED.get(case, {})

    def scope(name):
        # Every declared action counts, N and DV included (Jun "Count them", 2026-10-22).
        actions = configs[name]["actions"]
        modules = sorted({c for a in actions for c in COMPONENTS[case].get(a, [])})
        return len(modules), len(actions), modules

    candidates = [n for n in configs if n != "original" and n not in leaked and coh[n] == "coherent"]
    adequate = [n for n in candidates if adeq[n]["adequacy"] == "adequate"]
    unresolved = [n for n in candidates if adeq[n]["adequacy"] == "unresolved"]
    if not adequate:
        retained, kind = None, "no_adequate_candidate"
    else:
        best = min(scope(n)[:2] for n in adequate)
        tied = sorted(n for n in adequate if scope(n)[:2] == best)
        if len(tied) == 1:
            retained, kind = tied[0], "retained"
        elif initial in tied:
            retained, kind = initial, "retained_initial_among_tied"
        else:
            retained, kind = None, "unresolved_choice"
    before = scope(initial) if initial else (None, None, [])
    after = scope(retained) if retained else (None, None, [])
    wording = None
    if retained and initial and after[0] == before[0] and (after[1] or 0) < (before[1] or 0):
        wording = "smaller action set, same module scope"
    return {
        "case": case, "initial_candidate": initial, "selection_basis": basis,
        "comparison_ids": [r["comparison_id"] for r in rows if r["case"] == case],
        "decision": kind, "retained_candidate": retained,
        "tied_candidates": tied if adequate and kind == "unresolved_choice" else [],
        "unresolved_candidates": unresolved,
        "adequacy_before": adeq[initial]["adequacy"] if initial else None,
        "adequacy_after": adeq[retained]["adequacy"] if retained else None,
        "modules_before": before[0], "modules_after": after[0], "actions_before": before[1], "actions_after": after[1],
        "module_names_after": after[2], "wording": wording,
        "claim_limit": "concerns the evaluated configurations and frozen checks of this case only",
        "qualification": quals,
    }


# ---------------------------------------------------------------- report


class Registry:
    def __init__(self):
        self.rows = []

    def add(self, name, value, what, source, how):
        self.rows.append((f"ext_{name}", value, what, source, how, date.today().isoformat()))
        return str(value)

    def write(self):
        text = NUMBERS.read_text(encoding="utf-8") if NUMBERS.exists() else "# Number registry — motivation_pilot\n"
        start, end = "<!-- ext:start -->", "<!-- ext:end -->"
        block = [start, "", "| name | value | what it counts | source file | how it is computed | date read |", "|---|---|---|---|---|---|"]
        block += ["| " + " | ".join(str(x) for x in row) + " |" for row in self.rows]
        block += ["", end]
        if start in text and end in text:
            head, rest = text.split(start, 1)
            text = head + "\n".join(block) + rest.split(end, 1)[1]
        else:
            text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
        NUMBERS.write_text(text, encoding="utf-8")


ORIGIN = {"original": "published buggy program", "published": "published fix, privileged reference", "baseline": "baseline repair",
          "attempt_1": "baseline attempt 1", "attempt_2": "baseline attempt 2, locked", "audit_E1": "evaluator audit"}


def _historical_table() -> list[tuple[str, int, int]]:
    rows = [json.loads(line) for line in git_show("repair_family_pilot/artifacts/donor_tables/runs.jsonl").splitlines() if line.strip()]
    out = []
    for arm in ("empty", "A", "B", "AB"):
        mine = [r for r in rows if r["repair_set"] == arm]
        out.append((arm, len(mine), sum(1 for r in mine if r["outcome"] == "success")))
    return out


def _route_table(runs, case, configs, checks, reg, src):
    head = "| configuration | origin | " + " | ".join(checks) + " | adequacy |"
    lines = [head, "|" + "---|" * (len(checks) + 3)]
    quals = qualification(case, runs)
    for name in configs:
        cells = []
        for check in checks:
            o = outcome(runs, case, name, check)
            cells.append(f"{o['label']} {o['passes']}/{REPETITIONS}")
        a = adequacy(runs, case, name, quals)["adequacy"]
        lines.append(f"| {name} | {ORIGIN.get(name, 'constructed from declared actions')} | " + " | ".join(cells) + f" | {a} |")
    return lines


MINIMALITY_ROUTES = {"79343179": ["L1L2L3", "baseline"], "78366661": ["N+P1", "published"]}


def _minimality(case, configs, adeq) -> list[str]:
    """Inclusion minimality over the proper subsets of each route's declared actions, N and DV included."""
    out = []
    by_actions = {frozenset(cfg["actions"]): name for name, cfg in configs.items()}
    for route in MINIMALITY_ROUTES.get(case, []):
        actions = set(configs[route]["actions"])
        if adeq.get(route) != "adequate":
            out.append(f"{route} is not adequate, so no minimality statement applies.")
            continue
        evaluated, missing = [], []
        for size in range(len(actions)):
            for chosen in itertools.combinations(sorted(actions), size):
                name = by_actions.get(frozenset(chosen))
                if name is None:
                    missing.append(" and ".join(chosen) + " without " + " and ".join(sorted(actions - set(chosen))))
                else:
                    evaluated.append((name, adeq.get(name)))
        smaller = [n for n, a in evaluated if a == "adequate"]
        if smaller:
            out.append(f"{route} is not inclusion minimal, because the evaluated reduction {', '.join(smaller)} is adequate.")
        elif not missing and all(a == "inadequate" for _, a in evaluated):
            out.append(f"{route} is inclusion minimal in the evaluated domain. Every coherent proper subset was run and is inadequate.")
        else:
            out.append(f"{route} has no successful evaluated reduction. {', '.join(missing)} was not run, so its minimality is unresolved.")
    return out


R_DIR = ROOT / "artifacts" / "agentdefect_extension" / "exp-2026-10-22-r"
E_DIR = ROOT / "artifacts" / "agentdefect_extension" / "exp-2026-10-23-e"
V_DIR = ROOT / "artifacts" / "agentdefect_extension" / "exp-2026-10-23-v"
EMBED_PRICE_3_SMALL = 0.02 / 1_000_000  # text-embedding-3-small, assumed and unverified (plan revision 4)


def _scorer_limitation() -> str:
    words = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    say = lambda n: words[n] if n <= 10 else str(n)
    log = json.loads((ROOT / "artifacts" / "oracle_corrections.json").read_text(encoding="utf-8"))
    entry = next((e for e in log if e.get("version") == SCORER_VERSION), None)
    if entry is None:
        return ""
    parts = [f"{say(a['check_results_changed'])} check results in {a['experiment']}, "
             + ("none of which changed a run status" if a["statuses_changed"] == 0 else f"{say(a['statuses_changed'])} of which changed a run status")
             for a in entry["applied_to"]]
    return ("Title checks of 77099194 and 78383658 use scorer v2, a correction made after outcomes were seen and logged in "
            "oracle_corrections.json. It changed " + ", and ".join(parts) + ".")


def _retrieval_section(reg: "Registry") -> list[str]:
    """Section 7, the 78383658 retrieval intervention, from the exp-2026-10-22-r records."""
    runs = load_runs(R_DIR)
    decision_path = R_DIR / "decision.json"
    if not runs or not decision_path.exists():
        return []
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    manifest = json.loads((R_DIR / "experiment_manifest.json").read_text(encoding="utf-8"))
    comps = read_jsonl(R_DIR / "comparisons.jsonl")
    src = "artifacts/agentdefect_extension/exp-2026-10-22-r"
    lines = ["## 7. Retrieval intervention for 78383658, exp-2026-10-22-r", "",
             "R makes the retriever return every indexed document, with the count read from the index. It is an evaluator-designed "
             "development intervention motivated by the traces of section 4, not a discovered repair. All four configurations ran fresh, "
             f"{reg.add('r_runs', len(runs), 'runs recorded in exp-2026-10-22-r', f'{src}/runs.jsonl', 'line count')} runs against "
             f"{reg.add('r_scheduled', manifest['scheduled_executions'], 'scheduled executions of exp-2026-10-22-r', f'{src}/experiment_manifest.json', 'schedule length')} "
             f"scheduled, with no retry. The index held {reg.add('r_index', manifest['index_size'], 'chunks indexed by 78383658', f'{src}/experiment_manifest.json', 'CSVLoader and CharacterTextSplitter in memory')} chunks.", "",
             "| configuration | family | action | adventure | adequacy |", "|---|---|---|---|---|"]
    for name in manifest["configurations"]:
        cells = []
        for check in ("family", "action", "adventure"):
            o = outcome(runs, "78383658", name, check)
            cells.append(f"{o['label']} {o['passes']}/{REPETITIONS}")
        lines.append(f"| {name} | " + " | ".join(cells) + f" | {decision['adequacy'][name]} |")
    covered, total = decision["r_runs_with_coverage"], decision["r_runs"]
    lines += ["", f"Coverage was verified in {reg.add('r_covered', covered, 'R runs whose retrieval held every indexed chunk and whose final model request held every catalog title', f'{src}/decision.json', 'coverage rule')} "
              f"of {reg.add('r_runs_r', total, 'runs of the two R configurations', f'{src}/decision.json', 'R runs with a trace')} R runs.", "",
              "| comparison | without | with | class | verdict |", "|---|---|---|---|---|"]
    for row in comps:
        lines.append(f"| {row['comparison_id']} | {row['without']} {row['without_adequacy']['adequacy']} | {row['with']} {row['with_adequacy']['adequacy']} | "
                     f"{row['class']} | {row['verdict'] or 'none'} |")
    tokens_in = sum((r.get("tokens") or {}).get("prompt") or 0 for r in runs)
    tokens_out = sum((r.get("tokens") or {}).get("completion") or 0 for r in runs)
    lines += ["", "| outcome | value |", "|---|---|",
              f"| supported decision, from Jun's table | {decision['supported_decision']} |",
              f"| selected configuration | {decision['selected'] or 'none'} |", "",
              f"Chat use was {reg.add('r_tokens_in', tokens_in, 'chat input tokens in exp-2026-10-22-r', f'{src}/runs.jsonl', 'sum of tokens.prompt')} input and "
              f"{reg.add('r_tokens_out', tokens_out, 'chat output tokens in exp-2026-10-22-r', f'{src}/runs.jsonl', 'sum of tokens.completion')} output tokens.", ""]
    return lines


def _environment_section(reg: "Registry") -> list[str]:
    """Section 8, the environment flip experiment, from the exp-2026-10-23-e records."""
    summary_path = E_DIR / "summary.json"
    runs = load_runs(E_DIR)
    if not runs or not summary_path.exists():
        return []
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest = json.loads((E_DIR / "experiment_manifest.json").read_text(encoding="utf-8"))
    flips = read_jsonl(E_DIR / "flips.jsonl")
    src = "artifacts/agentdefect_extension/exp-2026-10-23-e"
    per_env = Counter(r["environment"] for r in runs)
    lines = ["## 8. Environment flip experiment, exp-2026-10-23-e", "",
             "One environment input changed per case. Every configuration of the matched comparisons ran fresh under the recorded "
             f"condition E0 and under the changed condition E1, {reg.add('e_runs', len(runs), 'runs recorded in exp-2026-10-23-e', f'{src}/runs.jsonl', 'line count')} runs against "
             f"{reg.add('e_scheduled', manifest['scheduled_executions'], 'scheduled executions of exp-2026-10-23-e', f'{src}/experiment_manifest.json', 'schedule length')} scheduled, "
             f"{reg.add('e_runs_e0', per_env.get('E0', 0), 'E0 runs recorded in exp-2026-10-23-e', f'{src}/runs.jsonl', 'environment field')} under E0 and "
             f"{reg.add('e_runs_e1', per_env.get('E1', 0), 'E1 runs recorded in exp-2026-10-23-e', f'{src}/runs.jsonl', 'environment field')} under E1, with no retry. "
             "A comparison flips when its verdict under E1 differs from its verdict under E0.", "",
             "| case | E1 change | retained under E0 | retained under E1 | E1 state | flipped comparisons |", "|---|---|---|---|---|---|"]
    show = lambda value: "none" if value is None else value
    reg.add("e_pandas_e1", "2.2.3", "pandas version of the 79343179 E1 interpreter", "/data/wang/junh/envs/harnessfix-pandas2", "pandas.__version__")
    reg.add("e_pandas_e0", "3.0.6", "pandas version of the harnessfix interpreter", "/data/wang/junh/envs/harnessfix", "pandas.__version__")
    catalog = manifest.get("catalog_check", {})
    reg.add("e_catalog_rows_e1", catalog.get("rows"), "rows of the 78383658 E1 catalog control_96.csv", f"{src}/experiment_manifest.json", "catalog_check.rows")
    reg.add("e_catalog_rows_e0", catalog.get("rows", 0) - catalog.get("added_rows", 0), "rows of the archive control.csv", f"{src}/experiment_manifest.json", "rows minus added_rows")
    for case, s in summary["cases"].items():
        state = "unresolved, endpoint error" if s.get("environment_unresolved") else "observed"
        lines.append(f"| {case} | {s['change']} | {show(s['retained']['E0'])} | {show(s['retained']['E1'])} | {state} | {len(s['flips'])} |")
    unresolved_flips = summary.get("flipped_in_unresolved_environment", 0)
    observed_comparisons = sum(1 for f in flips if not summary["cases"][f["case"]].get("environment_unresolved"))
    reg.add("e_comparisons_observed", observed_comparisons, "comparisons in cases whose E1 condition was observed", f"{src}/flips.jsonl",
            "rows whose case is not environment_unresolved")
    lines += ["", f"Flipped comparisons numbered {reg.add('e_flips', summary['flipped_comparisons'], 'comparisons whose verdict differs between E0 and E1', f'{src}/flips.jsonl', 'flipped true')} "
              f"of {reg.add('e_comparisons', summary['comparisons_per_environment'], 'comparisons evaluated in each environment', f'{src}/flips.jsonl', 'line count')}. "
              + (f"Of these, {reg.add('e_flips_unresolved', unresolved_flips, 'flipped comparisons in a case whose E1 endpoint returned an error', f'{src}/flips.jsonl', 'flipped and environment_unresolved')} "
                 "sit in a case whose E1 endpoint returned an error for every request, so that environment is unresolved and the difference is not an observation of the program."
                 if unresolved_flips else ""), ""]
    for case, s in summary["cases"].items():
        lines += [f"### {case}, {s['change']}", "", "| configuration | adequacy under E0 | adequacy under E1 |", "|---|---|---|"]
        for name in s["configurations"]:
            a0, a1 = s["adequacy"]["E0"][name], s["adequacy"]["E1"][name]
            fmt = lambda a: a["adequacy"] + " (" + ", ".join(f"{k} {v}" for k, v in a["checks"].items()) + ")"
            lines.append(f"| {name} | {fmt(a0)} | {fmt(a1)} |")
        lines += ["", "| comparison | verdict under E0 | verdict under E1 | flipped |", "|---|---|---|---|"]
        for f in [f for f in flips if f["case"] == case]:
            lines.append(f"| {f['comparison_id']} | {f['verdict_E0'] or f['class_E0']} | {f['verdict_E1'] or f['class_E1']} | {'yes' if f['flipped'] else 'no'} |")
        if s.get("first_e1_error"):
            e = s["first_e1_error"]
            n = len(s["not_completed"]["E1"])
            count = reg.add(f"e_{case}_e1_not_completed", n, f"E1 runs of {case} that did not complete", f"{src}/runs.jsonl", "status outside the completed set") if n >= 10 else str(n)
            code = re.search(r"Error code: (\d+)", e.get("error_message") or "")
            if code:
                reg.add(f"e_{case}_e1_http_status", code.group(1), f"HTTP status of the first E1 endpoint error of {case}", f"{src}/runs.jsonl", "error_message")
            lines += ["", f"E1 runs not completed, {count}. First, {e['status']} {e.get('error_type') or ''} {(e.get('error_message') or '')[:300]}".rstrip() + "."]
        lines.append("")
    lines += ["| case | predicted outcome | observed |", "|---|---|---|"]
    for p in summary["predictions"]:
        lines.append(f"| {p['case']} | {p['outcome']} | {summary['cases'][p['case']]['observed']} |")
    tokens_in = sum((r.get("tokens") or {}).get("prompt") or 0 for r in runs)
    tokens_out = sum((r.get("tokens") or {}).get("completion") or 0 for r in runs)
    chars = sum(r.get("embedding_characters") or 0 for r in runs)
    lines += ["", f"Chat use was {reg.add('e_tokens_in', tokens_in, 'chat input tokens in exp-2026-10-23-e', f'{src}/runs.jsonl', 'sum of tokens.prompt')} input and "
              f"{reg.add('e_tokens_out', tokens_out, 'chat output tokens in exp-2026-10-23-e', f'{src}/runs.jsonl', 'sum of tokens.completion')} output tokens over both environments, "
              f"and embedding calls received {reg.add('e_embed_chars', chars, 'characters sent to embedding calls in exp-2026-10-23-e', f'{src}/runs.jsonl', 'sum of embedding_characters')} characters. "
              "The gpt-4 price is not among the pilot constants, so no dollar figure is given for this experiment.", ""]
    return lines


def _fmt(x, nd=2):
    return "none" if x is None else f"{x:.{nd}f}"


def _interval(iv):
    return "none" if iv is None else f"[{iv[0]:.2f}, {iv[1]:.2f}]".replace("-0.00", "0.00")


_WORDS = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def _count(reg: "Registry", name, value, what, source, how, zero="none") -> str:
    """Register a count and print it the house way, words up to ten and numerals above."""
    reg.add(name, value, what, source, how)
    if isinstance(value, int) and value in _WORDS:
        return zero if value == 0 else _WORDS[value]
    return str(value)


def _interval_reg(reg: "Registry", tag: str, iv, what: str, src: str) -> str:
    if iv is None:
        return "none"
    lo = reg.add(tag + "_lo", f"{iv[0]:.2f}".replace("-0.00", "0.00"), f"lower end of the delta interval, {what}", src, "contrast.delta_interval[0]")
    hi = reg.add(tag + "_hi", f"{iv[1]:.2f}", f"upper end of the delta interval, {what}", src, "contrast.delta_interval[1]")
    return f"[{lo}, {hi}]"


def _reanalysis_section(reg: "Registry") -> list[str]:
    """Section 9, every recorded comparison re-read as an enactment adjusted pass probability contrast, from exp-2026-10-23-v."""
    summary_path = V_DIR / "summary.json"
    if not summary_path.exists():
        return []
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = read_jsonl(V_DIR / "reanalysis.jsonl")
    src = "artifacts/agentdefect_extension/exp-2026-10-23-v/reanalysis.jsonl"
    by = summary["by_verdict"]
    req, rem = by.get("required_in_context", {}), by.get("removable_in_context", {})
    enacted_rows = [r for r in rows if r["enactment"]["state"] == "observed"]
    partial = [r for r in rows if r["enactment"]["rate"] not in (None, 0, 1)]
    never = [r for r in rows if r["enactment"]["state"] == "never_enacted"]
    not_obs = [r for r in rows if r["enactment"]["state"] == "not_observable"]
    three = [r for r in rows if r["recorded_verdict"] == "required_in_context" and r["with"]["n"] == 3]
    lines = ["## 9. Verdicts with enactment rates and intervals, exp-2026-10-23-v", "",
             "Every comparison row of sections 3, 7 and 8 is re-read without a model call. Each side's passes over its runs give a Jeffreys Beta "
             "posterior of the pass probability, the effect is the posterior of the difference Δ between the with side and the without side, "
             "and a with side run counts as enacted when every module the change touches has its boundary event in the run's trace. "
             f"A required verdict survives when P(Δ > 0) is at least {reg.add('v_level', summary['level'], 'posterior probability level of the survival rules', 'artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json', 'level')}, "
             f"a removable verdict when P(abs Δ < {summary['delta']}) is at least {summary['level']}, "
             "and the other verdict values carry no survival label. "
             f"Rows, {reg.add('v_rows', summary['rows'], 'comparison rows reanalysed in exp-2026-10-23-v', src, 'line count')}, "
             f"{reg.add('v_rows_22', summary['by_batch'].get('exp-2026-10-22', 0), 'reanalysed rows from exp-2026-10-22', src, 'batch field')} from section 3, "
             f"{_count(reg, 'v_rows_r', summary['by_batch'].get('exp-2026-10-22-r', 0), 'reanalysed rows from exp-2026-10-22-r', src, 'batch field')} from section 7 and "
             f"{reg.add('v_rows_e', summary['by_batch'].get('exp-2026-10-23-e', 0), 'reanalysed rows from exp-2026-10-23-e', src, 'batch field')} from section 8.", "",
             "| recorded verdict | rows | survives | fails | no label | never enacted | partially enacted | not observable |", "|---|---|---|---|---|---|---|---|"]
    for v, s in by.items():
        key = v.replace("_in_context", "").replace("_parent_not_adequate", "")
        lines.append(f"| {v} | {reg.add(f'v_{key}_rows', s['rows'], f'reanalysed rows with recorded verdict {v}', src, 'recorded_verdict')} | "
                     f"{reg.add(f'v_{key}_survives', s['survives'], f'{v} rows whose survival rule holds', src, 'survives true')} | "
                     f"{reg.add(f'v_{key}_fails', s['fails'], f'{v} rows whose survival rule fails', src, 'survives false')} | {s['no_label']} | "
                     f"{s['never_enacted']} | {s['partially_enacted']} | {s['not_observable']} |")
    lines += ["",
              f"Enactment. {reg.add('v_enacted_rows', len(enacted_rows), 'rows whose with side enactment was observed', src, 'enactment.state observed')} rows have an observed enactment rate, "
              f"{_count(reg, 'v_never', len(never), 'rows whose with side never enacted the change', src, 'enactment.state never_enacted')} rows never enacted the change in any with side run, and "
              f"{reg.add('v_not_observable', len(not_obs), 'rows whose change touches a module with no probe', src, 'enactment.state not_observable')} rows touch a module with no probe, "
              "document splitting, the model client or data loading, so their enactment is not observable. "
              + " ".join(f"`{r['comparison_id']}` in {r['batch']} passed {_count(reg, f'v_partial{i}_k', r['with']['k'], 'with side passes of the partially enacted row', src, 'with.k')} of "
                         f"{_count(reg, f'v_partial{i}_n', r['with']['n'], 'with side runs of the partially enacted row', src, 'with.n')} with side runs while "
                         f"{_count(reg, f'v_partial{i}_e', r['enactment']['enacted'], 'enacted with side runs of the partially enacted row', src, 'enactment.enacted')} of "
                         f"{_count(reg, f'v_partial{i}_r', r['enactment']['runs'], 'with side runs of the partially enacted row', src, 'enactment.runs')} enacted the change." for i, r in enumerate(partial)), "",
              f"Repetition. {reg.add('v_required_three', len(three), 'required rows resting on three with side runs', src, 'required_in_context and with.n 3')} of the "
              f"{reg.add('v_required_rows', req.get('rows', 0), 'required rows', src, 'recorded_verdict')} required rows rest on three runs a side. "
              f"For every one of them Fisher's exact two sided p is {reg.add('v_fisher_three', '0.10', 'Fisher p for three of three against zero of three', 'verdict_stats.fisher_p', 'computed')} and P(Δ > 0) is "
              f"{reg.add('v_ppos_three', '0.996', 'P(delta > 0) for three of three against zero of three', 'verdict_stats.contrast', 'computed')}, so the posterior rule accepts what the exact test does not, and "
              f"{reg.add('v_required_fisher', summary['required_fail_fisher'], 'required rows with Fisher p at or above 0.05', src, 'fisher_p >= 0.05')} required rows have p at or above {reg.add('v_fisher_level', '0.05', 'significance level of the Fisher count', 'report text', 'constant')}. "
              f"Of the {_count(reg, 'v_removable_rows', rem.get('rows', 0), 'removable rows', src, 'recorded_verdict')} removable rows "
              f"{_count(reg, 'v_removable_survives', rem.get('survives', 0), 'removable rows surviving at the margin', src, 'survives true')} survive at the margin, "
              f"since three against three gives {reg.add('v_close_three', '0.72', 'P(abs delta < 0.2) for three of three against three of three', 'verdict_stats.prob_delta_close', 'computed')} and nine against nine "
              f"{reg.add('v_close_nine', '0.95', 'P(abs delta < 0.2) for nine of nine against nine of nine, 0.946', 'verdict_stats.prob_delta_close', 'computed')} for the probability that the two pass rates lie within "
              f"{reg.add('v_margin', summary['delta'], 'equivalence margin of the survival rule', 'artifacts/agentdefect_extension/exp-2026-10-23-v/summary.json', 'delta')}. "
              f"The stricter margin {reg.add('v_margin_strict', '0.1', 'the stricter margin reported beside the rule', 'verdict_stats.DELTAS', 'constant')} is reported beside it.", ""]
    for v in ("required_in_context", "removable_in_context"):
        sub = [r for r in rows if r["recorded_verdict"] == v]
        if not sub:
            continue
        lines += [f"### {v}, rows grouped by their counts", "",
                  "| with k/n | without k/n | enacted | rows | P(Δ > 0) | Δ interval | P(abs Δ < 0.1) | P(abs Δ < 0.2) | PN | Fisher p | survives | comparisons |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        groups = {}
        for r in sub:
            en = r["enactment"]
            enacted = "not observable" if en["state"] == "not_observable" else f"{en['enacted']}/{en['runs']}"
            key = (r["with"]["k"], r["with"]["n"], r["without"]["k"], r["without"]["n"], enacted)
            groups.setdefault(key, []).append(r)
        for gi, (key, members) in enumerate(sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])), start=1):
            r = members[0]
            c = r["contrast"] or {}
            tag = f"v_{v.split('_')[0]}_g{gi}"
            what = f"{v} rows with {key[0]}/{key[1]} against {key[2]}/{key[3]}, enacted {key[4]}"
            close = c.get("p_delta_close") or {}
            names = ", ".join(f"{m['comparison_id']} ({m['batch']})" for m in members)
            lines.append(f"| {reg.add(tag + '_wk', key[0], f'with side passes, {what}', src, 'with.k')}/{reg.add(tag + '_wn', key[1], f'with side runs, {what}', src, 'with.n')} | "
                         f"{reg.add(tag + '_ok', key[2], f'without side passes, {what}', src, 'without.k')}/{reg.add(tag + '_on', key[3], f'without side runs, {what}', src, 'without.n')} | {key[4]} | "
                         f"{reg.add(tag + '_rows', len(members), f'rows in the group, {what}', src, 'count')} | "
                         f"{reg.add(tag + '_ppos', _fmt(c.get('p_delta_positive')), f'P(delta > 0), {what}', src, 'contrast.p_delta_positive')} | "
                         f"{_interval_reg(reg, tag, c.get('delta_interval'), what, src)} | "
                         f"{reg.add(tag + '_c1', _fmt(close.get('0.1')), f'P(abs delta < 0.1), {what}', src, 'contrast.p_delta_close 0.1')} | "
                         f"{reg.add(tag + '_c2', _fmt(close.get('0.2')), f'P(abs delta < 0.2), {what}', src, 'contrast.p_delta_close 0.2')} | "
                         f"{reg.add(tag + '_pn', _fmt(r['pn']), f'PN at the posterior means, {what}', src, 'pn')} | "
                         f"{reg.add(tag + '_fisher', _fmt(r['fisher_p'], 3), f'Fisher exact two sided p, {what}', src, 'fisher_p')} | "
                         f"{'yes' if r['survives'] else 'no'} | {names} |")
        lines.append("")
    lines += ["The rows without a survival label, with their intervals and enactment, are in `exp-2026-10-23-v/reanalysis.jsonl`. "
              "The command is `PYTHONPATH=src python -m motivation_pilot.verdict_reanalysis run`, with `--delta 0.1` for the stricter margin.", ""]
    return lines


def _reanalysis_limitation() -> str:
    if not (V_DIR / "summary.json").exists():
        return ""
    return ("The reanalysis of section 9 reads the recorded runs only. Its posteriors use the Jeffreys prior on each side, which accepts a "
            "three against zero contrast at 0.996 where Fisher's exact test gives 0.10, and both are reported. Enactment is read from the "
            "boundary events of the traces, so edits in modules without a probe have no enactment rate.")


def _environment_limitation() -> str:
    summary_path = E_DIR / "summary.json"
    if not summary_path.exists():
        return ""
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    unresolved = [case for case, s in summary["cases"].items() if s.get("environment_unresolved")]
    text = ("The environment experiment of section 8 changed one input per case and tested each case on its frozen inputs only. "
            "A verdict that held under E1 holds for that one changed value and not for the environment in general.")
    if unresolved:
        text += (" The E1 condition of " + ", ".join(unresolved) + " is unresolved, because the endpoint returned an error for every "
                 "request, so no verdict under that condition is an observation of the program.")
    return text


def cmd_report() -> int:
    runs = load_runs(OUT)
    comps = read_jsonl(OUT / "comparisons.jsonl")
    decisions = {d["case"]: d for d in read_jsonl(OUT / "decisions.jsonl")}
    manifest = json.loads((OUT / "experiment_manifest.json").read_text(encoding="utf-8"))
    pilot = json.loads((ROOT / "artifacts" / "pilot_results.json").read_text(encoding="utf-8"))
    reg = Registry()
    base = f"artifacts/agentdefect_extension/{EXP_ID}"
    src_runs, src_comp, src_dec = f"{base}/runs.jsonl", f"{base}/comparisons.jsonl", f"{base}/decisions.jsonl"
    lines = ["# AgentDefect extension exp-2026-10-22, contribution of persistent component changes", "",
             "<!-- hand:start -->", "", "<!-- hand:end -->", ""]
    old = OUT / "report.md"
    if old.exists() and "<!-- hand:start -->" in old.read_text(encoding="utf-8"):
        hand = old.read_text(encoding="utf-8").split("<!-- hand:start -->", 1)[1].split("<!-- hand:end -->", 1)[0]
        lines[2:5] = ["<!-- hand:start -->" + hand + "<!-- hand:end -->"]

    # 1. Case flow
    status = Counter(r["status"] for r in runs)
    lines += ["## 1. Case flow, scopes and qualification", "",
              f"The live stage recorded {reg.add('runs', len(runs), 'runs recorded in runs.jsonl', src_runs, 'line count')} runs "
              f"against {reg.add('scheduled', manifest['scheduled_executions'], 'scheduled executions', f'{base}/experiment_manifest.json', 'schedule length')} "
              f"scheduled, with no retry. Of these, {reg.add('model_enabled', manifest['model_enabled_episodes'], 'scheduled episodes in model-enabled scopes', f'{base}/experiment_manifest.json', 'cases other than 79343179')} "
              f"were in model-enabled scopes and {reg.add('loader', manifest['loader_episodes'], 'scheduled loader episodes of 79343179', f'{base}/experiment_manifest.json', 'case 79343179')} were loader episodes.", "",
              "| status | runs |", "|---|---|"]
    for name, count in sorted(status.items()):
        lines.append(f"| {name} | {reg.add('status_' + name, count, f'runs with status {name}', src_runs, 'status count')} |")
    n_inputs = sum(len(case_inputs(c)) for c in CASE_ORDER)
    lines += ["", "| unit | count |", "|---|---|",
              f"| independent programs run | {reg.add('programs', len(CASE_ORDER), 'independent programs with runs', f'{base}/experiment_manifest.json', 'CASE_ORDER')} |",
              f"| programs kept as controls without runs | {reg.add('controls', len(CONTROLS), 'programs not run, failure not reproduced', 'artifacts/pilot_results.json', 'not_repaired')} |",
              f"| inputs, over all programs | {reg.add('inputs', n_inputs, 'inputs over the six programs, a conversation counted once', f'{base}/experiment_manifest.json', 'case_inputs')} |",
              f"| configurations | {reg.add('configurations', manifest['configurations'], 'configurations over the six programs', f'{base}/experiment_manifest.json', 'configurations')} |",
              f"| comparisons | {reg.add('comparisons', manifest['comparisons'], 'with and without comparisons', f'{base}/experiment_manifest.json', 'comparisons')} |",
              f"| repetitions per configuration and input | {REPETITIONS} |"]
    lines += ["", "| case | scope | role here | required checks |", "|---|---|---|---|"]
    for case in CASE_ORDER:
        quals = qualification(case, runs)
        lines.append(f"| {case} | {'loader_only' if case == '79343179' else 'full_program'} | runs | "
                     + ", ".join(f"{k} {v['status']}" for k, v in quals.items()) + " |")
    reasons = {row["case_id"]: row["reason"] for row in pilot["not_repaired"]}
    for case in CONTROLS:
        lines.append(f"| {case} | not run | failure not reproduced in the pilot | {reasons[case]} |")
    lines += ["", "No case has a frozen preservation check, so preservation coverage is absent in every case.", ""]

    # 2. Routes
    lines += ["## 2. Existing complete routes against the frozen checks", "",
              "Each cell gives the outcome over three repetitions and the number of passing repetitions.", ""]
    routes = {"76906469": ["original", "A", "B", "AB"], "79343179": ["original", "baseline", "published"],
              "78366661": ["original", "baseline", "published"], "77178370": ["original", "audit_E1", "published"],
              "77099194": ["original", "attempt_1", "attempt_2", "published"], "78383658": ["original", "published"]}
    for case in CASE_ORDER:
        checks = [c for i in case_inputs(case) for c in i["checks"]]
        title = {"76906469": "76906469, new table, gpt-6-luna, the published two-turn conversation",
                 "79343179": "79343179, scope loader_only"}.get(case, case)
        lines += [f"### {title}", ""] + _route_table(runs, case, routes[case], checks, reg, src_runs) + [""]
        if case == "76906469":
            hist = [json.loads(line) for line in git_show("repair_family_pilot/artifacts/donor_tables/runs.jsonl").splitlines() if line.strip()]
            per_cell = Counter((r["group_id"], r["repair_set"]) for r in hist)
            hist_src = "cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl"
            groups = reg.add("hist_groups", len({r["group_id"] for r in hist}), "task groups of the historical 76906469 collection", hist_src, "distinct group_id")
            repeats = reg.add("hist_repeats", max(per_cell.values()), "repeats per group and arm in the historical collection", hist_src,
                              "rows per group_id and repair_set, all equal")
            lines += [f"### 76906469, historical table from commit cb39baa, gpt-6-luna, {groups} task groups with {repeats} repeats", "",
                      "| arm | episodes | successes |", "|---|---|---|"]
            for arm, n, ok in _historical_table():
                lines.append(f"| {arm} | {reg.add('hist_' + arm + '_n', n, f'historical episodes of arm {arm}', 'cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl', 'rows with repair_set')} | "
                             f"{reg.add('hist_' + arm + '_ok', ok, f'historical successes of arm {arm}', 'cb39baa:repair_family_pilot/artifacts/donor_tables/runs.jsonl', 'outcome success')} |")
            lines.append("")
    ev = pilot["evaluation"]

    def pilot_cell(case, arm, question):
        r = ev[case]["arms"][arm][question]
        return f"{sum(1 for x in r['repetitions'] if x.get('passed'))}/{len(r['repetitions'])}"

    lines += ["### Leaked variants, audit only, pilot results of 2026-10-20", "",
              "| case | variant | why excluded | pilot public | pilot related |", "|---|---|---|---|---|",
              f"| 77178370 | baseline | the repair prompt named brick, wood and stone | {pilot_cell('77178370', 'baseline', 'What are buildings made of?')} | "
              f"cars {pilot_cell('77178370', 'baseline', 'What are cars made out of?')}, materials {pilot_cell('77178370', 'baseline', 'Which building materials do the notes name?')} |",
              "| 78383658 | attempt_1 | the repair prompt named Harry Potter | failed its one public run | not run |",
              f"| 78383658 | attempt_2 | built from attempt_1's code | {pilot_cell('78383658', 'baseline', 'Find movies for family, combining their Name and Description.')} | "
              f"action {pilot_cell('78383658', 'baseline', 'Find movies whose genres include Action. Return each title with its description.')}, "
              f"adventure {pilot_cell('78383658', 'baseline', 'Find movies whose genres include Adventure. Return each title with its description.')} |", ""]

    # 3. Reductions
    lines += ["## 3. With and without comparisons", "",
              "| comparison | change | components | without | with | class | verdict |", "|---|---|---|---|---|---|---|"]
    for row in comps:
        comps_of = ", ".join(COMPONENTS[row["case"]].get(row["change"], []))
        lines.append(f"| {row['comparison_id']} | {row['change']} | {comps_of} | {row['without']} {row['without_adequacy']['adequacy']} | "
                     f"{row['with']} {row['with_adequacy']['adequacy']} | {row['class']} | {row['verdict'] or 'none, diagnostic'} |")
    lines += ["", "| case | change | useful observed | conditionally necessary observed | redundant within evaluated contexts |", "|---|---|---|---|---|"]
    with (OUT / "contribution_verdicts.csv").open(newline="", encoding="utf-8") as handle:
        for v in csv.DictReader(handle):
            lines.append(f"| {v['case']} | {v['change']} | {v['useful_observed']} | {v['conditionally_necessary_observed']} | {v['redundant_within_evaluated_contexts']} |")
    lines.append("")
    for case in MINIMALITY_ROUTES:
        quals = qualification(case, runs)
        configs = build_configurations(case)
        adeq = {n: adequacy(runs, case, n, quals)["adequacy"] for n in configs}
        lines += _minimality(case, configs, adeq)
    lines += ["", "The 76906469 comparisons that contain B without A are interface dependency diagnostics. B stopped before any model "
              "request with the error that chat_history should be a list of base messages. They support no claim about the agent module "
              "as a repair scope.", ""]

    # 4. Intermediate observations
    lines += ["## 4. Intermediate observations, repetition 1 of each input unless stated", ""]
    def derived(r):
        return instrument.derive(instrument.read_trace(OUT / r["trace"])) if r.get("trace") else None
    probed = [r for r in runs if r["probe"]]
    lines += ["### 76906469", "", "| configuration | memory value type | model requests | turn 2 request holds the turn 1 question | stop stage |", "|---|---|---|---|---|"]
    for name in ("original", "A", "B", "AB"):
        r = next(x for x in probed if x["case"] == "76906469" and x["configuration"] == name and x["repetition"] == 1)
        d = derived(r)
        holds = any("capital of France" in json.dumps(m) for m in d["request_messages"][1:])
        types = sorted({t.get("chat_history") for m in d["memory_before"] for t in [m["types"] or {}]})
        lines.append(f"| {name} | {', '.join(str(t) for t in types)} | {d['requests_prepared']} | {'yes' if holds else 'no'} | {r.get('failure_stage') or 'completed'} |")
    lines += ["", "### 79343179", "", "| configuration | columns | expected names present | names missing | rows |", "|---|---|---|---|---|"]
    for name in build_configurations("79343179"):
        r = next(x for x in probed if x["case"] == "79343179" and x["configuration"] == name and x["repetition"] == 1)
        cols = r["loader"]["columns"]
        present = [c for c in LOADER_COLUMNS if c in cols]
        missing = [c for c in LOADER_COLUMNS if c not in cols]
        lines.append(f"| {name} | {len(cols)} | {len(present)} | {', '.join(missing) or 'none'} | {r['loader']['rows']} |")
    lines += ["", "### 78366661", "", "| configuration | texts embedded | passages returned |", "|---|---|---|"]
    for name in build_configurations("78366661"):
        r = next(x for x in probed if x["case"] == "78366661" and x["configuration"] == name and x["repetition"] == 1)
        d = derived(r)
        embedded = sum(e.get("count") or 0 for e in d["embeddings"] if e.get("method") == "embed_documents")
        lines.append(f"| {name} | {reg.add('embedded_' + safe_id(name), embedded, f'texts embedded by 78366661 {name}, repetition 1', src_runs, 'embed_documents counts in the trace')} | "
                     f"{d['finals'][0]['count'] if d['finals'] else 0} |")
    lines += ["", "### 77178370, all three repetitions", "",
              "| configuration | input | runs with a tool call | runs that retrieved notes | runs whose model request held a note | passes |", "|---|---|---|---|---|---|"]
    for name in ("original", "audit_E1", "P_core", "published"):
        for item in case_inputs("77178370"):
            rs = [x for x in probed if x["case"] == "77178370" and x["configuration"] == name and x["input_id"] == item["input_id"]]
            ds = [derived(x) for x in rs]
            tool = sum(1 for d in ds if any(t.get("stage") == "start" for t in d["tool_calls"]))
            ret = sum(1 for d in ds if any(x.get("documents") for x in d["retrieved"]))
            note = sum(1 for d in ds if any("Buildings are made out of" in json.dumps(m) or "Cars are made out of" in json.dumps(m) for m in d["request_messages"]))
            ok = sum(1 for x in rs if x["status"] == "completed_pass")
            lines.append(f"| {name} | {item['input_id']} | {tool}/{len(rs)} | {ret}/{len(rs)} | {note}/{len(rs)} | {ok}/{len(rs)} |")
    for case, fname in (("77099194", "movies.csv"), ("78383658", "control.csv")):
        lines += ["", f"### {case}", "", "| configuration | input | documents retrieved | missing titles | missing titles that were in the retrieved context |", "|---|---|---|---|---|"]
        for name in build_configurations(case):
            for item in case_inputs(case):
                r = next(x for x in probed if x["case"] == case and x["configuration"] == name and x["input_id"] == item["input_id"] and x["repetition"] == 1)
                d = derived(r)
                docs = [doc.get("page_content", "") for x in d["retrieved"] if x["boundary"] == "retrieval" for doc in (x.get("documents") or []) if isinstance(doc, dict)]
                missing = (r["checks"].get(item["input_id"]) or {}).get("missing") or []
                present = [m for m in missing if any(m in doc for doc in docs)]
                cells = []
                for label, value in (("docs", len(docs)), ("missing", len(missing)), ("missing_in_context", len(present))):
                    if value >= 10:
                        value = reg.add(f"{case}_{safe_id(name)}_{item['input_id']}_{label}", value,
                                        f"{label.replace('_', ' ')} for {case} {name} {item['input_id']}, repetition 1", src_runs,
                                        "retrieval events in the trace and the check's missing list")
                    cells.append(str(value))
                lines.append(f"| {name} | {item['input_id']} | " + " | ".join(cells) + " |")
    lines.append("")

    # 5. Decisions
    lines += ["## 5. Repair decisions", "",
              "| case | initial candidate | adequacy before | decision | retained | adequacy after | modules before, after | actions before, after |",
              "|---|---|---|---|---|---|---|---|"]
    for case in CASE_ORDER:
        d = decisions[case]
        show = lambda value: "none" if value is None else value
        lines.append(f"| {case} | {show(d['initial_candidate'])} | {show(d['adequacy_before'])} | {d['decision']} | {show(d['retained_candidate'])} | "
                     f"{show(d['adequacy_after'])} | {show(d['modules_before'])}, {show(d['modules_after'])} | {show(d['actions_before'])}, {show(d['actions_after'])} |")
    lines.append("")

    # 6. Usage
    tokens_in = sum((r.get("tokens") or {}).get("prompt") or 0 for r in runs)
    tokens_out = sum((r.get("tokens") or {}).get("completion") or 0 for r in runs)
    requests = sum(r.get("chat_requests") or 0 for r in runs)
    attempts = sum((r.get("derived") or {}).get("backend_attempts") or 0 for r in runs)
    chars = sum(r.get("embedding_characters") or 0 for r in runs)
    dollars = tokens_in * pr.PRICE_IN + tokens_out * pr.PRICE_OUT + chars / 4 * EMBED_PRICE
    lines += ["## 6. Executions, model calls and tokens", "",
              f"Chat model requests numbered {reg.add('chat_requests', requests, 'successful chat requests over all runs', src_runs, 'sum of chat_requests')}, "
              f"and probed runs recorded {reg.add('backend_attempts', attempts, 'model API network attempts in probed runs', src_runs, 'sum of derived.backend_attempts')} "
              f"model API network attempts including embeddings. Chat use was {reg.add('tokens_in', tokens_in, 'chat input tokens over all runs', src_runs, 'sum of tokens.prompt')} "
              f"input and {reg.add('tokens_out', tokens_out, 'chat output tokens over all runs', src_runs, 'sum of tokens.completion')} output tokens. "
              f"Embedding calls received {reg.add('embed_chars', chars, 'characters sent to embedding calls in probed runs', src_runs, 'sum of embedding_characters')} characters. "
              f"At the pilot price constants and an assumed embedding price the recorded use costs about "
              f"${reg.add('cost', round(dollars, 2), 'estimated dollars of recorded use', src_runs, 'tokens times pilot_run.PRICE_IN and PRICE_OUT plus characters over four times 0.10 per million')}.", "",
              "The 76906469 historical table is read from commit cb39baa and the leaked variants from the pilot results of 2026-10-20. "
              "No earlier run was reused as a matched run.", ""]
    lines += _retrieval_section(reg)
    lines += _environment_section(reg)
    lines += _reanalysis_section(reg)
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    limits = ["# Limitations", "",
              "The verdicts concern the evaluated configurations and the frozen checks of each case only.",
              "In 78383658 the expected titles were absent from the retrieved documents in every configuration and input pair of "
              "exp-2026-10-22, where every evaluated candidate kept the default retrieval limit.",
              _scorer_limitation(),
              "The 78383658 retrieval intervention of section 7 is evaluator designed and serves as development evidence, not as a discovered "
              "repair. It was tested on the three frozen inputs of that case only.",
              "The PDF case check is a reproduction endpoint. A nonempty passage list does not establish passage relevance or complete PDF search recovery.",
              "The 76906469 check is a limited endpoint that looks for the word france in the second answer. Both raw answers are kept in runs.jsonl.",
              "No case has a frozen preservation check, so no regression claim is made.",
              "79343179 ran in loader scope only. The full agent was not run.",
              "Three repetitions are an observed pass rule for this pilot, not a statement about general reliability.",
              "The 77178370 public check uses the versioned oracle correction of oracle_corrections.json.",
              "The boundary states written during the live run counted installed probes as observations. The tables here recompute them from the traces.",
              _environment_limitation(), _reanalysis_limitation(), ""]
    (OUT / "limitations.md").write_text("\n".join(line for line in limits if line is not None), encoding="utf-8")
    reg.write()
    print("report.md, limitations.md, NUMBERS.md ext block written")
    return 0


# ---------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motivation_pilot.extension")
    parser.add_argument("command", choices=["map", "manifest", "selftest", "live", "compare", "report", "rescore"])
    args = parser.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    return {"map": cmd_map, "manifest": cmd_manifest, "selftest": cmd_selftest, "live": cmd_live,
            "compare": cmd_compare, "report": cmd_report, "rescore": cmd_rescore}[args.command]()


if __name__ == "__main__":
    sys.exit(main())
