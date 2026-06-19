"""
===============================================================================
File        : sequence_number.py
Description : SQLAlchemy model for maintaining sequence counters used across
              the NVR system. Supports entity-wise sequence generation with
              optional date-based resetting.
Created     : 2026-06-10
Author      : Sujit Saju
===============================================================================
"""

from sqlalchemy import Column, BigInteger, Integer, String, Boolean

from app.database.base import Base


class SequenceNumber(Base):
    """
    Stores sequence counters for different entities in the NVR system.

    Example:
        entity_type      sequence_number
        --------------------------------
        CAMERA                  125
        USER                     42
        MASTER_NODE               8
        SLAVE_NODE               17
        LICENSE                   5

    If `with_date` is enabled, the sequence can be reset based on the
    stored `date_format`.
    """

    __tablename__ = "tbl_seq_number"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    entity_type = Column(String(100), unique=True, nullable=False)

    prefix = Column(String(20), nullable=False)

    sequence_number = Column(BigInteger, nullable=False, default=1)

    number_width = Column(Integer, nullable=False, default=5)

    date_format = Column(String(20), nullable=True, default="%Y%m%d")

    with_date = Column(Boolean, nullable=False, default=False)