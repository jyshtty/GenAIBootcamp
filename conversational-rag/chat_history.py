"""
Chat history management — stores, persists, and retrieves conversation sessions.

Sessions are saved as JSON files under data/chat_sessions/<session_id>.json.

Example usage:
    python chat_history.py --export my_session
"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Optional


SESSION_DIR = os.path.join("data", "chat_sessions")


class ChatHistoryManager:
    """Manage in-memory and on-disk chat sessions."""

    def __init__(self, session_dir: str = SESSION_DIR, max_history: int = 50):
        """
        Args:
            session_dir (str): Directory to persist session files.
            max_history (int): Maximum messages kept per session in memory.
        """
        self.session_dir = session_dir
        self.max_history = max_history
        self._sessions: Dict[str, List[Dict]] = {}

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def add_message(self, session_id: str, role: str, content: str):
        """
        Append a message to the session history.

        Args:
            session_id (str): Unique session identifier.
            role (str): "user" or "assistant".
            content (str): Message text.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        self._sessions[session_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Trim in-memory if over limit (keep most recent)
        if len(self._sessions[session_id]) > self.max_history:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> List[Dict]:
        """Return the full message history for a session."""
        return self._sessions.get(session_id, [])

    def get_langchain_messages(self, session_id: str) -> List[Dict]:
        """
        Return history formatted for LangChain / OpenAI (role + content only).

        Timestamps are stripped because the LLM API doesn't accept extra keys.
        """
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.get_history(session_id)
        ]

    def clear_session(self, session_id: str):
        """Remove all messages for a session from memory."""
        self._sessions.pop(session_id, None)

    def list_sessions(self) -> List[str]:
        """Return all active in-memory session IDs."""
        return list(self._sessions.keys())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_session(self, session_id: str):
        """Persist a session to disk as JSON."""
        os.makedirs(self.session_dir, exist_ok=True)
        path = os.path.join(self.session_dir, f"{session_id}.json")
        data = {
            "session_id": session_id,
            "saved_at": datetime.utcnow().isoformat(),
            "messages": self._sessions.get(session_id, []),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Session '{session_id}' saved to {path}")

    def load_session(self, session_id: str) -> bool:
        """
        Load a session from disk into memory.

        Returns:
            bool: True if loaded successfully, False if file not found.
        """
        path = os.path.join(self.session_dir, f"{session_id}.json")
        if not os.path.exists(path):
            return False
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._sessions[session_id] = data.get("messages", [])
        print(f"Session '{session_id}' loaded ({len(self._sessions[session_id])} messages).")
        return True

    def export_session(self, session_id: str, output_path: Optional[str] = None) -> str:
        """
        Export a session to a formatted text file.

        Returns:
            str: Path to the exported file.
        """
        os.makedirs(self.session_dir, exist_ok=True)
        output_path = output_path or os.path.join(self.session_dir, f"{session_id}_export.txt")
        history = self.get_history(session_id)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Chat Session: {session_id}\n")
            f.write("=" * 60 + "\n\n")
            for msg in history:
                ts = msg.get("timestamp", "")
                role = msg["role"].upper()
                f.write(f"[{ts}] {role}:\n{msg['content']}\n\n")
        print(f"Session exported to {output_path}")
        return output_path

    def get_session_stats(self, session_id: str) -> Dict:
        """Return basic statistics for a session."""
        history = self.get_history(session_id)
        user_msgs = [m for m in history if m["role"] == "user"]
        asst_msgs = [m for m in history if m["role"] == "assistant"]
        return {
            "session_id": session_id,
            "total_messages": len(history),
            "user_messages": len(user_msgs),
            "assistant_messages": len(asst_msgs),
        }


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat history management")
    parser.add_argument("--export", metavar="SESSION_ID", help="Export a session to text")
    parser.add_argument("--list", action="store_true", help="List saved sessions on disk")
    args = parser.parse_args()

    manager = ChatHistoryManager()

    if args.export:
        manager.load_session(args.export)
        manager.export_session(args.export)

    elif args.list:
        os.makedirs(SESSION_DIR, exist_ok=True)
        sessions = [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
        print("Saved sessions:", sessions if sessions else "(none)")

    else:
        parser.print_help()
