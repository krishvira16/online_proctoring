import pytest_asyncio
from quart import Quart
from sqlalchemy.ext.asyncio import AsyncEngine

from app import create_app
from app.database import create_engine_manager, create_db_schema_objects


@pytest_asyncio.fixture
async def app():
    app = create_app(use_testing_profile=True)
    engine_manager = create_engine_manager(app)
    async with engine_manager():
        engine: AsyncEngine = getattr(app, 'engine')
        await create_db_schema_objects(engine)
        yield app

@pytest_asyncio.fixture
def test_client(app: Quart):
    return app.test_client()