"""
===============================================================================
File        : unique_code_service.py
Description : Service responsible for generating entity-specific unique codes.
Author      : Sujit
Created     : 2026-06-13
===============================================================================
"""

from datetime import datetime

from app.models.sequence_number import SequenceNumber
from app.repositories.sequence_repository import SequenceRepository
from app.core.unique_code_config import UNIQUE_CODE_CONFIG


class UniqueCodeService:

    def __init__(self, db):
        self.db = db
        self.repo = SequenceRepository(db)

    async def generate(self, entity_type: str) -> str:
        """
        Generate a unique code for the given entity type.

        Examples:
            CAMERA      -> CAM00001
            MASTER_NODE -> MST0001
            USER        -> USR00001
        """

        # Fetch sequence configuration from DB
        seq = await self.repo.get_by_entity_type(entity_type)

        # If configuration doesn't exist, create it from config file
        if seq is None:

            config = UNIQUE_CODE_CONFIG.get(entity_type)

            if config is None:
                raise ValueError(
                    f"No UNIQUE_CODE_CONFIG found for entity type '{entity_type}'."
                )

            seq = SequenceNumber(
                entity_type=entity_type,
                prefix=config["prefix"],
                sequence_number=1,
                number_width=config["number_width"],
                with_date=config.get("with_date", False),
                date_format=config.get("date_format", "%Y%m%d"),
            )

            self.db.add(seq)
            await self.db.flush()

        # Current value
        current_sequence = seq.sequence_number

        # Increment for next request
        seq.sequence_number += 1

        # Persist increment
        await self.db.commit()
        await self.db.refresh(seq)

        # Format sequence
        formatted_sequence = str(current_sequence).zfill(seq.number_width)

        if seq.with_date:
            date_part = datetime.now().strftime(seq.date_format)
            return f"{seq.prefix}{date_part}-{formatted_sequence}"

        return f"{seq.prefix}{formatted_sequence}"
