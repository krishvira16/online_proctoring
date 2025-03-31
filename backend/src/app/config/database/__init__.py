from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncEngine

from . import postgresql


class EngineEventRegistrar(Protocol):
    def register_engine_events(self, engine: AsyncEngine) -> None:
        ...

engine_event_registrar: dict[str, EngineEventRegistrar] = {
    'postgresql': postgresql
}