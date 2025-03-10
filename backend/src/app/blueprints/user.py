from dataclasses import dataclass

from quart import Blueprint, Response
from quart_auth import AuthUser, login_user, logout_user
from quart_schema import validate_querystring, validate_request
from sqlalchemy import select

from ..data_model import User
from ..database import get_orm_session, orm_session, transactional
from ..error_handling import APIError
from ..password_hashing import check_password_hash, generate_password_hash, mitigate_against_timing_attack


bp = Blueprint('user', __name__, url_prefix='/user')

@dataclass
class UserDetails:
    username: str
    full_name: str
    email: str
    password: str

@bp.post('/create_account')
@validate_request(UserDetails)
@transactional
async def create_account(data: UserDetails):
    orm_session = get_orm_session()
    
    existing_username = await orm_session.scalar(
        select(User.username).where(User.username == data.username)
    )
    if existing_username is not None:
        raise APIError(422, 'Username is already taken up.')
    
    existing_email = await orm_session.scalar(
        select(User.email).where(User.email == data.email)
    )
    if existing_email is not None:
        raise APIError(422, 'E-mail address is already registered.')

    password_hash = await generate_password_hash(data.password)
    new_user = User(
        data.username,
        full_name=data.full_name,
        email=data.email,
        password_hash=password_hash
    )
    orm_session.add(new_user)
    return Response(status=201)

@dataclass
class LoginCredential:
    username: str
    password: str

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

@bp.post('/logout')
async def logout():
    logout_user()
    return Response(status=204)