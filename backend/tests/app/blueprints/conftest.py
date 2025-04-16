import pytest_asyncio
from quart.typing import TestClientProtocol

from app.blueprints.user import UserDetails
from app.blueprints.user.authentication import LoginCredential


@pytest_asyncio.fixture
def user_details():
    return UserDetails(
        username='test_username',
        full_name='test_full_name',
        email='email@test.py',
        password='test_password'
    )

@pytest_asyncio.fixture
async def existing_user_details(test_client: TestClientProtocol, user_details: UserDetails):
    await test_client.post('/user/create_account', json=user_details) # Create a user account
    return user_details

@pytest_asyncio.fixture
async def logged_in_user_details(test_client: TestClientProtocol, existing_user_details: UserDetails):
    login_credential = LoginCredential.from_structural_superset(existing_user_details)
    await test_client.post('/user/authentication/login', json=login_credential)
    return existing_user_details