#!/usr/bin/env python3
"""
Face-presence watcher — watches the webcam, and when it recognizes your
enrolled face, speaks a welcome and turns on your entry light via Home
Assistant. Meant to run continuously (e.g. as a background service) so it
catches you the moment you walk in.

Run enroll_face.py once first to teach it your face.

Usage:
    python3 presence.py
"""
import os
import pickle
import time
from pathlib import Path

import cv2
import face_recognition
from dotenv import load_dotenv
from rich.console import Console

from agent import ha_turn_on_silent, speak

load_dotenv()
console = Console()

FACE_DATA_PATH = Path(os.getenv("FACE_DATA_PATH", "face_data.pkl"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
FACE_CHECK_INTERVAL = float(os.getenv("FACE_CHECK_INTERVAL", "2"))
FACE_TOLERANCE = float(os.getenv("FACE_TOLERANCE", "0.6"))  # lower = stricter match

ENTRY_LIGHT_ENTITY = os.getenv("ENTRY_LIGHT_ENTITY", "")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "Welcome home!")
WELCOME_COOLDOWN_SECONDS = float(os.getenv("WELCOME_COOLDOWN_SECONDS", "600"))  # don't re-trigger for 10 min


def load_known_faces() -> list:
    if not FACE_DATA_PATH.exists():
        console.print(f"[bold red]No face data found at {FACE_DATA_PATH}.[/bold red] Run enroll_face.py first.")
        raise SystemExit(1)
    with open(FACE_DATA_PATH, "rb") as f:
        return pickle.load(f)


def welcome_home() -> None:
    console.print("[bold green]Recognized you — welcome home![/bold green]")
    speak(WELCOME_MESSAGE)
    if ENTRY_LIGHT_ENTITY:
        result = ha_turn_on_silent(ENTRY_LIGHT_ENTITY)
        if "error" in result:
            console.print(f"[red]Could not turn on {ENTRY_LIGHT_ENTITY}: {result['error']}[/red]")
    else:
        console.print("[dim]No ENTRY_LIGHT_ENTITY set in .env — skipping light.[/dim]")


def main():
    known_encodings = load_known_faces()
    console.print(f"[bold green]Watching camera {CAMERA_INDEX} for your face...[/bold green] (Ctrl+C to stop)")

    cam = cv2.VideoCapture(CAMERA_INDEX)
    if not cam.isOpened():
        console.print(f"[bold red]Could not open camera index {CAMERA_INDEX}.[/bold red]")
        raise SystemExit(1)

    last_welcome_time = 0.0

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                time.sleep(FACE_CHECK_INTERVAL)
                continue

            rgb_frame = frame[:, :, ::-1]
            locations = face_recognition.face_locations(rgb_frame)
            encodings = face_recognition.face_encodings(rgb_frame, locations)

            for encoding in encodings:
                matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=FACE_TOLERANCE)
                if any(matches):
                    now = time.time()
                    if now - last_welcome_time > WELCOME_COOLDOWN_SECONDS:
                        welcome_home()
                        last_welcome_time = now
                    break

            time.sleep(FACE_CHECK_INTERVAL)
    except KeyboardInterrupt:
        pass
    finally:
        cam.release()


if __name__ == "__main__":
    main()
