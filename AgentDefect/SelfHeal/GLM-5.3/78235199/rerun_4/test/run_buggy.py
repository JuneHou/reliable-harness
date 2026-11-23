import os

class OpenAIFineTuningHandler:
    def save_finetuning_events(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")  
        print(f"Wrote 0 examples to {path}")


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
