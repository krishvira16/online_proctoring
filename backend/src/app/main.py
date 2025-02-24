from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_db_and_tables, create_engine
from . import data_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with create_engine(app):
        async with create_db_and_tables(app):
            yield

app = FastAPI(lifespan=lifespan)