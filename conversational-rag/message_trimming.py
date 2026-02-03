# trim chat history so we dont hit token limit - keep recent stuff

import os
import argparse
from typing import List, Dict, Any, Optional, Tuple

import tiktoken
from dotenv import load_dotenv

load_dotenv()

DEFAULT_STRATEGY = "last_n"
DEFAULT_MODEL = "gpt-4"
TIKTOKEN_ENCODING = "cl100k_base"  # fallback if model not found


def get_encoding(model: Optional[str] = None) -> tiktoken.Encoding:
    # tiktoken encoding for model
    try:
        return tiktoken.encoding_for_model(model or DEFAULT_MODEL)
    except KeyError:
        return tiktoken.get_encoding(TIKTOKEN_ENCODING)


def count_tokens(messages: List[Dict[str, str]], encoding: Optional[tiktoken.Encoding] = None) -> int:
    # count tokens for all messages (rough)
    if encoding is None:
        encoding = get_encoding()
    total = 0
    for msg in messages:
        text = f"{msg.get('role', '')} {msg.get('content', '')}"
        total += len(encoding.encode(text)) + 4
    return total


def _to_dict_list(messages: List[Any]) -> List[Dict[str, str]]:
    # make everything {role, content}
    result = []
    for m in messages:
        if isinstance(m, dict):
            result.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        else:
            role = getattr(m, "type", None) or getattr(m, "role", "user")
            if role == "human":
                role = "user"
            elif role == "ai":
                role = "assistant"
            content = getattr(m, "content", "") or getattr(m, "message", "")
            if isinstance(content, list) and content and hasattr(content[0], "get"):
                content = content[0].get("text", str(content))
            result.append({"role": role, "content": str(content)})
    return result


def trim_messages(
    messages: List[Any],
    max_tokens: Optional[int] = None,
    max_history_length: Optional[int] = None,
    strategy: str = DEFAULT_STRATEGY,
    model: Optional[str] = DEFAULT_MODEL,
) -> Tuple[List[Dict[str, str]], int]:
    # trim to fit token/history limit, return trimmed list and token count
    encoding = get_encoding(model)
    normalized = _to_dict_list(messages)
    max_len = max_history_length or int(os.getenv("MAX_HISTORY_LENGTH", "10"))
    max_messages = 2 * max_len  # pairs = user+assistant

    if max_tokens is None:
        max_tokens = 4096

    if len(normalized) <= max_messages and count_tokens(normalized, encoding) <= max_tokens:
        return normalized, count_tokens(normalized, encoding)

    if strategy == "last_n_drop" or strategy == "last_n":
        trimmed = normalized[-max_messages:] if len(normalized) > max_messages else normalized
    elif strategy == "last_n_summarize":
        # keep last N, older ones become one summary line
        if len(normalized) <= max_messages:
            trimmed = normalized
        else:
            older = normalized[:-max_messages]
            summary_msg = {
                "role": "system",
                "content": f"[Previous conversation summary: {len(older)} messages omitted for length.]",
            }
            trimmed = [summary_msg] + normalized[-max_messages:]
    else:
        trimmed = normalized[-max_messages:] if len(normalized) > max_messages else normalized

    # still too long? drop oldest til under
    while len(trimmed) > 1 and count_tokens(trimmed, encoding) > max_tokens:
        trimmed = trimmed[1:]
    total_tokens = count_tokens(trimmed, encoding)
    return trimmed, total_tokens


def run_test() -> None:
    # quick test - long history then trim, print before/after
    encoding = get_encoding()
    long_history = []
    for i in range(15):
        long_history.append({"role": "user", "content": f"User question number {i} here. " * 20})
        long_history.append({"role": "assistant", "content": f"Assistant answer number {i} here. " * 30})

    before_tokens = count_tokens(long_history, encoding)
    print(f"Before trim: {len(long_history)} messages, ~{before_tokens} tokens")

    trimmed, after_tokens = trim_messages(
        long_history,
        max_history_length=5,
        strategy="last_n",
    )
    print(f"After trim (last_n, max_history_length=5): {len(trimmed)} messages, ~{after_tokens} tokens")

    trimmed2, after_tokens2 = trim_messages(
        long_history,
        max_history_length=5,
        strategy="last_n_summarize",
    )
    print(f"After trim (last_n_summarize, max_history_length=5): {len(trimmed2)} messages, ~{after_tokens2} tokens")
    print("Test passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Message trimming for conversational RAG")
    parser.add_argument("--test", action="store_true", help="Run trimming test")
    args = parser.parse_args()
    if args.test:
        run_test()
