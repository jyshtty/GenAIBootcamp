# Assignment 1: Exploring Tokenization Across Models and Languages

**Focus:** Calculate and compare token counts for given texts across LLM models and languages to understand tokenization differences.

## What You Need to Do

1. **Compute token counts** for the four texts below across:
   - **Mandatory models:** GPT-3.5-Turbo, GPT-4, GPT-4o (each over all 4 languages).
   - **Optional models:** Llama-3.1-8B, Mistral-v0.3, Mistral-Nemo (or other comparable models if you prefer).

2. **Present your results** in any clear format:
   - A markdown/HTML table is ideal, but **printing token counts** (e.g. from a script) is also acceptable.
   - Ensure each model × language count is identifiable.

3. **Write a short reflection** on:
   - What you observed about tokenization (e.g. by language, script, model).
   - How this might affect LLM usage (cost, context length, multilingual behavior).

## Texts to Use

- **English:** "The cat sat on the windowsill, watching the rain fall. Suddenly, a flash of lightning lit up the sky, startling the little creature. It leaped down and scurried to its favorite hiding spot under the bed."
- **Spanish:** "El gato estaba sentado en el alféizar de la ventana, mirando la lluvia caer. De repente, un relámpago iluminó el cielo, sobresaltando a la pequeña criatura. Saltó y corrió a su escondite favorito debajo de la cama."
- **Arabic:** "جلست القطة على حافة النافذة، تراقب هطول المطر. وفجأة، أضاءت ومضة من البرق السماء، مما أثار ذهول المخلوق الصغير. قفزت إلى أسفل وهرعت إلى مكان اختبائها المفضل تحت السرير."
- **Hindi:** "बिल् ली खि ड़की पर बैठी हुई बा रि श को देख रही थी । अचा नक, आसमा न में बि जली चमकी , जि ससे छो टा जी व चौं क गया । वह नी चे कूद गई और बि स्तर के नी चे अपनी पसंदी दा छि पने की जगह पर भा ग गई।"

*(If the assignment PDF is image-based and you use OCR, small differences in spaces or punctuation can change token counts slightly; that is acceptable.)*

## Evaluation at a Glance

- **Total marks:** 100 (84 for mandatory GPT models, 16 for optional models, plus reflection).
- **Passing marks:** 70/100.
- Evaluators use the expected reference counts as a guide but allow **minor variations** (e.g. ±5 tokens) due to OCR, preprocessing, or model versions.
- Using **alternative models** instead of the listed optional ones is fine if you show understanding of tokenization concepts.

## How to Run Tests

```bash
python -m unittest tests.test -v
```
