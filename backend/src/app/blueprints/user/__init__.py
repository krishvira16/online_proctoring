from dataclasses import dataclass

from quart import Blueprint, Response
from quart_schema import validate_request
from sqlalchemy import select

from ...data_model import User
from ...database import get_orm_session, transactional
from ...error_handling import APIError
from ...password_hashing import generate_password_hash


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

from .. import BlueprintModule  # noqa: E402
from . import authentication, current  # noqa: E402

bp_modules: list[BlueprintModule] = [
    authentication,
    current,
]

for bp_module in bp_modules:
    bp.register_blueprint(bp_module.bp)