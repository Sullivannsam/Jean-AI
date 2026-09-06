#!/usr/bin/env python3
"""
Local terminal AI agent — talks to a model served by Ollama (fully local),
can run shell commands, read/write files, and control smart home devices via
Home Assistant. Optional voice mode: talk to it and hear it talk back,
fully offline (faster-whisper for listening, piper for speaking).

Professional features: conversation context window + rolling summary, session
logging, startup config validation, a `--status` health check, shell command
allow/denylist, command history, and rendered markdown output.

Requirements: see requirements.txt

Setup:
    1. Install Ollama, pull a base model, build the agent model (see README.md)
    2. Copy config.example.env to .env and fill in your Home Assistant token
       (and piper paths if you want voice mode)
    3. Run text mode:   python3 agent.py
       Run voice mode:  python3 agent.py --voice
    4. Health check:    python3 agent.py --status
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

load_dotenv()
console = Console()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL_NAME = os.getenv("MODEL_NAME", "my-agent")
MAX_TOOL_STEPS = int(os.getenv("MAX_TOOL_STEPS", "8"))
WORKDIR_SCOPE = Path.cwd()

# How long Ollama should keep the model loaded in RAM between calls. Without
# this, Ollama's default (5 min) can unload the model between turns in a slow
# back-and-forth conversation, forcing a multi-second reload on the next
# message. "-1" keeps it loaded indefinitely (fine for a dedicated box).
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "10m")
# Read timeout for a single Ollama call — generous by default since CPU-only
# inference can take a while on longer replies.
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))
# Retries for transient connection/timeout failures only (never for a reply
# Ollama actually returned) — covers brief hiccups like Ollama still starting.
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "2"))

# Shared session: reuses TCP connections to Ollama/Home Assistant instead of
# opening a new one on every request, and centralizes retry policy for
# connection-level failures (DNS hiccup, connection refused, etc.) so a
# flaky moment doesn't kill an otherwise-working turn.
_session = requests.Session()
_retry = requests.adapters.Retry(
    total=2,
    connect=2,
    read=0,  # read/timeout retries are handled explicitly in call_model
    backoff_factor=0.5,
    status_forcelist=(502, 503, 504),
    allowed_methods=frozenset(["GET", "POST"]),
)
_adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=_retry)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

# Conversation context management
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))  # rolling window
SUMMARY_PROMPT = "Briefly summarize our conversation so far, keeping any user preferences. Return only the summary."

# Session logging
LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
SESSION_LOG = None

HA_URL = os.getenv("HA_URL", "").rstrip("/")
HA_TOKEN = os.getenv("HA_TOKEN", "")
HA_REQUIRE_CONFIRM = os.getenv("HA_REQUIRE_CONFIRM", "true").lower() == "true"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
RECORD_SECONDS = int(os.getenv("RECORD_SECONDS", "5"))
CONFIRM_RECORD_SECONDS = int(os.getenv("CONFIRM_RECORD_SECONDS", "3"))
# If `sox` is installed, recording auto-stops this many seconds after you stop
# talking instead of always waiting the full RECORD_SECONDS — cuts wasted
# waiting on short commands. Threshold is sox's silence-detection sensitivity
# (higher % = requires quieter silence to trigger a stop).
SILENCE_DURATION = os.getenv("SILENCE_DURATION", "1.2")
SILENCE_THRESHOLD = os.getenv("SILENCE_THRESHOLD", "3%")
PIPER_BINARY = os.getenv("PIPER_BINARY", "piper")
PIPER_MODEL = os.getenv("PIPER_MODEL", "")

# Whisper tuning for non-native/accented English. Forcing the language stops
# Whisper from ever mis-guessing the spoken language from an accent (its
# auto-detect only looks at the first ~30s and can flip languages mid-guess
# on accented speech, producing garbage). A higher beam_size searches more
# candidate transcriptions before picking one — slower but more accurate.
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
WHISPER_VAD_FILTER = os.getenv("WHISPER_VAD_FILTER", "true").lower() == "true"

# Optional friendly device map: "living room light" -> "light.living_room".
# The model consults this as a hint before hitting Home Assistant live.
HA_ENTITY_MAP = {}
_HA_MAP_RAW = os.getenv("HA_ENTITY_MAP", "")
if _HA_MAP_RAW.strip():
    for _entry in _HA_MAP_RAW.split(","):
        if "=" in _entry:
            _k, _v = _entry.split("=", 1)
            HA_ENTITY_MAP[_k.strip().lower()] = _v.strip()

# Vision (optional) — only enabled when VISION_MODEL points at a vision-capable
# model you've pulled in Ollama (e.g. qwen2.5vl, llava).
VISION_MODEL = os.getenv("VISION_MODEL", "").strip()
VISION_ENABLED = bool(VISION_MODEL)

WAKEWORD_MODEL = os.getenv("WAKEWORD_MODEL", "hey_jarvis")  # openWakeWord ships a few pretrained ones
WAKEWORD_THRESHOLD = float(os.getenv("WAKEWORD_THRESHOLD", "0.5"))

# If true, skip confirmation entirely in voice/wake mode (no "yes" needed at all —
# it just does whatever you ask, immediately). Off by default: see the safety
# note in README before turning this on.
SKIP_CONFIRM_IN_VOICE = os.getenv("SKIP_CONFIRM_IN_VOICE", "false").lower() == "true"

# --- Shell command policy ----------------------------------------------------
# Commands are checked against an allowlist first (pure + common safe commands
# run immediately-ish), then a denylist (never allowed without explicit note),
# and anything else falls through to the normal confirmation prompt.
SHELL_ALLOWLIST = set(os.getenv("SHELL_ALLOWLIST", "ls,pwd,whoami,date,uptime,echo,cat,head,tail,wc,git status").split(","))
SHELL_DENYLIST = set(os.getenv("SHELL_DENYLIST", "rm,dd,mkfs,chmod,chown,shutdown,reboot,halt,sudo,su,mount,umount,fdisk,parted,>").split(","))
SHELL_ALLOWLIST = {s.strip() for s in SHELL_ALLOWLIST if s.strip()}
SHELL_DENYLIST = {s.strip() for s in SHELL_DENYLIST if s.strip()}

# Set to True when running in --voice or --wake mode, so confirmations happen
# by voice instead of by typing.
VOICE_MODE_ACTIVE = False


# ---------------------------------------------------------------------------
# Session logging (secrets are redacted before writing)
# ---------------------------------------------------------------------------

_SENSITIVE_KEYS = ("HA_TOKEN", "PIPER_BINARY", "PIPER_MODEL")
SESSION_LOG_ACTIVE = False


def setup_logging() -> None:
    global SESSION_LOG_ACTIVE
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        global SESSION_LOG
        SESSION_LOG = LOG_DIR / f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl"
        SESSION_LOG_ACTIVE = True
    except OSError as e:
        console.print(f"[dim](session logging disabled: {e})[/dim]")


def _redact(value: str) -> str:
    """Replace sensitive values in a string with *** to avoid leaking secrets to logs."""
    for key in _SENSITIVE_KEYS:
        raw = os.getenv(key)
        if raw:
            value = value.replace(raw, "***")
    if HA_TOKEN:
        value = value.replace(HA_TOKEN, "***")
    return value


def log_event(event: str, **fields) -> None:
    """Append one JSON record to the session log (secrets redacted)."""
    if not SESSION_LOG_ACTIVE:
        return
    payload = {"ts": datetime.now().isoformat(), "event": event}
    for k, v in fields.items():
        payload[k] = _redact(str(v)) if isinstance(v, str) else v
    try:
        with open(SESSION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Startup config validation
# ---------------------------------------------------------------------------

def validate_config() -> list[str]:
    """Return a list of human-readable warnings for missing/broken config."""
    warnings: list[str] = []
    if not Path(".env").exists():
        warnings.append("No .env file — copy config.example.env to .env.")

    # Ollama reachability
    try:
        _session.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=3)
    except Exception:
        warnings.append(f"Could not reach Ollama at {OLLAMA_URL}. Is it running?")

    if not HA_URL or not HA_TOKEN:
        warnings.append("Home Assistant not configured — set HA_URL/HA_TOKEN in .env to enable device control.")
    elif not (HA_URL.startswith("http://") or HA_URL.startswith("https://")):
        warnings.append("HA_URL does not start with http:// or https://.")

    if voice_enabled() and not PIPER_MODEL:
        warnings.append("PIPER_MODEL not set — voice output disabled.")

    if VISION_ENABLED and not VisionAvailable():
        warnings.append(f"VISION_MODEL='{VISION_MODEL}' set but this model is not available in Ollama.")

    return warnings


def voice_enabled() -> bool:
    return any(os.getenv(k) for k in ("PIPER_MODEL", "WHISPER_MODEL", "RECORD_SECONDS"))


def VisionAvailable() -> bool:
    try:
        resp = _session.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=3)
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        return any(VISION_MODEL in m for m in models)
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Confirmation helpers
# ---------------------------------------------------------------------------

def confirm_action(prompt: str) -> bool:
    """Ask for confirmation — by voice (speak + listen) if in voice/wake mode,
    otherwise by typing, unless SKIP_CONFIRM_IN_VOICE is on."""
    if VOICE_MODE_ACTIVE:
        if SKIP_CONFIRM_IN_VOICE:
            return True
        speak(f"{prompt} Say yes or no.")
        console.print(f"[cyan]{prompt} — listening for yes/no...[/cyan]")
        response = listen(record_seconds=CONFIRM_RECORD_SECONDS)
        return response.strip().lower().startswith(("yes", "yeah", "yep", "sure", "confirm", "go ahead", "do it"))
    return Confirm.ask(prompt, default=False)


# ---------------------------------------------------------------------------
# Shell / file tools
# ---------------------------------------------------------------------------

def _in_scope(path_str: str) -> Path:
    p = (WORKDIR_SCOPE / path_str).resolve()
    if not str(p).startswith(str(WORKDIR_SCOPE.resolve())):
        raise PermissionError(f"Path '{path_str}' is outside the allowed working directory.")
    return p


def _classify_command(cmd: str) -> str:
    """Return 'allow', 'deny', or 'unknown' for a shell command based on the
    allow/deny lists. Uses the first whitespace-delimited token."""
    first = cmd.strip().split()[0] if cmd.strip() else ""
    if first in SHELL_ALLOWLIST:
        return "allow"
    if first in SHELL_DENYLIST:
        return "deny"
    return "unknown"


def run_shell(cmd: str) -> dict:
    classification = _classify_command(cmd)
    comment = ""
    if classification == "deny":
        console.print("[bold red]This command is on your denylist and won't be run.[/bold red]")
        return {"stdout": "", "stderr": f"Command '{cmd}' blocked by denylist.", "exit_code": -2}
    if classification == "allow":
        comment = "[green]safe command (allowlist)[/green]"
    else:
        comment = "[yellow]not on allowlist[/yellow]"
    console.print(Panel(cmd, title=f"[yellow]Proposed shell command — {comment}[/yellow]", border_style="yellow"))
    if classification == "unknown" and not confirm_action("Run this command?"):
        return {"stdout": "", "stderr": "User declined to run this command.", "exit_code": -1}
    log_event("shell", cmd=cmd, classification=classification)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=WORKDIR_SCOPE)
        return {"stdout": result.stdout[-4000:], "stderr": result.stderr[-2000:], "exit_code": result.returncode}
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out after 30s.", "exit_code": -1}


def read_file(path: str) -> dict:
    try:
        return {"content": _in_scope(path).read_text()[-8000:]}
    except Exception as e:
        return {"error": str(e)}


def write_file(path: str, content: str) -> dict:
    try:
        p = _in_scope(path)
        console.print(Panel(f"{path}\n\n{content[:500]}", title="[yellow]Proposed file write[/yellow]", border_style="yellow"))
        if not confirm_action(f"Write to {path}?"):
            return {"error": "User declined to write this file."}
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
        log_event("file_write", path=str(p))
        return {"status": "written", "path": str(p)}
    except Exception as e:
        return {"error": str(e)}


def list_dir(path: str = ".") -> dict:
    try:
        p = _in_scope(path)
        return {"entries": sorted(str(x.relative_to(p)) + ("/" if x.is_dir() else "") for x in p.iterdir())}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Home Assistant tools
# ---------------------------------------------------------------------------

def _ha_headers() -> dict:
    return {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}


def _ha_confirm(action_desc: str) -> bool:
    console.print(Panel(action_desc, title="[yellow]Home Assistant action[/yellow]", border_style="yellow"))
    if not HA_REQUIRE_CONFIRM:
        return True
    return confirm_action("Do this?")


def _ha_call_service(domain: str, service: str, entity_id: str, extra: dict | None = None) -> dict:
    if not HA_URL or not HA_TOKEN:
        return {"error": "HA_URL / HA_TOKEN not set. Copy config.example.env to .env and fill them in."}
    payload = {"entity_id": entity_id, **(extra or {})}
    try:
        resp = _session.post(f"{HA_URL}/api/services/{domain}/{service}", headers=_ha_headers(), json=payload, timeout=10)
        resp.raise_for_status()
        return {"status": "ok", "result": resp.json()}
    except Exception as e:
        return {"error": str(e)}


def ha_turn_on_silent(entity_id: str) -> dict:
    """Turn on a device with no confirmation prompt — for automations like
    presence detection, where waiting for a 'yes' defeats the purpose."""
    domain = entity_id.split(".")[0]
    return _ha_call_service(domain, "turn_on", entity_id)


def ha_turn_on(entity_id: str) -> dict:
    if not _ha_confirm(f"Turn ON {entity_id}"):
        return {"error": "User declined."}
    domain = entity_id.split(".")[0]
    return _ha_call_service(domain, "turn_on", entity_id)


def ha_turn_off(entity_id: str) -> dict:
    if not _ha_confirm(f"Turn OFF {entity_id}"):
        return {"error": "User declined."}
    domain = entity_id.split(".")[0]
    return _ha_call_service(domain, "turn_off", entity_id)


def ha_set_temperature(entity_id: str, temperature: float) -> dict:
    if not _ha_confirm(f"Set {entity_id} temperature to {temperature}"):
        return {"error": "User declined."}
    return _ha_call_service("climate", "set_temperature", entity_id, {"temperature": temperature})


def ha_get_state(entity_id: str) -> dict:
    if not HA_URL or not HA_TOKEN:
        return {"error": "HA_URL / HA_TOKEN not set."}
    try:
        resp = _session.get(f"{HA_URL}/api/states/{entity_id}", headers=_ha_headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def ha_list_entities(domain: str = "") -> dict:
    if not HA_URL or not HA_TOKEN:
        return {"error": "HA_URL / HA_TOKEN not set."}
    try:
        resp = _session.get(f"{HA_URL}/api/states", headers=_ha_headers(), timeout=10)
        resp.raise_for_status()
        states = resp.json()
        entities = []
        for s in states:
            eid = s.get("entity_id", "")
            if domain and not eid.startswith(domain + "."):
                continue
            name = s.get("attributes", {}).get("friendly_name") or eid
            entities.append({"id": eid, "name": name})
        entities = entities[:100]
        return {"entities": entities}
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Memory (persistent across sessions) and vision (optional)
# ---------------------------------------------------------------------------

def remember(key: str, value: str) -> dict:
    try:
        from memory import remember_fact
        remember_fact(key, value)
        log_event("remember", key=key)
        return {"status": "remembered", "key": key, "value": value}
    except Exception as e:
        return {"error": str(e)}


def recall() -> dict:
    try:
        from memory import recall_facts
        return {"facts": recall_facts()}
    except Exception as e:
        return {"error": str(e)}


def describe_scene(prompt: str = "Describe what you see in this image.") -> dict:
    if not VISION_ENABLED:
        return {"error": "Vision is not enabled. Set VISION_MODEL in .env to a vision-capable Ollama model (e.g. qwen2.5vl, llava)."}
    try:
        from vision import describe_scene as _ds
        return {"description": _ds(prompt)}
    except Exception as e:
        return {"error": str(e)}


def kb_search(query: str, k: int = 3) -> dict:
    try:
        from knowledge import kb_search as _s
        return _s(query, k)
    except Exception as e:
        return {"error": str(e)}


def kb_ingest(path: str | None = None) -> dict:
    try:
        from knowledge import kb_ingest as _i
        return _i(path)
    except Exception as e:
        return {"error": str(e)}


def kb_stats() -> dict:
    try:
        from knowledge import kb_stats as _st
        return {"knowledge": _st()["knowledge"]}
    except Exception as e:
        return {"error": str(e)}


def research(topic: str, urls: list | None = None) -> dict:
    try:
        from research_agent import research as _r
        return _r(topic, urls)
    except Exception as e:
        return {"error": str(e)}


def search_history(query: str, k: int = 10) -> dict:
    try:
        from session_memory import search_history as _sh
        return _sh(query, k=k)
    except Exception as e:
        return {"error": str(e)}


def list_sessions() -> dict:
    try:
        from session_memory import list_sessions as _ls
        return _ls()
    except Exception as e:
        return {"error": str(e)}


TOOLS = {
    "run_shell": lambda args: run_shell(args.get("cmd", "")),
    "read_file": lambda args: read_file(args.get("path", "")),
    "write_file": lambda args: write_file(args.get("path", ""), args.get("content", "")),
    "list_dir": lambda args: list_dir(args.get("path", ".")),
    "ha_turn_on": lambda args: ha_turn_on(args.get("entity_id", "")),
    "ha_turn_off": lambda args: ha_turn_off(args.get("entity_id", "")),
    "ha_set_temperature": lambda args: ha_set_temperature(args.get("entity_id", ""), args.get("temperature")),
    "ha_get_state": lambda args: ha_get_state(args.get("entity_id", "")),
    "ha_list_entities": lambda args: ha_list_entities(args.get("domain", "")),
    "remember": lambda args: remember(args.get("key", ""), args.get("value", "")),
    "recall": lambda args: recall(),
    "describe_scene": lambda args: describe_scene(args.get("prompt", "Describe what you see in this image.")),
    "kb_search": lambda args: kb_search(args.get("query", ""), args.get("k", 3)),
    "kb_ingest": lambda args: kb_ingest(args.get("path")),
    "kb_stats": lambda args: kb_stats(),
    "research": lambda args: research(args.get("topic", ""), args.get("urls")),
    "search_history": lambda args: search_history(args.get("query", ""), args.get("k", 10)),
    "list_sessions": lambda args: list_sessions(),
}


# ---------------------------------------------------------------------------
# Voice: listen (arecord + faster-whisper) and speak (piper + aplay)
# ---------------------------------------------------------------------------

_whisper_model = None


def _whisper_vocab_hint() -> str | None:
    """Build a short phrase of known device names/commands to prime Whisper
    toward the right vocabulary. Whisper uses `initial_prompt` as a style/
    vocabulary hint — this doesn't force a transcription, but it noticeably
    helps it land on domain words (device names, entity ids) instead of the
    nearest-sounding English word, especially with an accent."""
    words = list(HA_ENTITY_MAP.keys())
    if not words:
        return None
    return "Devices: " + ", ".join(words) + "."


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        console.print(f"[dim]Loading whisper model '{WHISPER_MODEL}'...[/dim]")
        _whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper_model


def _record_with_silence_cutoff(wav_path: str, max_seconds: int) -> bool:
    """Record via sox's `rec`, auto-stopping once you stop talking instead of
    always waiting the full max duration. Returns False (caller should fall
    back to fixed-duration arecord) if `sox` isn't installed — this is a pure
    speed optimization, not a hard requirement."""
    if shutil.which("rec") is None:
        return False
    try:
        subprocess.run(
            [
                "rec", "-q", "-r", "16000", "-c", "1", wav_path,
                "silence", "1", "0.1", SILENCE_THRESHOLD,
                "1", str(SILENCE_DURATION), SILENCE_THRESHOLD,
            ],
            check=True, capture_output=True, timeout=max_seconds + 2,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def listen(record_seconds: int | None = None) -> str:
    """Record audio from the default mic, transcribe with faster-whisper.
    `record_seconds` overrides the global RECORD_SECONDS (used for short
    yes/no) and also acts as the max duration when silence-cutoff recording
    is available (via `sox`) — recording stops as soon as you stop talking
    instead of always waiting the full duration."""
    if record_seconds is None:
        record_seconds = RECORD_SECONDS
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        console.print(f"[cyan]Listening (up to {record_seconds}s)...[/cyan] (speak now)")
        if not _record_with_silence_cutoff(wav_path, record_seconds):
            try:
                subprocess.run(
                    ["arecord", "-d", str(record_seconds), "-f", "cd", "-t", "wav", wav_path],
                    check=True, capture_output=True,
                )
            except FileNotFoundError:
                console.print("[bold red]'arecord' not found.[/bold red] Install it: sudo apt install alsa-utils")
                return ""
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Recording failed:[/bold red] {e.stderr.decode(errors='ignore')}")
                return ""

        model = _get_whisper_model()
        segments, _ = model.transcribe(
            wav_path,
            language=WHISPER_LANGUAGE,
            beam_size=WHISPER_BEAM_SIZE,
            vad_filter=WHISPER_VAD_FILTER,
            initial_prompt=_whisper_vocab_hint(),
        )
        text = " ".join(seg.text.strip() for seg in segments)
        console.print(f"[bold blue]you (voice)>[/bold blue] {text}")
        return text.strip()
    finally:
        if wav_path and Path(wav_path).exists():
            try:
                os.unlink(wav_path)
            except OSError:
                pass


def speak(text: str) -> None:
    """Synthesize speech with piper and play it with aplay."""
    if not PIPER_MODEL or not Path(PIPER_MODEL).exists():
        console.print("[dim](voice output skipped — PIPER_MODEL not set or file not found; see config.example.env)[/dim]")
        return
    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name
        try:
            subprocess.run(
                [PIPER_BINARY, "--model", PIPER_MODEL, "--output_file", wav_path],
                input=text, text=True, check=True, capture_output=True,
            )
            subprocess.run(["aplay", wav_path], check=True, capture_output=True)
        except FileNotFoundError:
            console.print(f"[bold red]'{PIPER_BINARY}' or 'aplay' not found.[/bold red] Install piper and alsa-utils.")
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]Speech failed:[/bold red] {e.stderr.decode(errors='ignore') if e.stderr else e}")
    finally:
        if wav_path and Path(wav_path).exists():
            try:
                os.unlink(wav_path)
            except OSError:
                pass


def run_wake_word_loop() -> None:
    """Always-on mode: no Enter key needed. Say the wake word, then your
    command, and it responds by voice. Runs until Ctrl+C."""
    global VOICE_MODE_ACTIVE
    VOICE_MODE_ACTIVE = True

    import numpy as np
    import sounddevice as sd
    from openwakeword.model import Model as WakeModel

    console.print(f"[dim]Loading wake word model '{WAKEWORD_MODEL}'...[/dim]")
    oww_model = WakeModel(wakeword_models=[WAKEWORD_MODEL])
    console.print(f"[bold green]Listening for wake word '{WAKEWORD_MODEL}'...[/bold green] (Ctrl+C to stop)\n")

    CHUNK = 1280  # openWakeWord expects 16kHz mono, ~80ms chunks
    messages: list[dict] = []

    def audio_callback(indata, frames, time_info, status):
        audio = np.frombuffer(bytes(indata), dtype=np.int16)
        prediction = oww_model.predict(audio)
        for wakeword, score in prediction.items():
            if score > WAKEWORD_THRESHOLD:
                raise sd.CallbackStop()

    while True:
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=CHUNK, dtype="int16", channels=1, callback=audio_callback):
                sd.sleep(10 ** 7)
        except sd.CallbackStop:
            pass
        except KeyboardInterrupt:
            break

        console.print("[cyan]Wake word heard — go ahead[/cyan]")
        user_input = listen()
        # Ignore degenerate transcriptions (silence/single characters) to avoid
        # looping on the wake word itself or room noise.
        if not user_input or len(user_input.strip()) < 2:
            console.print("[dim](nothing clear heard, back to listening)[/dim]")
            continue
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})
        answer = run_agent_turn(messages)
        messages.append({"role": "assistant", "content": answer})
        console.print(Panel(answer, title="agent", border_style="green"))
        speak(answer)
        # Small debounce so lingering wake-word audio doesn't immediately retrigger.
        time.sleep(1.5)


# ---------------------------------------------------------------------------
# Model communication + agent loop (with context window + offline handling)
# ---------------------------------------------------------------------------

def _model_available() -> bool:
    try:
        _session.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=3)
        return True
    except Exception:
        return False


def call_model(messages: list[dict]) -> str:
    """Call Ollama. Raises a friendly error if unreachable, so the caller can
    show a useful message instead of a stack trace.

    Previously this did a separate GET to /api/tags before every single call
    to check reachability, then made the real POST — doubling round-trips on
    every turn for no benefit (the POST fails the same way if Ollama is down).
    It also meant a slow-to-load model could look "unreachable" during the
    3s-timeout ping even though Ollama itself was fine. Now we just try the
    real call, and retry a couple of times with backoff if it's a transient
    connection/timeout issue (e.g. Ollama still starting up)."""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "keep_alive": OLLAMA_KEEP_ALIVE,
    }
    last_err: Exception | None = None
    for attempt in range(OLLAMA_MAX_RETRIES + 1):
        try:
            resp = _session.post(OLLAMA_URL, json=payload, timeout=(5, OLLAMA_TIMEOUT))
            resp.raise_for_status()
            try:
                return resp.json()["message"]["content"]
            except (KeyError, ValueError) as e:
                raise RuntimeError(f"Unexpected response from Ollama: {e}") from e
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_err = e
            if attempt < OLLAMA_MAX_RETRIES:
                wait = 0.5 * (2 ** attempt)
                log_event("ollama_retry", attempt=attempt + 1, error=str(e))
                time.sleep(wait)
                continue
    raise ConnectionError(f"Ollama unreachable after {OLLAMA_MAX_RETRIES + 1} attempt(s): {last_err}")


def _trim_context(messages: list[dict]) -> None:
    """Keep a rolling window of recent messages plus any summary at the front.
    When it exceeds MAX_CONTEXT_MESSAGES, collapse the oldest ones into a short
    summary so long sessions stay fast without losing key preferences."""
    if len(messages) <= MAX_CONTEXT_MESSAGES:
        return
    # Always keep the standing system prompt (index 0) so tools survive.
    system_prompt = messages[0] if messages and messages[0].get("role") == "system" else None
    head_idx = 1 if system_prompt is not None else 0
    window = messages[head_idx:]
    # Drop a prior {summary} message inside the body if present.
    if window and window[0].get("content", "").startswith("{summary}"):
        window = window[1:]
    overflow = window[: len(window) - MAX_CONTEXT_MESSAGES]
    kept = window[len(window) - MAX_CONTEXT_MESSAGES:]

    summary = " ".join(f"{m['role']}: {m['content']}" for m in overflow)[-6000:]
    new_head = [] if system_prompt is None else [system_prompt]
    messages[:] = new_head + [
        {"role": "system", "content": "{summary} Earlier context:\n" + summary}
    ] + kept


def _find_balanced_object(text: str, start: int) -> tuple[str, int] | None:
    """Scan text from `start` for the first balanced JSON object and return
    (raw_slice, index_of_closing_brace), or None if no balanced object is found."""
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


def try_parse_tool_call(text: str) -> dict | None:
    """Extract a tool call from the model's reply, tolerating markdown code
    fences, leading/trailing prose, and surplus whitespace. Returns the parsed
    object only if it names a tool we know about."""
    stripped = text.strip()
    # 1) drop ```json ... ``` fences
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].lstrip()
    # 2) locate the first balanced {...} object anywhere in the reply
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
            continue  # invalid JSON inside braces — look for another object
        if isinstance(obj, dict) and obj.get("tool") in TOOLS:
            return obj
        # A valid object but not a tool call we recognise — keep scanning in
        # case the model emitted prose before the real call.
    return None


def run_agent_turn(messages: list[dict]) -> str:
    for step in range(MAX_TOOL_STEPS):
        reply = call_model(messages)
        tool_call = try_parse_tool_call(reply)
        if tool_call is None:
            log_event("agent_reply", reply=reply)
            return reply
        tool_name = tool_call["tool"]
        args = tool_call.get("args", {})
        if not isinstance(args, dict):
            args = {}
        console.print(f"[cyan]→ calling tool:[/cyan] {tool_name}({args})")
        log_event("tool_call", tool=tool_name, args=json.dumps(args, default=str))
        result = TOOLS[tool_name](args)
        log_event("tool_result", tool=tool_name, result=json.dumps(result, default=str)[:2000])
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": f"Tool result: {json.dumps(result, default=str)}"})
    return "Reached max tool steps for this turn without a final answer."


def render_reply(answer: str) -> None:
    """Render the model's answer. Plain text stays plain; markdown (headings,
    lists, fenced code) gets rendered by rich."""
    console.print(Panel(Markdown(answer) if _looks_like_markdown(answer) else answer, title="agent", border_style="green"))


def _looks_like_markdown(text: str) -> bool:
    markers = ["\n-", "\n#", "\n```", "- [ ]", "**", "|", "\n1."]
    return any(m in text for m in markers)


# ---------------------------------------------------------------------------
# Status / health check
# ---------------------------------------------------------------------------

def run_status_check() -> int:
    """Print a health summary for every subsystem and return an exit code."""
    table = Table(title="Personal AI Agent — Status", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Detail", style="dim")

    # Ollama + model
    try:
        resp = _session.get(OLLAMA_URL.replace("/api/chat", "/api/tags"), timeout=5)
        resp.raise_for_status()
        model_names = [m.get("name", "") for m in resp.json().get("models", [])]
        have_model = MODEL_NAME in model_names
        installed = [m for m in model_names if MODEL_NAME in m]
        table.add_row("Ollama", "OK", f"{len(model_names)} models")
        table.add_row("Agent model", "OK" if installed else "MISSING",
                      MODEL_NAME + (" (installed)" if installed else " — run: ollama create my-agent -f Modelfile"))
    except Exception:
        table.add_row("Ollama", "FAIL", "not reachable at " + OLLAMA_URL)

    # Home Assistant
    if HA_URL and HA_TOKEN:
        try:
            resp = _session.get(f"{HA_URL}/api/", headers=_ha_headers(), timeout=5)
            table.add_row("Home Assistant", "OK" if resp.ok else f"FAIL ({resp.status_code})", HA_URL)
        except Exception:
            table.add_row("Home Assistant", "FAIL", HA_URL)
    else:
        table.add_row("Home Assistant", "SKIPPED", "not configured (set HA_URL/HA_TOKEN)")

    # Voice
    table.add_row("TTS (piper)", "OK" if Path(PIPER_MODEL).exists() else "SKIPPED", PIPER_MODEL or "not configured")
    table.add_row("Voice mode", "Voice" if voice_enabled() else "Text", "")

    # Vision
    if VISION_ENABLED:
        table.add_row("Vision", "OK" if VisionAvailable() else "model missing", VISION_MODEL)
    else:
        table.add_row("Vision", "SKIPPED", "VISION_MODEL not set")

    # Face data + camera
    face_path = Path(os.getenv("FACE_DATA_PATH", "face_data.pkl"))
    if face_path.exists():
        table.add_row("Face data", "OK", str(face_path))
    else:
        table.add_row("Face data", "SKIPPED", "no face_data.pkl (run enroll_face.py)")

    console.print(table)
    console.print()
    return table.row_count  # heuristic; not a meaningful exit code nuance


# ---------------------------------------------------------------------------
# Error surfacing
# ---------------------------------------------------------------------------

def handle_model_error(e: Exception) -> None:
    """Show a friendly, actionable message instead of a traceback when the
    model backend fails mid-conversation."""
    if isinstance(e, requests.exceptions.ConnectionError) or isinstance(e, ConnectionError):
        console.print("[bold red]Lost connection to Ollama.[/bold red] Is it still running?")
        console.print(f"  endpoint: {OLLAMA_URL}")
    elif isinstance(e, requests.exceptions.HTTPError):
        console.print(f"[bold red]Ollama returned HTTP {e.response.status_code}.[/bold red]")
        if e.response.status_code == 404:
            console.print(f"  Model '{MODEL_NAME}' not found. Build it with: ollama create {MODEL_NAME} -f Modelfile")
    else:
        console.print(f"[bold red]Agent error:[/bold red] {e}")


# ---------------------------------------------------------------------------
# Interactive loop (with readline history)
# ---------------------------------------------------------------------------

def _load_history() -> None:
    try:
        import readline
        hist = Path("history.txt")
        if hist.exists():
            readline.read_history_file(str(hist))
        readline.set_history_length(200)
    except (ImportError, OSError):
        pass


def _save_history() -> None:
    try:
        import readline
        hist = Path("history.txt")
        readline.write_history_file(str(hist))
    except (ImportError, OSError):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--voice", action="store_true", help="Talk to the agent by voice (press Enter, then speak)")
    parser.add_argument("--wake", action="store_true", help="Always-listening mode: say the wake word, then your command")
    parser.add_argument("--vision", action="store_true", help="Enable the describe_scene (camera/vision) tool")
    parser.add_argument("--status", action="store_true", help="Print a health check and exit")
    args = parser.parse_args()

    global VOICE_MODE_ACTIVE

    if args.status:
        sys.exit(run_status_check())

    if args.vision:
        global VISION_ENABLED
        VISION_ENABLED = bool(VISION_MODEL)
        if not VISION_ENABLED:
            console.print("[bold red]Vision requested but VISION_MODEL is not set in .env.[/bold red]")
            console.print("Pull a vision model, e.g. `ollama pull qwen2.5vl:7b`, and set VISION_MODEL=qwen2.5vl:7b.")
            sys.exit(1)

    if args.wake or args.voice:
        VOICE_MODE_ACTIVE = True

    # Startup banner + config validation
    setup_logging()
    log_event("session_start", mode="wake" if args.wake else ("voice" if args.voice else "text"))
    console.print("[bold green]Local terminal agent[/bold green] — model:", MODEL_NAME)
    console.print(f"File tools scoped to: {WORKDIR_SCOPE}")
    for warn in validate_config():
        console.print(f"[yellow]⚠ {warn}[/yellow]")
    console.print(f"Home Assistant: {'configured' if HA_URL and HA_TOKEN else '[dim]not configured (see .env)[/dim]'}")
    if SESSION_LOG_ACTIVE:
        console.print(f"[dim]Session log: {SESSION_LOG}[/dim]")

    if args.wake:
        run_wake_word_loop()
        return

    console.print(f"Mode: {'voice' if args.voice else 'text'} — type/say 'exit' to quit.\n")

    _load_history()
    messages: list[dict] = []
    # Inject standing instructions (who the agent is, its tools, how to act).
    # This is skipped for --status/--voice quick probes only when validated.
    try:
        from system_prompt import build_system_prompt
        messages.append({"role": "system", "content": build_system_prompt(str(WORKDIR_SCOPE))})
    except Exception:
        pass

    try:
        while True:
            try:
                if args.voice:
                    console.input("[dim]Press Enter then speak...[/dim]")
                    user_input = listen()
                    if not user_input:
                        continue
                else:
                    user_input = console.input("[bold blue]you> [/bold blue]")
            except (EOFError, KeyboardInterrupt):
                break

            if user_input.strip().lower() in {"exit", "quit"}:
                break

            log_event("user_input", input=user_input)
            messages.append({"role": "user", "content": user_input})
            _trim_context(messages)
            try:
                answer = run_agent_turn(messages)
            except Exception as e:
                handle_model_error(e)
                # Drop the message that caused the failure so the session can
                # continue without a poisoned prompt.
                messages.pop()
                continue
            messages.append({"role": "assistant", "content": answer})
            _trim_context(messages)
            render_reply(answer)

            if args.voice:
                speak(answer)
    finally:
        _save_history()
        log_event("session_end")
        if SESSION_LOG_ACTIVE:
            console.print(f"[dim]Session log written to {SESSION_LOG}[/dim]")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]Could not reach Ollama at localhost:11434.[/bold red]")
        console.print("Make sure Ollama is installed and running: https://ollama.com")
        sys.exit(1)