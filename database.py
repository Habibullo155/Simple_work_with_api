from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import declarative_base

Base = declarative_base()

db_url = "sqlite+aiosqlite:///database.db"

engine = create_async_engine(db_url, echo=True)
async_session = async_sessionmaker(engine,class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as db:
        yield db
