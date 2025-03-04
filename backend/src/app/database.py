import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from functools import wraps

import click
from quart import Quart, current_app, g
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from werkzeug.local import LocalProxy

from .data_model import Base


async def create_engine():
    engine = create_async_engine(
        current_app.config['DB_URI'],
        echo=True,
        pool_pre_ping=True
    )
    setattr(current_app, 'engine', engine)
    yield
    await engine.dispose()

def get_orm_session() -> AsyncSession:
    if 'session' not in g:
        engine: AsyncEngine = getattr(current_app, 'engine')
        g.session = AsyncSession(engine)
    return g.session

async def close_orm_session(e = None):
    session: AsyncSession = g.pop('session', None)
    if session is not None:
        await session.close()

orm_session = LocalProxy(get_orm_session)

def transactional[T, **P](func: Callable[P, Awaitable[T]] | Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        async with orm_session.begin():
            return await current_app.ensure_async(func)(*args, **kwargs) # type: ignore
    return wrapper

def init_app(app: Quart):
    app.while_serving(create_engine)

    @click.command('init-db')
    def create_db_and_tables():
        async def _create_db_and_tables():
            async with app.app_context():
                async with asynccontextmanager(create_engine)():
                    engine: AsyncEngine = getattr(current_app, 'engine')
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
        
        asyncio.get_event_loop().run_until_complete(_create_db_and_tables())
    
    app.cli.add_command(create_db_and_tables)

    app.teardown_appcontext(close_orm_session)