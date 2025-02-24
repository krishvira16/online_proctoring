from contextlib import asynccontextmanager
from os import environ
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession

from .data_model import Base


mysql_url = URL.create(
    drivername='mysql+aiomysql',
    username=environ['DB_USERNAME'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=int(environ['DB_PORT']),
    database=environ['DB_NAME']
)

engine: None | AsyncEngine = None

@asynccontextmanager
async def create_engine(app: FastAPI):
    global engine
    engine = create_async_engine(
        mysql_url,
        echo=True,
        pool_pre_ping=True
    )
    yield
    await engine.dispose()

@asynccontextmanager
async def create_db_and_tables(app: FastAPI):
    if engine is None:
        raise Exception('`engine` should be created before calling this function.')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

async def get_session():
    async with AsyncSession(engine) as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]