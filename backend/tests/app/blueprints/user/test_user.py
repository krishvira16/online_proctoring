from copy import replace

from quart import Quart
import quart.typing
from sqlalchemy import select

from app.blueprints.user import UserDetails
from app.data_model import User
from app.database import orm_session


class TestCreateAccount:
    async def test_create_account(self, app: Quart, test_client: quart.typing.TestClientProtocol, user_details: UserDetails):
        response = await test_client.post('/user/create_account', json=user_details)
        assert response.status_code == 201
        response_body = await response.get_json()
        assert response_body is None
        async with app.app_context():
            saved_user_id = await orm_session.scalar(select(User.id).where(User.username == user_details.username))
            assert saved_user_id is not None
    
    async def test_duplicate_username_error(self, test_client: quart.typing.TestClientProtocol, existing_user_details: UserDetails):
        # Attempt to create a new user account (with duplicate username):
        new_user_details = replace(existing_user_details, email='email2@test.py')
        response = await test_client.post('/user/create_account', json=new_user_details)
        assert response.status_code == 422
        response_body = await response.get_json()
        assert response_body == 'Username is already taken up.'
    
    async def test_duplicate_email_error(self, test_client: quart.typing.TestClientProtocol, existing_user_details: UserDetails):
        # Attempt to create a new user account (with duplicate email address):
        new_user_details = replace(existing_user_details, username='test_username2')
        response = await test_client.post('/user/create_account', json=new_user_details)
        assert response.status_code == 422
        response_body = await response.get_json()
        assert response_body == 'E-mail address is already registered.'