#!/usr/bin/env python3
"""
Importable agent core used by the API server. Wraps a single chat turn against
Ollama with a tool-calling loop, plus session state (per-client conversation +
rolling context).

This reuses the same tool functions as the standalone agent.py so behavior is
consistent between the terminal app and the server.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME = os.getenv("MODEL_NAME", "my-agent")
MAX_TOOL_STEPS = 8
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))

# Optional session log (server-side)
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))


# ---------------------------------------------------------------------------
# The tools live in the standalone agent.py. We import it as a module (its
# `if __name__ == "__main__"` guard keeps main() from running; heavy imports
# like rich/dotenv are already system-installed, and optional voice deps load
# only when the tools are invoked).
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent  # Model_Components/


def get_agent_tools() -> dict:
    import importlib.util
    import sys
    spec = importlib.util.spec_from_file_location("local_agent", str(ROOT / "agent.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["local_agent"] = mod
    spec.loader.exec_module(mod)

    tools = dict(mod.TOOLS)

    # Add SSH remote-control tools (laptop) from ssh_control, if configured.
    from . import ssh_control
    if ssh_control.is_configured():
        tools["ssh_shell"] = lambda args: ssh_control.remote_shell(args.get("cmd", ""))
        tools["ssh_read"] = lambda args: ssh_control.remote_read(args.get("path", ""))
        tools["ssh_write"] = lambda args: ssh_control.remote_write(args.get("path", ""), args.get("content", ""))
        tools["ssh_list"] = lambda args: ssh_control.remote_list(args.get("path", "~"))
    return tools


def _find_balanced_object(text: str, start: int):
    i = text.find("{", start)
    if i == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for j in range(i, len(text)):
        ch = text[j]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[i:j + 1], j
    return None


def try_parse_tool_call(text: str, tools: dict):
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].lstrip()
    start = 0
    while True:
        found = _find_balanced_object(stripped, start)
        if found is None:
            return None
        raw, _end = found
        start = _end + 1
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("tool") in tools:
            return obj
    return None


class AgentSession:
    """Per-client conversation with rolling context management."""

    def __init__(self, client_id: str = "default"):
        self.client_id = client_id
        self.messages: list[dict] = []
        self.tools = get_agent_tools()
        try:
            sys.path.insert(0, str(ROOT))
            from system_prompt import build_system_prompt
            self.messages.append({"role": "system", "content": build_system_prompt(str(ROOT))})
        except Exception:
            pass

    def _model_available(self) -> bool:
        try:
            requests.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=3)
            return True
        except Exception:
            return False

    def _call_model(self, messages) -> str:
        if not self._model_available():
            raise ConnectionError("Ollama is not reachable.")
        resp = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "messages": messages, "stream": False}, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    def _trim(self):
        if len(self.messages) <= MAX_CONTEXT_MESSAGES:
            return
        # Extract the standing system prompt (index 0) so it always survives.
        system_prompt = self.messages[0] if self.messages and self.messages[0].get("role") == "system" else {"role": "system", "content": "You are a local terminal agent."}
        body = self.messages[1:]
        overflow = body[: len(body) - MAX_CONTEXT_MESSAGES]
        kept = body[len(body) - MAX_CONTEXT_MESSAGES:]
        summary = " ".join(f"{m['role']}: {m['content']}" for m in overflow)[-6000:]
        self.messages[:] = [system_prompt] + [
            {"role": "system", "content": "{summary} Earlier context:\n" + summary}
        ] + kept

    def chat(self, user_text: str) -> str:
        """Run one user turn end-to-end and return the final reply."""
        self.messages.append({"role": "user", "content": user_text})
        self._trim()
        for _ in range(MAX_TOOL_STEPS):
            reply = self._call_model(self.messages)
            call = try_parse_tool_call(reply, self.tools)
            if call is None:
                self.messages.append({"role": "assistant", "content": reply})
                self._trim()
                self._log("reply", reply=reply)
                return reply
            name = call["tool"]
            args = call.get("args", {})
            if not isinstance(args, dict):
                args = {}
            self._log("tool_call", tool=name, args=json.dumps(args, default=str))
            try:
                result = self.tools[name](args)
            except Exception as e:
                result = {"error": str(e)}
            self._log("tool_result", tool=name, result=json.dumps(result, default=str)[:2000])
            self.messages.append({"role": "assistant", "content": reply})
            self.messages.append({"role": "user", "content": f"Tool result: {json.dumps(result, default=str)}"})
        return "Reached max tool steps for this turn without a final answer."

    def reset(self):
        self.messages = []

    def _log(self, event: str, **fields):
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            path = LOG_DIR / f"server-{datetime.now().strftime('%Y%m%d')}.jsonl"
            payload = {"ts": datetime.now().isoformat(), "client": self.client_id, "event": event}
            payload.update(fields)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
        except OSError:
            pass