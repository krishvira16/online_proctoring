from dataclasses import dataclass

from quart import Blueprint, current_app
from quart_bcrypt import Bcrypt
from quart_schema import validate_request
from sqlalchemy import select

from ..data_model import User
from ..database import get_orm_session, transactional
from ..error_handling import APIError


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

    bcrypt: Bcrypt = getattr(current_app, 'bcrypt')
    password_hash = (await bcrypt.async_generate_password_hash(data.password)).decode('utf-8')
    new_user = User(
        data.username,
        full_name=data.full_name,
        email=data.email,
        password_hash=password_hash
    )
    orm_session.add(new_user)
    return 'Account created successfully', 201