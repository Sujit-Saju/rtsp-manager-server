import os

from quart import Blueprint, request
from app.core.config import Config
from app.services.stream_service import StreamService

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
stream_bp = Blueprint("stream", __name__, url_prefix=f"{API_PREFIX}/cameras")

class StreamController:

    def __init__(self):
        self.bp = Blueprint(
            "stream",
            __name__,
            url_prefix=f"{Config.API_PREFIX}/stream",
        )
        
        self.register_routes()

    def register_routes(self):

        self.bp.add_url_rule(
            "",
            view_func=self.create_stream,
            methods=["POST"],
        )

        self.bp.add_url_rule(
            "",
            view_func=self.get_all_streams,
            methods=["GET"],
        )

        self.bp.add_url_rule(
            "/<string:uniq_code>",
            view_func=self.get_stream,
            methods=["GET"],
        )

        self.bp.add_url_rule(
            "/<string:uniq_code>",
            view_func=self.update_stream,
            methods=["PUT"],
        )

        self.bp.add_url_rule(
            "/<string:uniq_code>",
            view_func=self.delete_stream,
            methods=["DELETE"],
        )

    async def create_stream(self):
        data = await request.get_json()
        return await self.service.create_stream(data)

    async def get_all_streams(self):
        return await self.service.get_all_streams()

    async def get_stream(self, uniq_code):
        return await self.service.get_stream(uniq_code)

    async def update_stream(self, uniq_code):
        data = await request.get_json()
        data["uniqCode"] = uniq_code
        return await self.service.update_stream(data)

    async def delete_stream(self, uniq_code):
        return await self.service.delete_stream(uniq_code)
    
    @classmethod
    def blueprint(cls):

        return cls().bp