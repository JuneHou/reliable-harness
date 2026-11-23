import json
import os

# ENHANCED_PROGRAM_V1: Centralised prompt construction
from dataclasses import dataclass, field

@dataclass
class PromptBuilder:
    task_description: str = "Perform the given task."
    history: str = ""
    constraints: str = "Follow all constraints."
    extra: dict = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        # Merge defaults with provided overrides
        data = {
            "task_description": self.task_description,
            "history": self.history,
            "constraints": self.constraints,
            **self.extra,
            **kwargs,
        }
        # Ensure mandatory fields are present
        for key in ("task_description", "history", "constraints"):
            data.setdefault(key, "")
        # Simple template rendering
        prompt = f"""Task: {data['task_description']}
History: {data['history']}
Constraints: {data['constraints']}
"""
        # Append any additional sections
        for k, v in data.items():
            if k not in ("task_description", "history", "constraints"):
                prompt += f"{k.capitalize()}: {v}\n"
        return prompt.strip()

# ENHANCED_PROGRAM_V1: Persistence guidance for give‑up handling
MAX_GIVEUP_RETRIES = 2

class PersistenceGuidance:
    """Decides whether to retry when the model says it cannot determine."""
    def __init__(self):
        self.retry_count = 0

    def should_retry(self, response_text: str) -> bool:
        lowered = response_text.lower()
        give_up_phrases = [
            "unable to determine",
            "cannot find",
            "i cannot determine",
            "i am unable to determine",
        ]
        if any(p in lowered for p in give_up_phrases):
            if self.retry_count < MAX_GIVEUP_RETRIES:
                self.retry_count += 1
                return True
        return False


class OpenAIFineTuningHandler:
    """Collects fine‑tuning events and writes them as JSONL."""
    def __init__(self):
        self._events = []  # type: list[dict]

    def record_event(self, event: dict):
        """Add a fine‑tuning example."""
        self._events.append(event)

    def save_finetuning_events(self, path):
        if not self._events:
            # No events to write – raise to surface test failures
            raise ValueError("No fine‑tuning events recorded.")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for ev in self._events:
                f.write(json.dumps(ev) + "\n")
        print(f"Wrote {len(self._events)} examples to {path}")



class CallbackManager:
   
    def __init__(self, handlers):
        self.handlers = handlers


class VectorStoreIndex:

    @staticmethod
    def from_documents(docs):
        return VectorStoreIndex()
    
    def as_query_engine(self, similarity_top_k, llm):
        return self
    
    def query(self, question):
        return None



class FineTuningExample:
    def __init__(self, dataset_path, documents):
        self.dataset_path = dataset_path
        self.documents = documents
        self.llm = None

    
    def jsonl_generation(self):
        """Generate JSONL file for fine-tuning events."""
        os.makedirs(self.dataset_path, exist_ok=True)
        
        finetuning_handler = OpenAIFineTuningHandler()
        callback_manager = CallbackManager([finetuning_handler])
        self.llm = type("LLM", (), {"callback_manager": callback_manager})()
        
        questions = []
        with open(f'{self.dataset_path}/train_questions.txt', "r", encoding='utf-8') as f:
            for line in f:
                questions.append(line.strip())
        
        try:
            index = VectorStoreIndex.from_documents(self.documents)
            query_engine = index.as_query_engine(similarity_top_k=2, llm=self.llm)
            for question in questions:
                response = query_engine.query(question)
                # Record a minimal fine‑tuning event (question & response)
                if hasattr(finetuning_handler, "record_event"):
                    finetuning_handler.record_event({"question": question, "response": response})
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            finetuning_handler.save_finetuning_events(
                f'{self.dataset_path}/finetuning_events.jsonl'
            )


def prepare_test_data(questions_path):
    os.makedirs(os.path.dirname(questions_path), exist_ok=True)
    with open(questions_path, "w", encoding="utf-8") as f:
        f.write("Question 1\nQuestion 2\n")


def run_agent(questions_path):
   
    dataset_path = os.path.dirname(questions_path)
    ft = FineTuningExample(dataset_path=dataset_path, documents=[])
    ft.jsonl_generation()


if __name__ == "__main__":
    questions_path = "./dataset_data/train_questions.txt"
    prepare_test_data(questions_path)
    run_agent(questions_path)
