# ============================================
# File     : __init__.py
# Author   : Sujit
# Desc     : Quart application factory
# ============================================

import os

from app.controller import register_all
from quart import Quart
from quart_cors import cors
from quart_schema import QuartSchema

from app.core.config import Config
from app.database import engine, Base
from app.core.logger import logger


def create_app() -> Quart:

    app = Quart(__name__)

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

        logger.info("Database ready.")

    # ---------------------------------------
    # Shutdown
    # ---------------------------------------

    @app.after_serving
    async def shutdown():

        logger.info("Closing database engine...")

        await engine.dispose()

        logger.info("Database engine closed.")

    # ---------------------------------------
    # Blueprints
    # ---------------------------------------

    register_all(app)

    return app