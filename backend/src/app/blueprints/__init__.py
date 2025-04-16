from typing import Protocol

from quart import Blueprint


class BlueprintModule(Protocol):
    bp: Blueprint

from . import user  # noqa: E402

bp_modules: list[BlueprintModule] = [
    user,
]