from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import wraps
from typing import Self

from quart import Blueprint, Response, current_app, g
import quart_auth
from quart_auth import AuthUser, Unauthorized, login_required, login_user, logout_user
from quart_schema import validate_querystring, validate_request
from sqlalchemy import select
from werkzeug.local import LocalProxy

from ...data_model import User
from ...database import orm_session
from ...error_handling import APIError, handle_api_error
from ...password_hashing import check_password_hash, mitigate_against_timing_attack
from . import UserDetails


bp = Blueprint('authentication', __name__, url_prefix='/authentication')

@dataclass
class LoginCredential:
    username: str
    password: str

    @classmethod
    def from_structural_superset(cls, user_details: UserDetails) -> Self:
        return cls(
            username=user_details.username,
            password=user_details.password
        )

class InvalidCredentialError(APIError):
    def __init__(self):
        super().__init__(401, 'Invalid credential')

@dataclass
class RememberMeOption:
    remember: bool = False

@bp.post('/login')
@validate_request(LoginCredential)
@validate_querystring(RememberMeOption)
async def login(data: LoginCredential, query_args: RememberMeOption):
    result = (await orm_session.execute(
        select(User.id, User.password_hash).where(User.username == data.username)
    )).one_or_none()
    if result is None:
        await mitigate_against_timing_attack()
        raise InvalidCredentialError
    else:
        user_id, password_hash = result._tuple()
        if await check_password_hash(password_hash, data.password):
            login_user(AuthUser(str(user_id)), remember=query_args.remember)
            return Response(status=204)
        else:
            raise InvalidCredentialError

@login_required
async def ensure_authenticated():
    current_user_id = int(quart_auth.current_user.auth_id) # type: ignore
    current_user = await orm_session.get(User, current_user_id)
    if current_user is None:
        # Handle case where the user account has been deleted but the session cookie is still valid:
        logout_user()
        raise APIError(401, 'Unauthorised')
    g.current_user = current_user

def authentication_required[T, **P](func: Callable[P, Awaitable[T]] | Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        await ensure_authenticated()
        return await current_app.ensure_async(func)(*args, **kwargs) # type: ignore
    return wrapper

@bp.app_errorhandler(Unauthorized)
async def handle_unauthorized_error(e: Unauthorized):
    return await handle_api_error(APIError(401, 'Unauthorised'))

def get_current_user() -> User:
    if 'current_user' not in g:
        raise RuntimeError('Cannot get the current user outside of an authenticated context.')
    return g.current_user

current_user: User = LocalProxy(get_current_user) # type: ignore

@bp.post('/logout')
async def logout():
    logout_user()
    return Response(status=204)