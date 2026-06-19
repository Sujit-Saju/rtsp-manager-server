# ============================================
# File     : base.py
# Author   : Sujit
# Created  : 2026-06-10
# Desc     : Base repository with generic CRUD
#            operations for all models
# ============================================

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db: AsyncSession, model):
        self.db = db
        self.model = model

    async def get_by_id(self, id: int):
        result = await self.db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_by_uniq_code(self, uniq_code: str):
        result = await self.db.execute(
            select(self.model).where(self.model.uniq_code == uniq_code)
        )
        return result.scalars().first()

    async def get_all(self):
        result = await self.db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: int):
        obj = await self.get_by_id(id)

        if obj:
            await self.db.delete(obj)
            await self.db.commit()

        return obj

    async def update(self, obj):
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
