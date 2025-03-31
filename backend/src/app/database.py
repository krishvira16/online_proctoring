import asyncio
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from functools import wraps

from quart import Quart, current_app, g
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from werkzeug.local import LocalProxy

from .config.database import engine_event_registrar
from .data_model import Base


def create_engine_manager(app: Quart):
    @asynccontextmanager
    async def engine_manager():
        engine = create_async_engine(
            app.config['DB_URI'],
            echo=True,
            pool_pre_ping=True
        )
        engine_event_registrar[engine.name].register_engine_events(engine)
        setattr(app, 'engine', engine)
        yield
        await engine.dispose()
    
    return engine_manager

async def create_db_schema_objects(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db_schema_objects(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

def get_orm_session() -> AsyncSession:
    if 'orm_session' not in g:
        engine: AsyncEngine = getattr(current_app, 'engine')
        g.orm_session = AsyncSession(engine)
    return g.orm_session

async def close_orm_session(e = None):
    orm_session: AsyncSession = g.pop('orm_session', None)
    if orm_session is not None:
        await orm_session.close()

orm_session: AsyncSession = LocalProxy(get_orm_session) # type: ignore

def transactional[T, **P](func: Callable[P, Awaitable[T]] | Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        async with orm_session.begin():
            return await current_app.ensure_async(func)(*args, **kwargs) # type: ignore
    return wrapper

def init_app(app: Quart):
    engine_manager = create_engine_manager(app)
    
    @app.while_serving
    async def manage_engine():
        async with engine_manager():
            yield

    @app.cli.command('create_db_schema_objects')
    def _create_db_schema_objects_command():
        async def create_db_schema_objects_command():
            async with engine_manager():
                engine: AsyncEngine = getattr(app, 'engine')
                await create_db_schema_objects(engine)
        
        asyncio.get_event_loop().run_until_complete(create_db_schema_objects_command())

    @app.cli.command('drop_db_schema_objects')
    def _drop_db_schema_objects_command():
        async def drop_db_schema_objects_command():
            async with engine_manager():
                engine: AsyncEngine = getattr(app, 'engine')
                await drop_db_schema_objects(engine)
        
        asyncio.get_event_loop().run_until_complete(drop_db_schema_objects_command())
    
    app.teardown_appcontext(close_orm_session)