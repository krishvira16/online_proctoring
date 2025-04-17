from typing import Protocol

from quart import Blueprint


class BlueprintModule(Protocol):
    bp: Blueprint

from . import user, test_setter  # noqa: E402

bp_modules: list[BlueprintModule] = [
    user,
    test_setter,
]