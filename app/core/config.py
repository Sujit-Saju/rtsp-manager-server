import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME = os.getenv("APP_NAME", "RTSP Manager")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENV = os.getenv("ENV", "development")

    RTSP_PORT = int(os.getenv("RTSP_PORT", 8554))

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///rtsp_manager.db"
    )

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    LOG_FOLDER = os.getenv("LOG_FOLDER", "logs")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    API_PREFIX = os.getenv("API_PREFIX", "/api/v1")