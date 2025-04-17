from dataclasses import dataclass
from typing import Self

from quart import Blueprint
from quart_schema import validate_response

from ...data_model import User
from .authentication import ensure_authenticated, current_user


bp = Blueprint('current', __name__)
bp.before_request(ensure_authenticated)

@dataclass
class UserDetailsWithoutPasswordHash:
    username: str
    full_name: str
    email: str
    test_setter_role: bool
    test_taker_role: bool
    invigilator_role: bool

    @classmethod
    async def from_structural_superset(cls, user: User) -> Self:
        return cls(
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            test_setter_role=await user.awaitable_attrs.test_setter_role is not None,
            test_taker_role=await user.awaitable_attrs.test_taker_role is not None,
            invigilator_role=await user.awaitable_attrs.invigilator_role is not None
        )

@bp.get('/details') # type: ignore
@validate_response(UserDetailsWithoutPasswordHash)
async def get_details() -> UserDetailsWithoutPasswordHash:
    return await UserDetailsWithoutPasswordHash.from_structural_superset(current_user)