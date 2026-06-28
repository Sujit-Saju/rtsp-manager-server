# RTSP Manager — Server

The backend for RTSP Manager. Upload a video file and get a live RTSP stream back — no physical camera required. The server handles video storage, transcoding via FFmpeg, and stream publishing through an embedded MediaMTX server.

---

## How It Works

1. You upload a video file (MP4, AVI, MOV, MKV, etc.) through the API
2. The server saves the file and extracts a snapshot thumbnail using OpenCV
3. A unique stream code is generated (e.g. `STREAM-0001`)
4. FFmpeg starts pushing the video to MediaMTX as a looping RTSP stream
5. The RTSP URL (`rtsp://<host>:8554/STREAM-0001`) is returned and ready to use

MediaMTX starts automatically when the first stream is created and shuts down when the last stream is deleted.

---

## Tech Stack

- **Python** with **Quart** (async web framework) + **Hypercorn** (ASGI server)
- **SQLAlchemy** async ORM with **SQLite** (via aiosqlite)
- **FFmpeg** for video transcoding
- **OpenCV** for snapshot extraction
- **MediaMTX** (embedded binary) as the RTSP server
- **quart-schema** + **Pydantic** for request validation

---

## Project Structure

```
app/
├── controller/         # HTTP route handlers
├── services/           # Business logic (stream lifecycle)
├── repositories/       # Database access layer
├── models/             # SQLAlchemy ORM models
├── utils/
│   ├── stream_manager.py   # FFmpeg + MediaMTX orchestration
│   ├── file_upload.py      # Video upload + snapshot generation
│   └── response.py         # Standardised API response helpers
├── core/               # Config, logger, DB session
└── bin/                # MediaMTX binaries (linux + windows)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- FFmpeg installed and available on `PATH`

### Setup

```bash
# Clone the repo
git clone https://github.com/sujit-saju/rtsp-manager-server.git
cd rtsp-manager-server

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set RTSP_HOST to your machine's local IP

# Run the server
python run.py
```

The API will be available at `http://localhost:5000`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `5000` | HTTP port |
| `RTSP_HOST` | `192.168.0.234` | Your machine's IP — used in RTSP URLs |
| `RTSP_PORT` | `8554` | Port MediaMTX listens on |
| `DATABASE_URL` | `sqlite+aiosqlite:///rtsp_manager.db` | Database connection string |
| `FFMPEG_BIN` | `ffmpeg` | Path to FFmpeg binary |
| `UPLOAD_FOLDER` | `uploads` | Directory for uploaded videos |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `API_PREFIX` | `/api/v1` | API route prefix |

---

## API Reference

All endpoints are prefixed with `/api/v1/stream`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/add` | Create a stream (multipart/form-data) |
| `GET` | `/list` | List all streams |
| `GET` | `/<uniq_code>` | Get a single stream |
| `DELETE` | `/delete?uniq_code=<code>` | Delete a stream and its uploaded file |

### Create Stream — Form Fields

| Field | Type | Description |
|---|---|---|
| `file` | File | Video file (max 50 MB) |
| `streamName` | string | Display name for the stream |
| `fps` | integer | Target frame rate |
| `resolution` | string | e.g. `1920x1080` |
| `loopEnabled` | boolean | Loop the video continuously |
| `status` | boolean | Enable stream on creation |

### Example Response

```json
{
  "success": true,
  "message": "Stream created successfully.",
  "data": {
    "streamName": "Loading Dock North",
    "fps": 30,
    "uniqCode": "STREAM-0001",
    "resolution": "1920x1080",
    "status": true,
    "loopEnabled": true,
    "rtspUrl": "rtsp://192.168.0.234:8554/STREAM-0001"
  }
}
```

---

## Consuming the RTSP Stream

```bash
# VLC
vlc rtsp://192.168.0.234:8554/STREAM-0001

# FFplay
ffplay rtsp://192.168.0.234:8554/STREAM-0001

# OpenCV (Python)
import cv2
cap = cv2.VideoCapture("rtsp://192.168.0.234:8554/STREAM-0001")
```

---

## Supported Video Formats

MP4, AVI, MOV, MKV, FLV, WebM

---

## License

MIT — see [LICENSE](LICENSE) for details.
