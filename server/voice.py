#!/usr/bin/env python3
"""
Server-side voice: speech-to-text (faster-whisper) and text-to-speech (piper).

Used by the API server so a caller can POST audio and get text back, or POST
text and get spoken audio back. Everything runs locally — no cloud.
"""
import os
import subprocess
import tempfile
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
PIPER_BINARY = os.getenv("PIPER_BINARY", "piper")
PIPER_MODEL = os.getenv("PIPER_MODEL", "")

_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        _whisper_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _whisper_model


def transcribe_bytes(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """Transcribe raw audio bytes to text. Returns '' on failure."""
    if not audio_bytes:
        return ""
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
        f.write(audio_bytes)
        path = f.name
    try:
        segments, _ = _get_whisper_model().transcribe(path)
        return " ".join(seg.text.strip() for seg in segments).strip()
    finally:
        _unlink(path)


def transcribe_file(wav_path: str) -> str:
    segments, _ = _get_whisper_model().transcribe(wav_path)
    return " ".join(seg.text.strip() for seg in segments).strip()


def synthesize(text: str) -> bytes:
    """Turn text into WAV bytes using piper. Returns b'' on failure."""
    if not PIPER_MODEL or not Path(PIPER_MODEL).exists():
        return b""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        out_path = f.name
    try:
        subprocess.run(
            [PIPER_BINARY, "--model", PIPER_MODEL, "--output_file", out_path],
            input=text, text=True, check=True, capture_output=True,
        )
        return Path(out_path).read_bytes()
    finally:
        _unlink(out_path)


def _unlink(path: str) -> None:
    try:
        os.unlink(path)
    except OSError:
        pass