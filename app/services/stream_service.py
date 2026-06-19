from app.repositories.stream_repository import StreamRepository
from app.utils.response import success_response, error_response

class StreamService:

    def __init__(self):
        self.repo = StreamRepository()

    async def create_stream(self, data):

        existing = await self.repo.find_by_stream_url(data["streamUrl"])

        if existing:
            return (
                error_response("Stream already exists."),
                409,
            )
        
        uniq_code = await self.unique_code_service.generate("STREAM")

        stream = await self.repo.create(data)

        return (
            success_response(
                "Stream created successfully.",
                stream.to_dict(),
            ),
            201,
        )

    async def get_all_streams(self):

        streams = await self.repo.find_all()

        return (
            success_response(
                "Streams fetched successfully.",
                [s.to_dict() for s in streams],
            ),
            200,
        )

    async def get_stream(self, uniq_code):

        stream = await self.repo.find_by_uniq_code(uniq_code)

        if not stream:
            return (
                error_response("Stream not found."),
                404,
            )

        return (
            success_response(
                "Stream fetched successfully.",
                stream.to_dict(),
            ),
            200,
        )

    async def update_stream(self, data):

        stream = await self.repo.find_by_uniq_code(data["uniqCode"])

        if not stream:
            return (
                error_response("Stream not found."),
                404,
            )

        updated = await self.repo.update(stream, data)

        return (
            success_response(
                "Stream updated successfully.",
                updated.to_dict(),
            ),
            200,
        )

    async def delete_stream(self, uniq_code):

        stream = await self.repo.find_by_uniq_code(uniq_code)

        if not stream:
            return (
                error_response("Stream not found."),
                404,
            )

        await self.repo.delete(stream)

        return (
            success_response("Stream deleted successfully."),
            200,
        )