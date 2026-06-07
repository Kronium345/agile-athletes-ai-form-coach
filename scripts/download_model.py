"""Download MediaPipe Pose Landmarker model."""

import urllib.request
from pathlib import Path

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)
MODEL_PATH = Path("models/pose_landmarker_lite.task")


def download_model() -> None:
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists():
        print(f"Model already exists at {MODEL_PATH}")
        return

    print(f"Downloading pose landmarker model to {MODEL_PATH}...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")


if __name__ == "__main__":
    download_model()
