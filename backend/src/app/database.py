from contextlib import asynccontextmanager
from os import environ

from fastapi import FastAPI
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel


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
        await conn.run_sync(SQLModel.metadata.create_all)
    yield