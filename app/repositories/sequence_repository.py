# ============================================
# File     : sequence_repository.py
# Author   : Sujit
# Created  : 2026-06-13
# Desc     : Repository for sequence number
# ============================================

from sqlalchemy import select

from app.models.sequence_number import SequenceNumber


class SequenceRepository:

    def __init__(self, db):
        self.db = db

    async def get_by_entity_type(self, entity_type: str):

        result = await self.db.execute(
            select(SequenceNumber).where(SequenceNumber.entity_type == entity_type)
        )

        return result.scalars().first()
