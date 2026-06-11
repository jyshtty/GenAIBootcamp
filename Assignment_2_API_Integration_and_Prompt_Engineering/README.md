# Assignment 2: API Integration and Prompt Engineering

**Focus:** Use an LLM (e.g. via DIAL API) to implement four prompt-engineering tasks. Evaluation focuses on **core objectives** rather than strict format; passing marks are **70/100**.

## What You Need to Do

Implement the four tasks (e.g. in a notebook or `02-Assignment-ApiPromptEngineering.py`). Each task should call the LLM with a clear prompt and return the required output.

### Task 1: `classify_and_prioritize(ticket_text)`

- **Classify** the support ticket into one of: `Bug`, `Feature Request`, `Question`, `Praise`, `Complaint`.
- **Assign** priority: `High`, `Medium`, or `Low`.
- **Return** a JSON object like `{"category": "...", "priority": "..."}`. Minor format variations (whitespace, key order) are acceptable as long as the structure is valid.

### Task 2: `solve_logic_puzzle(puzzle)`

- Use **Chain-of-Thought (CoT)** in your prompt: include an example that shows step-by-step reasoning for a similar puzzle.
- For the given puzzle (four friends: Alex, Ben, Chris, David in a line; Chris not at either end; Ben in front of Alex; David behind Chris), the correct order front-to-back is: **Chris, Ben, Alex, David**.
- Return the final order in any clear format (e.g. list or string) so the order is unambiguous.

### Task 3: `generate_python_function(description)`

- Given a natural-language description, generate the corresponding Python function.
- Prefer **only code** (no extra explanation); minimal comments are acceptable. Evaluation focuses on whether the generated code is correct and runnable.

### Task 4: `parse_email_body(email_text)`

- Extract **Name, Email, Phone** from the **primary** (sender’s) signature; ignore forwarded text and other signatures.
- Return a JSON object or `None` when no clear signature is found. Focus on correct extraction; strict JSON formatting is secondary.

## Evaluation at a Glance

- **Total marks:** 100 (25 per task).
- **Passing marks:** 70/100.
- Reviewers assess whether you **achieved the task goals** with the LLM; they are lenient on minor JSON/format differences and small output variations when the intent is correct.

## How to Run Tests

```bash
python -m unittest tests.test -v
```
