# app/services/stream_manager.py

import os
import json
import time
import threading
import subprocess

FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg")
MEDIAMTX_BIN = os.getenv("MEDIAMTX_BIN", "./mediamtx.exe")
MEDIAMTX_HOST = os.getenv("RTSP_HOST", "192.168.0.234")
RTSP_PORT = int(os.getenv("RTSP_PORT", "8554"))

# Config file written next to mediamtx.exe
MEDIAMTX_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(MEDIAMTX_BIN)), "mediamtx_config.yml"
)

FFPROBE_BIN = os.getenv("FFPROBE_BIN", FFMPEG_BIN.replace("ffmpeg.exe", "ffprobe.exe"))

_mediamtx_proc: subprocess.Popen | None = None
_mediamtx_config_path: str | None = None
_mediamtx_lock = threading.Lock()
_stream_count = 0

active_streams: dict[str, dict] = {}
_lock = threading.Lock()


# ─────────────────────────────────────────
# Dependency check
# ─────────────────────────────────────────


def check_dependencies():
    errors = []

    try:
        subprocess.run([FFMPEG_BIN, "-version"], capture_output=True, check=True)
        print(f"[startup] FFmpeg verified: {FFMPEG_BIN}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        errors.append(f"ffmpeg not found at '{FFMPEG_BIN}' — check FFMPEG_BIN in .env")

    if not os.path.isfile(MEDIAMTX_BIN):
        errors.append(f"mediamtx not found at '{MEDIAMTX_BIN}'")
    else:
        print(f"[startup] MediaMTX verified: {MEDIAMTX_BIN}")

    if errors:
        for e in errors:
            print(f"[STARTUP ERROR] {e}")
        raise RuntimeError("Missing required binaries. See errors above.")


# ─────────────────────────────────────────
# MediaMTX lifecycle
# ─────────────────────────────────────────


def _write_mediamtx_config() -> str:
    config = (
        "logLevel: error\n"
        f"rtspAddress: :{RTSP_PORT}\n"
        "rtmp: no\n"
        "hls: no\n"
        "webrtc: no\n"
        "srt: no\n"
        "paths:\n"
        "  ~^.*$:\n"
        "    source: publisher\n"
    )

    config_path = os.path.abspath(MEDIAMTX_CONFIG_PATH)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config)

    print(f"[mediamtx] Config written → {config_path}")
    return config_path


def _ensure_mediamtx_running():
    global _mediamtx_proc, _mediamtx_config_path, _stream_count

    with _mediamtx_lock:
        _stream_count += 1

        # Already running and healthy
        if _mediamtx_proc and _mediamtx_proc.poll() is None:
            return

        if _mediamtx_proc:
            print("[mediamtx] Process died — restarting...")

        # Write config and resolve absolute paths
        _mediamtx_config_path = _write_mediamtx_config()
        mediamtx_abs = os.path.abspath(MEDIAMTX_BIN)

        print(f"[mediamtx] Starting: {mediamtx_abs}")

        _mediamtx_proc = subprocess.Popen(
            [mediamtx_abs, _mediamtx_config_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(mediamtx_abs),  # run from its own directory
        )

        # Log stdout + stderr in background
        def _log_output(stream, label):
            for line in stream:
                decoded = line.decode(errors="replace").strip()
                if decoded:
                    print(f"[mediamtx] {decoded}")

        threading.Thread(
            target=_log_output, args=(_mediamtx_proc.stdout, "stdout"), daemon=True
        ).start()
        threading.Thread(
            target=_log_output, args=(_mediamtx_proc.stderr, "stderr"), daemon=True
        ).start()

        # Windows needs more time to bind ports
        time.sleep(2.5)

        if _mediamtx_proc.poll() is not None:
            raise RuntimeError(
                f"MediaMTX failed to start. Check binary at '{MEDIAMTX_BIN}'"
            )

        print(f"[mediamtx] Started → rtsp://{MEDIAMTX_HOST}:{RTSP_PORT}/<uniqCode>")


def _release_mediamtx():
    global _mediamtx_proc, _mediamtx_config_path, _stream_count

    with _mediamtx_lock:
        _stream_count -= 1

        if _stream_count > 0:
            return

        if _mediamtx_proc:
            _mediamtx_proc.terminate()
            _mediamtx_proc.wait()
            _mediamtx_proc = None
            print("[mediamtx] Stopped — no active streams")

        # Keep the config file — will be overwritten on next start anyway
        _mediamtx_config_path = None


# ─────────────────────────────────────────
# FFmpeg command builder
# ─────────────────────────────────────────


def _can_stream_copy(video_path: str, fps: int, resolution: str) -> bool:
    """Returns True if the video is already H.264 with matching fps/resolution."""
    try:
        width, height = resolution.split("x")
        result = subprocess.run(
            [
                FFPROBE_BIN,
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,r_frame_rate",
                "-of",
                "json",
                video_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        info = json.loads(result.stdout)
        s = info["streams"][0]

        src_codec = s.get("codec_name", "")
        src_width = str(s.get("width", ""))
        src_height = str(s.get("height", ""))
        fps_parts = s.get("r_frame_rate", "0/1").split("/")
        src_fps = int(fps_parts[0]) // max(int(fps_parts[1]), 1)

        return (
            src_codec == "h264"
            and src_width == width
            and src_height == height
            and src_fps == fps
        )
    except Exception:
        return False


def _build_ffmpeg_cmd(
    video_path: str, fps: int, resolution: str, uniq_code: str
) -> list[str]:
    width, height = resolution.split("x")
    rtsp_url = f"rtsp://127.0.0.1:{RTSP_PORT}/{uniq_code}"

    if _can_stream_copy(video_path, fps, resolution):
        print(f"[ffmpeg:{uniq_code}] Source is H.264 — using stream copy")
        video_args = ["-c:v", "copy", "-c:a", "copy"]
    else:
        print(f"[ffmpeg:{uniq_code}] Transcoding to H.264")
        video_args = [
            "-vf",
            f"scale={width}:{height}",
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "zerolatency",
            "-b:v",
            "2M",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
        ]

    return [
        FFMPEG_BIN,
        "-re",
        "-stream_loop",
        "-1",
        "-i",
        video_path,
        *video_args,
        "-f",
        "rtsp",
        "-rtsp_transport",
        "tcp",
        rtsp_url,
    ]


# ─────────────────────────────────────────
# Public API
# ─────────────────────────────────────────


def get_rtsp_url(uniq_code: str) -> str:
    return f"rtsp://{MEDIAMTX_HOST}:{RTSP_PORT}/{uniq_code}"


def starting_streaming(stream) -> str:
    uniq_code = stream.uniq_code
    rtsp_url = get_rtsp_url(uniq_code)

    _ensure_mediamtx_running()

    def run():
        cmd = _build_ffmpeg_cmd(
            video_path=stream.file_path,
            fps=stream.fps,
            resolution=stream.resolution,
            uniq_code=uniq_code,
        )

        ffmpeg_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )

        with _lock:
            active_streams[uniq_code] = {
                "ffmpeg": ffmpeg_proc,
                "rtsp_url": rtsp_url,
            }

        print(f"[ffmpeg:{uniq_code}] Streaming → {rtsp_url}")

        if ffmpeg_proc.stderr:
            for line in ffmpeg_proc.stderr:
                decoded = line.decode(errors="replace").strip()
                if decoded:
                    print(f"[ffmpeg:{uniq_code}] {decoded}")

        ffmpeg_proc.wait()
        _release_mediamtx()

        with _lock:
            active_streams.pop(uniq_code, None)

        print(f"[ffmpeg:{uniq_code}] Stream ended")

    threading.Thread(target=run, daemon=True).start()

    return rtsp_url


def stop_streaming(uniq_code: str):
    with _lock:
        entry = active_streams.get(uniq_code)

    if not entry:
        print(f"[stream_manager] No active stream found for {uniq_code}")
        return

    entry["ffmpeg"].terminate()
    entry["ffmpeg"].wait()
    print(f"[stream_manager] Stopped stream {uniq_code}")


def get_active_streams() -> dict:
    with _lock:
        return {
            code: {"rtsp_url": entry["rtsp_url"]}
            for code, entry in active_streams.items()
        }
