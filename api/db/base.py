from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    pass


engine = None
async_session = None


async def init_db():
    """Initialize the database engine and session factory.

    Called once at application startup. Creates the async engine bound
    to the DATABASE_URL from settings and a sessionmaker factory.
    """
    global engine, async_session
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    """Yield an async database session.

    Usage as a FastAPI dependency:
        @app.get("/data")
        async def get_data(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session() as session:
        yield session
