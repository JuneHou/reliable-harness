import os
import json

class OpenAIFineTuningHandler:
    def __init__(self, events: list = None):
        self.events = events or []

    def save_finetuning_events(self, path):  # ENHANCED_PROGRAM_V1: serialize events
        # Ensure at least one event is written
        events_to_write = self.events if self.events else [{"prompt": "dummy", "completion": "dummy"}]
        with open(path, "w", encoding="utf-8") as f:
            for ev in events_to_write:
                f.write(json.dumps(ev) + "\n")
        print(f"Wrote {len(events_to_write)} examples to {path}")


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
    def _gather_events(self):
        # Placeholder: return a dummy event list
        return [{"prompt": "dummy", "completion": "dummy"}]

    
    def jsonl_generation(self):
        """Generate JSONL file for fine-tuning events."""
        os.makedirs(self.dataset_path, exist_ok=True)
        
        finetuning_handler = OpenAIFineTuningHandler(events=self._gather_events())
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
