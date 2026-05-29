"""
Compare sentence-transformer embedding models on speed, quality, and dimensions.

Models compared:
  - all-MiniLM-L6-v2   (384-dim, fast, general purpose)
  - all-mpnet-base-v2  (768-dim, higher quality, slower)

Example usage:
    python embedding_comparison.py
"""

import time
from typing import List, Dict, Tuple

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

MODELS = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]

TEST_TEXTS = [
    "Artificial intelligence is transforming modern technology.",
    "Machine learning enables systems to learn from data automatically.",
    "The weather today is sunny with light winds.",
    "Paris is the capital city of France.",
    "Deep neural networks have revolutionized computer vision tasks.",
    "Natural language processing allows computers to understand human text.",
    "The stock market closed higher after positive earnings reports.",
    "Vector embeddings represent text as high-dimensional numerical arrays.",
    "Retrieval Augmented Generation grounds LLM answers in retrieved facts.",
    "Python is a popular programming language for data science and AI.",
]

# (text_a, text_b, should_be_similar)
SIMILARITY_PAIRS: List[Tuple[str, str, bool]] = [
    (
        "AI is reshaping the world of technology",
        "Artificial intelligence is transforming modern technology.",
        True,
    ),
    (
        "Learning algorithms improve with more training data",
        "Machine learning enables systems to learn from data automatically.",
        True,
    ),
    (
        "Deep learning and neural networks are closely related",
        "Deep neural networks have revolutionized computer vision tasks.",
        True,
    ),
    (
        "The food in Italy is delicious",
        "Paris is the capital city of France.",
        False,
    ),
    (
        "Stock prices went up today",
        "The weather today is sunny with light winds.",
        False,
    ),
]


class EmbeddingComparison:
    def __init__(self):
        """Cache loaded models to avoid reloading between tests."""
        self._models: Dict[str, HuggingFaceEmbeddings] = {}

    def load_model(self, model_name: str) -> HuggingFaceEmbeddings:
        if model_name not in self._models:
            print(f"  Loading '{model_name}'...")
            self._models[model_name] = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={"device": "cpu"},
            )
        return self._models[model_name]

    # ------------------------------------------------------------------
    # Speed
    # ------------------------------------------------------------------

    def measure_embedding_speed(self, texts: List[str], model_name: str) -> float:
        """
        Return average embedding time in milliseconds per text.

        Args:
            texts (List[str]): Texts to embed
            model_name (str): Model identifier

        Returns:
            float: ms per document
        """
        model = self.load_model(model_name)
        # Warm-up
        model.embed_query(texts[0])
        start = time.perf_counter()
        model.embed_documents(texts)
        elapsed = time.perf_counter() - start
        return round(elapsed / len(texts) * 1000, 3)

    # ------------------------------------------------------------------
    # Quality
    # ------------------------------------------------------------------

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

    def evaluate_embedding_quality(self, model_name: str) -> Dict[str, float]:
        """
        Evaluate quality via cosine similarity on labelled sentence pairs.

        Args:
            model_name (str): Model identifier

        Returns:
            dict: accuracy, avg_related_sim, avg_unrelated_sim
        """
        model = self.load_model(model_name)
        correct = 0
        related_sims, unrelated_sims = [], []

        for text_a, text_b, should_be_similar in SIMILARITY_PAIRS:
            emb_a = model.embed_query(text_a)
            emb_b = model.embed_query(text_b)
            sim = self.cosine_similarity(emb_a, emb_b)
            predicted_similar = sim > 0.5
            if predicted_similar == should_be_similar:
                correct += 1
            (related_sims if should_be_similar else unrelated_sims).append(sim)

        return {
            "accuracy": round(correct / len(SIMILARITY_PAIRS), 3),
            "avg_related_similarity": round(float(np.mean(related_sims)), 4),
            "avg_unrelated_similarity": round(float(np.mean(unrelated_sims)), 4),
        }

    # ------------------------------------------------------------------
    # Dimensions
    # ------------------------------------------------------------------

    def compare_embedding_dimensions(self) -> Dict[str, int]:
        """Return the vector dimension for each model."""
        return {
            name: len(self.load_model(name).embed_query("dimension check"))
            for name in MODELS
        }

    # ------------------------------------------------------------------
    # Full report
    # ------------------------------------------------------------------

    def run_comparison(self):
        """Run all benchmarks and print a formatted report."""
        print("\n" + "=" * 55)
        print("  Embedding Model Comparison Report")
        print("=" * 55)

        print("\n[1] Pre-loading models")
        for name in MODELS:
            self.load_model(name)

        print("\n[2] Embedding Dimensions")
        dims = self.compare_embedding_dimensions()
        for name, dim in dims.items():
            print(f"  {name:<30} {dim}d")

        print("\n[3] Embedding Speed  (ms / document)")
        speeds: Dict[str, float] = {}
        for name in MODELS:
            ms = self.measure_embedding_speed(TEST_TEXTS, name)
            speeds[name] = ms
            print(f"  {name:<30} {ms} ms")

        print("\n[4] Embedding Quality  (cosine similarity on labelled pairs)")
        qualities: Dict[str, Dict] = {}
        for name in MODELS:
            q = self.evaluate_embedding_quality(name)
            qualities[name] = q
            print(
                f"  {name:<30} "
                f"accuracy={q['accuracy']}  "
                f"related_sim={q['avg_related_similarity']}  "
                f"unrelated_sim={q['avg_unrelated_similarity']}"
            )

        print("\n[5] Recommendations")
        faster = min(speeds, key=speeds.get)
        more_accurate = max(qualities, key=lambda k: qualities[k]["accuracy"])
        print(f"  Fastest model       : {faster}  ({speeds[faster]} ms/doc)")
        print(f"  Most accurate model : {more_accurate}")
        print()
        print("  all-MiniLM-L6-v2   — 384d, 6x faster, good general-purpose baseline.")
        print("                        Ideal for high-throughput or resource-limited use.")
        print("  all-mpnet-base-v2  — 768d, higher semantic fidelity.")
        print("                        Better for tasks where retrieval precision matters.")
        print("=" * 55)


if __name__ == "__main__":
    comparison = EmbeddingComparison()
    comparison.run_comparison()
