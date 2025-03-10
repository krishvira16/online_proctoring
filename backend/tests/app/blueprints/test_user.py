from copy import replace
from datetime import datetime, timedelta

import pytest
from quart import Quart
from quart.typing import TestClientProtocol
from quart_auth import QuartAuth, generate_auth_token
from sqlalchemy import select

from app.blueprints.user import LoginCredential, UserDetails
from app.data_model import User
from app.database import orm_session


class TestCreateAccount:
    async def test_create_account(self, app: Quart, test_client: TestClientProtocol, user_details: UserDetails):
        response = await test_client.post('/user/create_account', json=user_details)
        assert response.status_code == 201
        response_body = await response.get_json()
        assert response_body is None
        async with app.app_context():
            saved_user_id = await orm_session.scalar(select(User.id).where(User.username == user_details.username))
            assert saved_user_id is not None
    
    async def test_duplicate_username_error(self, test_client: TestClientProtocol, existing_user_details: UserDetails):
        # Attempt to create a new user account (with duplicate username):
        new_user_details = replace(existing_user_details, email='email2@test.py')
        response = await test_client.post('/user/create_account', json=new_user_details)
        assert response.status_code == 422
        response_body = await response.get_json()
        assert response_body == 'Username is already taken up.'
    
    async def test_duplicate_email_error(self, test_client: TestClientProtocol, existing_user_details: UserDetails):
        # Attempt to create a new user account (with duplicate email address):
        new_user_details = replace(existing_user_details, username='test_username2')
        response = await test_client.post('/user/create_account', json=new_user_details)
        assert response.status_code == 422
        response_body = await response.get_json()
        assert response_body == 'E-mail address is already registered.'

def get_client_auth_cookie(test_client: TestClientProtocol, auth_manager: QuartAuth):
    for cookie in list(test_client.cookie_jar):  # type: ignore
        if (
            not cookie.domain_specified 
            and cookie.path == auth_manager.cookie_path 
            and cookie.name == auth_manager.cookie_name
        ):
            return cookie
    else:
        return None

class TestLogin:
    @pytest.mark.parametrize('remember', [False, True])
    async def test_successful_login(self, app: Quart, test_client: TestClientProtocol, existing_user_details: UserDetails, remember: bool):
        test_client.cookie_jar.clear() # type: ignore
        login_credential = LoginCredential(
            username=existing_user_details.username,
            password=existing_user_details.password
        )
        response = await test_client.post(f'/user/login?remember={remember}', json=login_credential)
        assert response.status_code == 204
        response_body = await response.get_json()
        assert response_body is None
        auth_manager: QuartAuth = getattr(app, 'auth_manager')
        auth_cookie = get_client_auth_cookie(test_client, auth_manager)
        assert auth_cookie is not None
        async with app.app_context():
            user_id = await orm_session.scalar(select(User.id).where(User.username == login_credential.username))
            assert auth_cookie.value == generate_auth_token(test_client, str(user_id))
        if remember:
            assert auth_cookie.discard is False
            # Verify that the duration of the set cookie is approximately `auth_manager.duration` seconds from now (upto a precision of 1 minute).
            assert (datetime.fromtimestamp(auth_cookie.expires) - datetime.now()) - timedelta(seconds=auth_manager.duration) < timedelta(minutes=1) # type: ignore
        else:
            assert auth_cookie.discard is True

    async def test_non_existant_username(self, test_client: TestClientProtocol, existing_user_details: UserDetails):
        login_credential = LoginCredential(
            username='some_username',
            password=existing_user_details.password
        )
        response = await test_client.post('/user/login', json=login_credential)
        assert response.status_code == 401
        response_body = await response.get_json()
        assert response_body == 'Invalid credential'
    
    async def test_invalid_password(self, test_client: TestClientProtocol, existing_user_details: UserDetails):
        login_credential = LoginCredential(
            username=existing_user_details.username,
            password='some_password'
        )
        response = await test_client.post('/user/login', json=login_credential)
        assert response.status_code == 401
        response_body = await response.get_json()
        assert response_body == 'Invalid credential'

class TestLogout:
    async def test_logout(self, app: Quart, test_client: TestClientProtocol, logged_in_user_details: UserDetails):
        response = await test_client.post('/user/logout')
        assert response.status_code == 204
        response_body = await response.get_json()
        assert response_body is None
        auth_manager: QuartAuth = getattr(app, 'auth_manager')
        auth_cookie = get_client_auth_cookie(test_client, auth_manager)
        assert auth_cookie is None