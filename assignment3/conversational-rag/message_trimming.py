"""
Smart message trimming to keep conversation history within LLM token limits.

Strategies
----------
  last_n   — keep only the most recent N human/AI pairs
  tokens   — keep messages until the token budget is consumed (newest first)
  smart    — tokens-based, but always keeps at least min_messages pairs

Example usage:
    python message_trimming.py --test
"""

import argparse
from typing import List, Dict

try:
    import tiktoken
    _ENCODER = tiktoken.get_encoding("cl100k_base")

    def _count_tokens(text: str) -> int:
        return len(_ENCODER.encode(text))

except ImportError:
    def _count_tokens(text: str) -> int:  # fallback: rough char-based estimate
        return len(text) // 4


def _msg_tokens(msg: Dict) -> int:
    return _count_tokens(msg.get("content", "")) + 4  # 4 tokens overhead per message


def get_encoding():
    """Return the tiktoken encoder (cl100k_base) or a char-based fallback."""
    try:
        import tiktoken
        return tiktoken.get_encoding("cl100k_base")
    except ImportError:
        class _FallbackEncoder:
            def encode(self, text: str):
                return list(text)
        return _FallbackEncoder()


def count_tokens(messages: List[Dict]) -> int:
    """Total token count across a list of {"role", "content"} messages."""
    return sum(_msg_tokens(m) for m in messages)


def trim_messages(messages: List[Dict], max_history_length: int = 10):
    """
    Keep the last `max_history_length` user/assistant pairs (system messages preserved).

    Returns:
        (trimmed_messages, total_tokens)
    """
    system = [m for m in messages if m.get("role") == "system"]
    non_system = [m for m in messages if m.get("role") != "system"]
    keep = max_history_length * 2  # pairs -> individual messages
    kept = non_system[-keep:] if len(non_system) > keep else non_system
    trimmed = system + kept
    return trimmed, count_tokens(trimmed)


class MessageTrimmer:
    """Trim a list of chat messages to fit within token or count constraints."""

    def __init__(self, max_tokens: int = 3000, max_messages: int = 20, min_messages: int = 2):
        """
        Args:
            max_tokens (int): Token budget for the trimmed history.
            max_messages (int): Hard cap on number of messages.
            min_messages (int): Minimum human/AI turns to always keep.
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.min_messages = min_messages

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def trim_by_count(self, messages: List[Dict], max_messages: int = None) -> List[Dict]:
        """
        Keep only the last max_messages messages.

        Args:
            messages (List[Dict]): Full history as list of {"role", "content"} dicts.
            max_messages (int): Override instance default.

        Returns:
            List[Dict]: Trimmed history.
        """
        limit = max_messages or self.max_messages
        system = [m for m in messages if m["role"] == "system"]
        non_system = [m for m in messages if m["role"] != "system"]
        kept = non_system[-limit:] if len(non_system) > limit else non_system
        return system + kept

    def trim_by_tokens(self, messages: List[Dict], max_tokens: int = None) -> List[Dict]:
        """
        Keep the most recent messages that fit within max_tokens.

        System messages are always kept and deducted from the budget first.

        Args:
            messages (List[Dict]): Full history.
            max_tokens (int): Override instance default.

        Returns:
            List[Dict]: Trimmed history.
        """
        budget = max_tokens or self.max_tokens
        system = [m for m in messages if m["role"] == "system"]
        non_system = [m for m in messages if m["role"] != "system"]

        used = sum(_msg_tokens(m) for m in system)
        kept = []
        for msg in reversed(non_system):
            cost = _msg_tokens(msg)
            if used + cost <= budget:
                kept.insert(0, msg)
                used += cost
            else:
                break

        return system + kept

    def smart_trim(self, messages: List[Dict], max_tokens: int = None, min_messages: int = None) -> List[Dict]:
        """
        Token-based trim that guarantees at least min_messages pairs are kept.

        Args:
            messages (List[Dict]): Full history.
            max_tokens (int): Override instance default.
            min_messages (int): Minimum pairs to preserve regardless of token budget.

        Returns:
            List[Dict]: Trimmed history.
        """
        budget = max_tokens or self.max_tokens
        min_keep = (min_messages or self.min_messages) * 2  # pairs → individual messages

        system = [m for m in messages if m["role"] == "system"]
        non_system = [m for m in messages if m["role"] != "system"]

        # Always keep at least min_keep messages
        guaranteed = non_system[-min_keep:] if len(non_system) > min_keep else non_system[:]
        remaining = non_system[: max(0, len(non_system) - min_keep)]

        used = sum(_msg_tokens(m) for m in system) + sum(_msg_tokens(m) for m in guaranteed)
        extra = []
        for msg in reversed(remaining):
            cost = _msg_tokens(msg)
            if used + cost <= budget:
                extra.insert(0, msg)
                used += cost
            else:
                break

        return system + extra + guaranteed

    def count_tokens(self, messages: List[Dict]) -> int:
        """Return the total token count for a list of messages."""
        return sum(_msg_tokens(m) for m in messages)


# ------------------------------------------------------------------
# CLI test
# ------------------------------------------------------------------

def _run_test():
    trimmer = MessageTrimmer(max_tokens=500, max_messages=6, min_messages=2)

    messages = [{"role": "system", "content": "You are a helpful RAG assistant."}]
    for i in range(1, 11):
        messages.append({"role": "user", "content": f"This is user message number {i} about machine learning concepts."})
        messages.append({"role": "assistant", "content": f"This is assistant reply number {i} explaining the concept in detail."})

    print(f"Original : {len(messages)} messages  /  ~{trimmer.count_tokens(messages)} tokens")

    by_count = trimmer.trim_by_count(messages)
    print(f"By count : {len(by_count)} messages  /  ~{trimmer.count_tokens(by_count)} tokens")

    by_tokens = trimmer.trim_by_tokens(messages)
    print(f"By tokens: {len(by_tokens)} messages  /  ~{trimmer.count_tokens(by_tokens)} tokens")

    smart = trimmer.smart_trim(messages)
    print(f"Smart    : {len(smart)} messages  /  ~{trimmer.count_tokens(smart)} tokens")
    print("Test passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test message trimming strategies")
    parser.add_argument("--test", action="store_true", help="Run trimming self-test")
    args = parser.parse_args()
    if args.test:
        _run_test()
    else:
        parser.print_help()
