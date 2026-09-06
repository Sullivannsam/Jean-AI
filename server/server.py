#!/usr/bin/env python3
"""
Personal AI server.

Runs the agent as an HTTP/API service bound to your local network (set
SERVER_BIND=0.0.0.0) so another machine (e.g. your laptop) can reach it. All
requests must carry an auth token (SERVER_TOKEN). Voice + Home Assistant +
laptop control all run here.

Endpoints:
    GET  /api/health          status of every subsystem
    POST /api/chat            {"text": "..."} -> {"reply": "..."}
    POST /api/stt             audio bytes in body -> {"text": "..."}
    POST /api/tts             {"text": "..."} -> wav audio (text/plain octet)
    POST /api/reset           reset this client's conversation

Auth: header `Authorization: Bearer <SERVER_TOKEN>` on every request.

Run with systemd (see systemd/jarvis-server.service) or manually:
    python3 server/server.py
"""
import argparse
import os
import sys
from pathlib import Path

# Make the parent dir (Model_Components/) importable so `server.*` resolves
# whether we run as `python3 -m server.server` or `python3 server/server.py`.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiohttp import web
from dotenv import load_dotenv

from server import ssh_control, voice
from server.agent_core import AgentSession

load_dotenv()

SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")  # 0.0.0.0 = reachable on LAN
SERVER_PORT = int(os.getenv("SERVER_PORT", "8899"))
SERVER_TOKEN = os.getenv("SERVER_TOKEN", "")
HA_URL = os.getenv("HA_URL", "")
HA_TOKEN = os.getenv("HA_TOKEN", "")
MODEL_NAME = os.getenv("MODEL_NAME", "my-agent")

_sessions: dict[str, AgentSession] = {}


def _get_session(client_id: str) -> AgentSession:
    if client_id not in _sessions:
        _sessions[client_id] = AgentSession(client_id)
    return _sessions[client_id]


def _authorized(request: web.Request) -> bool:
    if not SERVER_TOKEN:
        return True  # token not set -> open (dangerous; warn at startup)
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {SERVER_TOKEN}"


def _reject() -> web.Response:
    return web.json_response({"error": "Unauthorized. Provide Authorization: Bearer <SERVER_TOKEN>."}, status=401)


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

async def handle_health(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _reject()
    payload = {
        "agent_model": MODEL_NAME,
        "home_assistant": bool(HA_URL and HA_TOKEN),
        "ssh_laptop": ssh_control.is_configured(),
        "tts": bool(voice.PIPER_MODEL and Path(voice.PIPER_MODEL).exists()),
        "stt": True,  # faster-whisper loads on first use
    }
    return web.json_response(payload)


async def handle_chat(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _reject()
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Expected a JSON body with a 'text' field."}, status=400)
    text = (body.get("text") or "").strip()
    if not text:
        return web.json_response({"error": "Missing 'text'."}, status=400)
    client_id = body.get("client_id", "default")
    session = _get_session(client_id)
    try:
        reply = session.chat(text)
    except ConnectionError as e:
        return web.json_response({"error": f"Model backend unavailable: {e}"}, status=503)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
    return web.json_response({"reply": reply})


async def handle_stt(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _reject()
    audio = await request.read()
    if not audio:
        return web.json_response({"error": "No audio in body."}, status=400)
    try:
        text = voice.transcribe_bytes(audio)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
    return web.json_response({"text": text})


async def handle_tts(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _reject()
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Expected a JSON body with a 'text' field."}, status=400)
    text = (body.get("text") or "").strip()
    if not text:
        return web.json_response({"error": "Missing 'text'."}, status=400)
    wav = voice.synthesize(text)
    if not wav:
        return web.json_response({"error": "TTS not configured (set PIPER_MODEL)."}, status=501)
    return web.Response(body=wav, content_type="audio/wav")


async def handle_reset(request: web.Request) -> web.Response:
    if not _authorized(request):
        return _reject()
    client_id = (await request.json()).get("client_id", "default") if request.has_body else "default"
    _get_session(client_id).reset()
    return web.json_response({"status": "reset"})


async def handle_root(request: web.Request) -> web.Response:
    return web.Response(
        text="Personal AI server is running.\n"
             "Endpoints: /api/health, /api/chat, /api/stt, /api/tts, /api/reset\n"
             "Requests need header: Authorization: Bearer <SERVER_TOKEN>\n",
        content_type="text/plain",
    )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=SERVER_HOST)
    parser.add_argument("--port", type=int, default=SERVER_PORT)
    args = parser.parse_args()

    if not SERVER_TOKEN:
        print("WARNING: SERVER_TOKEN is not set in .env — the API will accept "
              "ALL requests. Generate one with: python3 -c \"import secrets;print(secrets.token_urlsafe(32))\"")
    if args.host in ("0.0.0.0", "::"):
        print(f"Serving on LAN at http://{args.host}:{args.port} — reachable by other machines on this network.")

    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/api/health", handle_health)
    app.router.add_post("/api/chat", handle_chat)
    app.router.add_post("/api/stt", handle_stt)
    app.router.add_post("/api/tts", handle_tts)
    app.router.add_post("/api/reset", handle_reset)

    print(f"Personal AI server listening on {args.host}:{args.port}")
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()