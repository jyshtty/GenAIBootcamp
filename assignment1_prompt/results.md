# Tokenization Analysis Across Different LLM Models

## Objective

The goal of this assignment is to compare token counts across multiple languages using different Large Language Model (LLM) tokenizers.

---

# Token Count Results

| Model         | English | Spanish | Arabic | Hindi |
| ------------- | ------- | ------- | ------ | ----- |
| GPT-3.5-Turbo | 47      | 71      | 113    | 213   |
| GPT-4         | 47      | 71      | 113    | 213   |
| GPT-4o        | 47      | 55      | 68     | 69    |

---

# Observations

1. English generated the fewest tokens across all models because most tokenizers are highly optimized for English text.

2. Arabic and Hindi generated significantly more tokens in GPT-3.5-Turbo and GPT-4 due to:

   * Unicode-based scripts
   * Different character segmentation strategies
   * Subword tokenization behavior

3. GPT-4o performed much better for multilingual tokenization:

   * Spanish tokens reduced from 71 → 55
   * Arabic tokens reduced from 113 → 68
   * Hindi tokens reduced from 213 → 69

4. This indicates that GPT-4o uses a more efficient tokenizer (`o200k_base`) for multilingual text compared to the older `cl100k_base` tokenizer used in GPT-3.5 and GPT-4.

---

# Impact on LLM Usage

Tokenization directly affects:

* API Cost
  More tokens increase usage cost.

* Context Window Usage
  Higher token counts consume context length faster.

* Inference Speed
  More tokens require more computation.

* Multilingual Performance
  Efficient tokenization improves performance and reduces cost for non-English languages.

---

# Conclusion

This experiment demonstrates that tokenization efficiency varies significantly across languages and models. Modern models like GPT-4o are considerably more optimized for multilingual text, making them more cost-effective and efficient for global applications.
