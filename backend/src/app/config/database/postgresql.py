from sqlalchemy import event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.ext.asyncio import AsyncEngine


def set_timezone_to_utc(dbapi_connection: DBAPIConnection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('SET TIMEZONE TO "UTC"')
    cursor.close()

def register_engine_events(engine: AsyncEngine):
    event.listen(engine.sync_engine, 'connect', set_timezone_to_utc)