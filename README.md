# Agile Athletes AI Form Coach — Backend

Production-ready MVP backend for the Agile Athletes fitness app. Uses **FastAPI**, **MediaPipe Pose Landmarker**, and **OpenCV** to analyze exercise form from uploaded videos.

## Architecture

```
Expo React Native (frontend)
        │
        ▼  POST /analyze-form (multipart video)
┌───────────────────────────────────────┐
│  FastAPI Backend (this repo)          │
│  ├── PoseDetector (MediaPipe)         │
│  ├── AngleCalculator                  │
│  ├── ExerciseRegistry                 │
│  │     └── SquatAnalyzer (MVP)        │
│  └── FormAnalyzerService              │
└───────────────────────────────────────┘
        │
        ▼
  Frame metrics saved to data/metrics/
```

### Extensibility

New exercises (deadlift, bench press, overhead press, pull-up) are added by:

1. Creating a new analyzer class extending `ExerciseAnalyzer`
2. Implementing exercise-specific rules (or reusing shared utilities)
3. Registering it in `ExerciseRegistry`

Core pose detection (`pose_detector.py`) and angle math (`angle_calculator.py`) remain unchanged.

## Requirements

- Python 3.11+
- pip

## Quick Start

### 1. Clone and set up virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements-dev.txt
```

### 3. Download MediaPipe model

```bash
python scripts/download_model.py
```

This downloads `pose_landmarker_lite.task` (~5 MB) to `models/`.

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## API

### `GET /health`

Returns service status and supported exercises.

### `POST /analyze-form`

Analyze exercise form from an uploaded video.

**Request** (multipart/form-data):

| Field     | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| `video`   | file   | Yes      | Exercise video (.mp4)    |
| `exercise`| string | No       | Exercise type (default: `squat`) |

**Example (curl):**

```bash
curl -X POST http://localhost:8000/analyze-form \
  -F "video=@squat.mp4" \
  -F "exercise=squat"
```

**Response:**

```json
{
  "exercise": "squat",
  "score": 82,
  "issues": [
    {
      "issue": "Knees collapsing inward",
      "severity": "medium",
      "feedback": "Push knees outward during descent."
    }
  ],
  "joint_angles": {
    "left_knee": 92,
    "right_knee": 88,
    "hip": 76
  }
}
```

## Squat Analysis Rules

| Rule            | Detection                                      | Penalty Weight |
|-----------------|------------------------------------------------|----------------|
| Depth           | Hip below knee level                           | 25             |
| Knee valgus     | Knee medial to hip-ankle axis                  | 20             |
| Forward lean    | Torso angle exceeds 45° from vertical          | 15             |
| Heel lift       | Heel rises above ankle                         | 10             |

Score starts at **100** and subtracts weighted penalties based on issue frequency across frames.

## Project Structure

```
app/
├── main.py                 # FastAPI application
├── api/
│   ├── routes.py           # HTTP endpoints
│   └── schemas.py          # Pydantic response models
├── core/
│   ├── config.py           # Settings (env-based)
│   └── dependencies.py     # Dependency injection
├── domain/
│   └── models.py           # Domain dataclasses
├── exercises/
│   ├── base.py             # ExerciseAnalyzer ABC
│   ├── registry.py         # Exercise registry
│   └── squat.py            # Squat analyzer
├── services/
│   ├── form_analyzer.py    # Analysis orchestration
│   └── video_processor.py  # Video validation & temp files
└── utils/
    ├── pose_detector.py    # MediaPipe wrapper (33 landmarks)
    ├── angle_calculator.py # Joint angle calculations
    ├── exercise_rules.py   # Squat form rules & scoring
    └── landmarks.py        # Landmark index constants
```

## MediaPipe Integration

This backend uses the current [Pose Landmarker Task API](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/python) (successor to the legacy [MediaPipe Pose](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/pose.md) solution).

| Official concept | Our implementation |
|------------------|-------------------|
| 33 BlazePose landmarks | `app/utils/landmarks.py` — `PoseLandmark` enum + `POSE_CONNECTIONS` |
| `pose_landmarks` (normalized image) | `FrameLandmarks.landmarks` |
| `pose_world_landmarks` (meters, hip origin) | `FrameLandmarks.world_landmarks` — preferred for angles & depth |
| Video stream mode (detect + track) | `RunningMode.VIDEO` + `detect_for_video()` |
| `min_detection_confidence` / `min_tracking_confidence` | Configurable via `Settings` (default 0.5) |
| Model complexity (Lite / Full / Heavy) | `pose_landmarker_lite.task` by default; swap via `POSE_MODEL_PATH` |

## Configuration

Environment variables (optional, see `.env.example`):

| Variable                    | Default                          | Description                    |
|-----------------------------|----------------------------------|--------------------------------|
| `POSE_MODEL_PATH`           | `models/pose_landmarker_lite.task` | MediaPipe model path         |
| `MAX_VIDEO_SIZE_MB`         | `50`                             | Max upload size                |
| `SAMPLE_EVERY_N_FRAMES`     | `1`                              | Frame sampling rate            |
| `METRICS_DIR`               | `data/metrics`                   | Frame metrics output directory |
| `CORS_ORIGINS`              | `*`                              | Allowed CORS origins           |

## Testing

```bash
pytest
```

Tests cover angle calculations, squat rules, analyzer logic, and API endpoints (with mocked pose detection).

## Docker

```bash
docker build -t agile-athletes-form-coach .
docker run -p 8000:8000 agile-athletes-form-coach
```

## Deploy to Render

1. Push this repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect the repo and use the included `Dockerfile`
4. Set health check path to `/health`
5. Optionally mount a persistent disk at `/app/data/metrics` for frame metrics storage

Or use the Blueprint:

```bash
# render.yaml included — deploy via Render Dashboard > Blueprints
```

## Adding a New Exercise

```python
# app/exercises/deadlift.py
from app.exercises.base import ExerciseAnalyzer
from app.domain.models import AnalysisResult, FrameLandmarks

class DeadliftAnalyzer(ExerciseAnalyzer):
    @property
    def name(self) -> str:
        return "deadlift"

    def analyze(self, frames: list[FrameLandmarks]) -> AnalysisResult:
        # Use calculate_all_joint_angles() and custom rules
        ...
```

Register in `ExerciseRegistry._register_defaults()`:

```python
self.register(DeadliftAnalyzer())
```

## License

Proprietary — Agile Athletes
