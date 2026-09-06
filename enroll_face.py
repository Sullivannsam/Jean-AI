#!/usr/bin/env python3
"""
Enroll your face so presence.py can recognize you.

Captures a handful of frames from your webcam, extracts face encodings, and
saves them to face_data.pkl. Run this once — more samples (different angles,
lighting) make recognition more reliable.

Usage:
    python3 enroll_face.py
"""
import os
import pickle
from pathlib import Path

import cv2
import face_recognition
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

FACE_DATA_PATH = Path(os.getenv("FACE_DATA_PATH", "face_data.pkl"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
NUM_SAMPLES = 5


def main():
    cam = cv2.VideoCapture(CAMERA_INDEX)
    if not cam.isOpened():
        console.print(f"[bold red]Could not open camera index {CAMERA_INDEX}.[/bold red]")
        raise SystemExit(1)

    console.print(f"[bold green]Capturing {NUM_SAMPLES} face samples.[/bold green]")
    console.print("Look at the camera and move your head slightly between shots.\n")

    encodings = []
    while len(encodings) < NUM_SAMPLES:
        console.input(f"[dim]Sample {len(encodings) + 1}/{NUM_SAMPLES} — press Enter, then hold still...[/dim]")
        ret, frame = cam.read()
        if not ret:
            console.print("[red]Failed to capture frame, try again.[/red]")
            continue

        rgb_frame = frame[:, :, ::-1]
        locations = face_recognition.face_locations(rgb_frame)
        if len(locations) != 1:
            console.print(f"[red]Expected exactly 1 face, found {len(locations)}. Try again.[/red]")
            continue

        frame_encodings = face_recognition.face_encodings(rgb_frame, locations)
        encodings.append(frame_encodings[0])
        console.print(f"[green]Got sample {len(encodings)}/{NUM_SAMPLES}[/green]\n")

    cam.release()

    with open(FACE_DATA_PATH, "wb") as f:
        pickle.dump(encodings, f)

    console.print(f"[bold green]Saved {len(encodings)} face encodings to {FACE_DATA_PATH}[/bold green]")
    console.print("Now run: python3 presence.py")


if __name__ == "__main__":
    main()
