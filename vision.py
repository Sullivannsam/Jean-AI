#!/usr/bin/env python3
"""
Optional vision capability — describes the current camera frame using a local
vision-capable model served by Ollama (e.g. qwen2.5vl, llava).

Only used when VISION_MODEL is set in .env and the agent is run with --vision.
"""
import base64
import os

import cv2
import requests

from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
VISION_MODEL = os.getenv("VISION_MODEL", "")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))


def _capture_base64() -> str:
    cam = cv2.VideoCapture(CAMERA_INDEX)
    if not cam.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}.")
    try:
        ret, frame = cam.read()
        if not ret:
            raise RuntimeError("Failed to capture a frame from the camera.")
        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            raise RuntimeError("Failed to encode the frame as JPEG.")
        return base64.b64encode(buf.tobytes()).decode("ascii")
    finally:
        cam.release()


def describe_scene(prompt: str = "Describe what you see in this image.") -> str:
    if not VISION_MODEL:
        raise RuntimeError("VISION_MODEL is not set in .env.")
    image_b64 = _capture_base64()
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_b64],
            }
        ],
        "stream": False,
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


if __name__ == "__main__":
    print(describe_scene())
