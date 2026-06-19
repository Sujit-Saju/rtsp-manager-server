# ============================================
# File     : stream_repository.py
# Author   : Sujit
# Created  : 2026-06-10
# Desc     : Repository for Stream data access,
#            extending base CRUD operations
# ============================================

from app.repositories.base import BaseRepository
from app.models.stream_entity import Stream
from sqlalchemy import func, select
from sqlalchemy.orm import Session


class StreamRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Stream)

    async def get_by_stream_url(self, stream_url: str):
        result = await self.db.execute(
            select(Stream).where(Stream.stream_url == stream_url)
        )
        return result.scalars().first()

    async def get_by_stream_url_and_uniq_code(self, stream_url: str, uniq_code: str):
        result = await self.db.execute(
            select(Stream).where(
                (Stream.stream_url == stream_url) & (Stream.uniq_code == uniq_code)
            )
        )
        return result.scalars().first()

    async def find_by_uniq_code(self, uniq_code: str):
        result = await self.db.execute(
            select(Stream).where(Stream.uniq_code == uniq_code)
        )
        return result.scalars().first()

    async def get_all_Stream(
        self,
        page: int | None = None,
        limit: int | None = None,
    ):
        query = select(Stream)

        # Apply pagination only if both page and limit are provided
        if page is not None and limit is not None:
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)

        return result.scalars().all()

    async def count(self):
        result = await self.db.execute(select(func.count()).select_from(Stream))
        return result.scalar_one()

    async def delete_by_uniq_code(self, uniq_code: str):
        result = await self.db.execute(
            select(Stream).where(Stream.uniq_code == uniq_code)
        )

        obj = result.scalars().first()

        if obj:
            await self.db.delete(obj)
            await self.db.commit()

        return obj

    async def create(self, camera_obj: Stream):
        self.db.add(camera_obj)

        await self.db.commit()
        await self.db.refresh(camera_obj)

        return camera_obj
