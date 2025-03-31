from datetime import datetime, timezone
from typing import Any, Optional, override

from sqlalchemy import DateTime, Dialect, TypeDecorator, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.operators import OperatorType


class TzAwareSqliteDateTime(TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    @override
    def coerce_compared_value(self, op: OperatorType | None, value: Any) -> Any:
        return self.impl.coerce_compared_value(op, value) # type: ignore
    
    @override
    def process_bind_param(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                raise TypeError('tzinfo is required.')
        return value

    @override
    def process_result_value(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc)
        return value

def enable_foreign_keys(dbapi_connection: DBAPIConnection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()

def register_engine_events(engine: AsyncEngine):
    event.listen(engine.sync_engine, 'connect', enable_foreign_keys)