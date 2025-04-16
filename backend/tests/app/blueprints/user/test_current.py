from dataclasses import asdict

from humps import camelize
import quart.typing

from app.blueprints.user import UserDetails
from app.blueprints.user.current import UserDetailsWithoutPasswordHash


class TestGetDetails:
    async def test_get_details(self, test_client: quart.typing.TestClientProtocol, logged_in_user_details: UserDetails):
        response = await test_client.get('/user/details', json=logged_in_user_details)
        assert response.status_code == 200
        response_body = await response.get_json()
        logged_in_user_details_without_password_hash = UserDetailsWithoutPasswordHash.from_structural_superset(logged_in_user_details)
        assert response_body == camelize(asdict(logged_in_user_details_without_password_hash))
    
    async def test_unauthenticated_error(self, test_client: quart.typing.TestClientProtocol, existing_user_details: UserDetails):
        response = await test_client.get('/user/details', json=existing_user_details)
        assert response.status_code == 401
        response_body = await response.get_json()
        assert response_body == 'Unauthorised'