# compare 2 embedding models - speed, quality and dimension

import time
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer


# query and correct doc pairs for checking quality
QUALITY_PAIRS = [
    ("What is machine learning?", "Machine learning is a subset of artificial intelligence that enables systems to learn from data."),
    ("How does a neural network work?", "Neural networks consist of layers of nodes that process inputs and produce outputs using weights and activation functions."),
    ("What is natural language processing?", "Natural language processing is the field of AI that deals with understanding and generating human language."),
    ("What are embeddings?", "Embeddings are dense vector representations of text or other data used for similarity and retrieval."),
    ("What is retrieval augmented generation?", "RAG combines retrieval of relevant documents with a language model to generate accurate, grounded answers."),
]


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """cosine sim between two vectors"""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


class EmbeddingComparison:
    """run comparison on sentence-transformers models"""

    def __init__(self):
        """dont load anything heavy here"""
        self._model_cache: Dict[str, SentenceTransformer] = {}

    def load_sentence_transformers_model(self, model_name: str = "all-MiniLM-L6-v2"):
        """load model by name, cache it"""
        if model_name not in self._model_cache:
            self._model_cache[model_name] = SentenceTransformer(model_name)
        return self._model_cache[model_name]

    def load_other_embedding_models(self) -> Dict[str, SentenceTransformer]:
        """get both models we compare"""
        models = {}
        for name in ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"]:
            models[name] = self.load_sentence_transformers_model(name)
        return models

    def measure_embedding_speed(self, texts: List[str], model_name: str) -> float:
        """time how long to embed all texts, return avg per text"""
        model = self.load_sentence_transformers_model(model_name)
        start = time.perf_counter()
        model.encode(texts)
        elapsed = time.perf_counter() - start
        return elapsed / len(texts) if texts else 0.0

    def evaluate_embedding_quality(self, model_name: str) -> Dict[str, float]:
        """check how good query-doc similarity is for our pairs"""
        model = self.load_sentence_transformers_model(model_name)
        queries = [p[0] for p in QUALITY_PAIRS]
        correct_docs = [p[1] for p in QUALITY_PAIRS]
        query_embs = model.encode(queries)
        doc_embs = model.encode(correct_docs)
        correct_sims = [cosine_similarity(query_embs[i], doc_embs[i]) for i in range(len(QUALITY_PAIRS))]
        mean_correct = float(np.mean(correct_sims))
        accuracy = sum(1 for s in correct_sims if s > 0.5) / len(correct_sims) if correct_sims else 0.0
        return {"accuracy": accuracy, "mean_correct_similarity": mean_correct}

    def compare_embedding_dimensions(self) -> Dict[str, int]:
        """get dimension for each model"""
        result = {}
        for name in ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"]:
            model = self.load_sentence_transformers_model(name)
            dim = model.get_sentence_embedding_dimension()
            result[name] = dim
        return result

    def run_comparison(self):
        """print report with dimensions speed quality and what to use when"""
        print("=== Embedding Model Comparison Report ===\n")

        model_names = ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"]
        sample_texts = [p[0] for p in QUALITY_PAIRS] + [p[1] for p in QUALITY_PAIRS]

        dimensions = self.compare_embedding_dimensions()
        print("Dimensions:")
        for name, dim in dimensions.items():
            print(f"  {name}: {dim}")

        print("\nSpeed (avg seconds per text, batch of {}):".format(len(sample_texts)))
        speed_results = {}
        for name in model_names:
            t = self.measure_embedding_speed(sample_texts, name)
            speed_results[name] = t
            print(f"  {name}: {t:.4f}s")

        print("\nQuality (mean correct query-doc similarity, accuracy):")
        for name in model_names:
            metrics = self.evaluate_embedding_quality(name)
            print(f"  {name}: mean_similarity={metrics['mean_correct_similarity']:.4f}, accuracy={metrics['accuracy']:.2f}")

        print("\n--- Recommendation ---")
        print("  all-MiniLM-L6-v2: Good balance of speed and quality; smaller dimension (384). Use for fast retrieval.")
        print("  paraphrase-MiniLM-L3-v2: Smaller/faster model (384 dim); use when latency is critical.")
        print("  For best quality on semantic similarity, consider all-mpnet-base-v2 (768 dim, slower).")


if __name__ == "__main__":
    comparison = EmbeddingComparison()
    comparison.run_comparison()
