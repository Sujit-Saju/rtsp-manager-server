from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///rtsp_manager.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)