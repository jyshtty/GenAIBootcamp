# chat history per session, timestamps, export and trim

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from message_trimming import trim_messages


_sessions: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> list of msgs
DEFAULT_EXPORT_DIR = "data/chat_sessions"


def add_message(session_id: str, role: str, content: str) -> None:
    # add one msg to session
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })


def get_messages(
    session_id: str,
    trim: bool = False,
    max_history_length: Optional[int] = None,
) -> List[Dict[str, Any]]:
    # get msgs for session, trim=True gives shorter list for llm
    messages = _sessions.get(session_id, [])
    if not trim:
        return messages
    simple = [{"role": m["role"], "content": m["content"]} for m in messages]
    trimmed_list, _ = trim_messages(
        simple,
        max_history_length=max_history_length,
    )
    return [{"role": m["role"], "content": m["content"]} for m in trimmed_list]


def clear_session(session_id: str) -> None:
    # wipe session
    _sessions[session_id] = []


def export_session(
    session_id: str,
    path: Optional[str] = None,
    format: str = "json",
) -> str:
    # write session to file, json or md. returns path
    messages = _sessions.get(session_id, [])
    export_dir = Path(DEFAULT_EXPORT_DIR)
    export_dir.mkdir(parents=True, exist_ok=True)
    if path is None:
        path = export_dir / f"session_{session_id}.{format}"
    else:
        path = Path(path)

    if format == "json":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"session_id": session_id, "messages": messages},
                f,
                ensure_ascii=False,
                indent=2,
            )
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# Chat session: {session_id}\n\n")
            for m in messages:
                role = m.get("role", "user")
                ts = m.get("timestamp", "")
                content = m.get("content", "")
                f.write(f"**{role}** ({ts})\n\n{content}\n\n")
    return str(path)


def get_session_ids() -> List[str]:
    # list of all session ids we know
    return list(_sessions.keys())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat history management")
    parser.add_argument("--export", metavar="SESSION_ID", help="Export session to data/chat_sessions/")
    parser.add_argument("--format", choices=["json", "md"], default="json", help="Export format")
    args = parser.parse_args()
    if args.export:
        out_path = export_session(args.export, format=args.format)
        print(f"Exported to {out_path}")
    else:
        print("Sessions:", get_session_ids())
        print("Use --export SESSION_ID to export a session.")
