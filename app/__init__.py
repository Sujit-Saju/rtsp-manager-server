# ============================================
# File     : __init__.py
# Author   : Sujit
# Desc     : Quart application factory
# ============================================

import os

from app.controller import register_all
from quart import Quart, send_from_directory
from quart_cors import cors
from quart_schema import QuartSchema

from app.core.config import Config
from app.core.session import get_db
from app.database import engine, Base
from app.core.logger import logger
from app.utils.stream_manager import _prewarm_mediamtx, check_dependencies, starting_streaming


def create_app() -> Quart:

    app = Quart(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
    # ---------------------------------------
    # Swagger
    # ---------------------------------------

    QuartSchema(
        app,
        info={
            "title": Config.APP_NAME,
            "version": "1.0.0",
        },
        openapi_path=f"{Config.API_PREFIX}/openapi.json",
        swagger_ui_path=f"{Config.API_PREFIX}/docs",
    )

    # ---------------------------------------
    # CORS
    # ---------------------------------------

    frontend_host = os.getenv("FRONTEND_BASE_URL", "192.168.0.234").strip()
    frontend_port = os.getenv("FRONTEND_PORT", "3000").strip()

    frontend_url = f"http://{frontend_host}:{frontend_port}"

    app = cors(
        app,
        allow_origin=[frontend_url],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    # ---------------------------------------
    # Startup
    # ---------------------------------------

    @app.before_serving
    async def startup():

        logger.info("Initializing database...")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        check_dependencies()
        logger.info("FFmpeg and MediaMTX verified.")
        
        # Start MediaMTX immediately at startup, don't wait for first stream
        _prewarm_mediamtx()

        logger.info("Database ready.")

        await restart_active_streams()

    # ---------------------------------------
    # Shutdown
    # ---------------------------------------

    @app.after_serving
    async def shutdown():

        logger.info("Closing database engine...")

        await engine.dispose()

        logger.info("Database engine closed.")

        # ---------------------------------------
    # Static file serving for uploads
    # ---------------------------------------

    @app.route("/api/v1/uploads/<path:filename>")
    async def serve_uploads(filename):
        uploads_dir = os.path.abspath("uploads")
        return await send_from_directory(uploads_dir, filename)
    
    # ---------------------------------------
    # Blueprints
    # ---------------------------------------

    register_all(app)

    return app

# ─────────────────────────────────────────
# Restart streams from DB on startup
# ─────────────────────────────────────────

async def restart_active_streams():
    from app.repositories.stream_repository import StreamRepository

    try:
        async with get_db() as db:
            repo = StreamRepository(db)
            streams = await repo.get_all_streams()

        if not streams:
            logger.info("No streams found in DB — nothing to restart.")
            return

        logger.info(f"Found {len(streams)} stream(s) in DB — restarting...")

        for stream in streams:
            try:
                rtsp_url = starting_streaming(stream)
                logger.info(f"[{stream.uniq_code}] Restarted → {rtsp_url}")
            except Exception as e:
                logger.error(f"[{stream.uniq_code}] Failed to restart: {e}")

        logger.info("All streams restarted successfully.")

    except Exception as e:
        logger.error(f"Failed to restart streams on startup: {e}")
        