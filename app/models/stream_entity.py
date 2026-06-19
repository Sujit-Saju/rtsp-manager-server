from enum import Enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum as SqlEnum,
)
from app.database.base import Base


class StreamSourceType(str, Enum):
    FILE = "FILE"
    USB_CAMERA = "USB_CAMERA"
    CSI_CAMERA = "CSI_CAMERA"
    RTSP = "RTSP"
    HTTP = "HTTP"
    HLS = "HLS"


class StreamStatus(str, Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DELETED = "DELETED"


class Stream(Base):
    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Unique stream identifier
    stream_code = Column(String(20), unique=True, nullable=False, index=True)

    # User defined name
    stream_name = Column(String(100), nullable=False)

    # Source
    source_type = Column(
        SqlEnum(StreamSourceType),
        nullable=False,
        default=StreamSourceType.FILE,
    )

    # Original uploaded file
    original_filename = Column(String(255))

    # Stored filename
    stored_filename = Column(String(255))

    # Absolute/local storage path
    file_path = Column(String(500))

    # RTSP endpoint
    stream_url = Column(String(255), unique=True)

    # Stream configuration
    fps = Column(Integer, default=15)

    resolution = Column(String(20), default="1280x720")

    codec = Column(String(20), default="H264")

    bitrate = Column(String(20), default="2M")

    rtsp_port = Column(Integer, default=8554)

    loop_enabled = Column(Boolean, default=True)

    # Runtime
    process_id = Column(Integer)

    connected_clients = Column(Integer, default=0)

    status = Column(
        SqlEnum(StreamStatus),
        nullable=False,
        default=StreamStatus.CREATED,
    )

    # Metadata
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    deleted_at = Column(DateTime)