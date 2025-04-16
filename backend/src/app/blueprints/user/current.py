from dataclasses import dataclass
from typing import Self

from quart import Blueprint
from quart_schema import validate_response

from ...data_model import User
from . import UserDetails
from .authentication import ensure_authenticated, current_user


bp = Blueprint('current', __name__)
bp.before_request(ensure_authenticated)

@dataclass
class UserDetailsWithoutPasswordHash:
    username: str
    full_name: str
    email: str

    @classmethod
    def from_structural_superset(cls, user: User | UserDetails) -> Self:
        return cls(
            username=user.username,
            full_name=user.full_name,
            email=user.email
        )

@bp.get('/details') # type: ignore
@validate_response(UserDetailsWithoutPasswordHash)
async def get_details() -> UserDetailsWithoutPasswordHash:
    return UserDetailsWithoutPasswordHash.from_structural_superset(current_user)