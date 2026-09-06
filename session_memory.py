#!/usr/bin/env python3
"""
Session memory + history search.

Lets the agent look back across ALL of its past conversations (terminal + server
logs in logs/) and find where a word/phrase was written, then continue based on
that context. Complements the RAG knowledge base (knowledge.py), which holds
curated/researched docs; this searches organic conversation history.

Events we index (from agent.py's log_event / server logs, all JSONL):
    user_input     — what you typed/said
    agent_reply    — what the agent answered
    tool_call      — which tool + args
    tool_result    — what the tool returned
    session_start / session_end — boundaries

Search is keyword based (regex over the raw lines) since we keep it dependency
free and offline. Returns the matching lines with their session file + timestamp
so the agent (or you) can tell exactly where it appeared.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))

# Event types we treat as "conversation text worth searching".
_TEXT_EVENTS = {"user_input", "agent_reply", "tool_call", "tool_result", "reply"}


def _iter_log_records(limit_sessions: int = 50):
    """Yield (record, filename) for every JSONL record across session + server logs."""
    files = sorted(LOG_DIR.glob("session-*.jsonl")) + sorted(LOG_DIR.glob("server-*.jsonl"))
    for f in files[:limit_sessions]:
        try:
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                yield rec, f.name
        except OSError:
            continue


def search_history(query: str, event: str = "any", k: int = 10) -> dict:
    """Search all past sessions for `query` (a word or phrase). Returns the
    matching lines with their session file and timestamp."""
    if not query or not query.strip():
        return {"error": "Provide a word or phrase to search for."}
    q = query.strip().lower()
    tokens = re.findall(r"[a-z0-9']+", q)
    k = int(k)

    matches: list[dict] = []
    for rec, fname in _iter_log_records():
        ev = rec.get("event", "")
        if event != "any" and ev != event:
            continue
        payload = rec.get("reply") or rec.get("input") or rec.get("tool") or rec.get("result") or rec.get("args") or ""
        if not isinstance(payload, str):
            payload = json.dumps(payload, default=str)
        hay = (payload.lower())
        # Require a full-phrase hit if more than one word, else any-word match.
        if len(tokens) > 1:
            hit = q in hay
        else:
            hit = tokens[0] in hay
        if not hit:
            continue
        matches.append({
            "session": fname,
            "ts": rec.get("ts", ""),
            "event": ev,
            "text": payload[:500],
        })

    # Newest-first, cap at k.
    matches.sort(key=lambda m: m["ts"], reverse=True)
    return {"query": query, "matches": matches[:k], "count": len(matches)}


def list_sessions() -> dict:
    """Return the list of session logs with timestamp ranges so the agent can
    tell how many conversations it has and roughly what was discussed."""
    sessions = []
    for f in sorted(LOG_DIR.glob("session-*.jsonl"), key=os.path.getmtime, reverse=True) + \
             sorted(LOG_DIR.glob("server-*.jsonl"), key=os.path.getmtime, reverse=True):
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size = f.stat().st_size
        sessions.append({"file": f.name, "last_modified": mtime, "lines": size and "~" + str(max(1, size // 100))})
    return {"sessions": sessions, "log_dir": str(LOG_DIR)}


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "search":
        import json as _json
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        print(_json.dumps(search_history(q), indent=2, default=str))
    else:
        import json as _json
        print(_json.dumps(list_sessions(), indent=2, default=str))