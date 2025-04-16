from dataclasses import dataclass

from quart import Quart, jsonify


@dataclass
class APIError(Exception):
    status_code: int
    description: str

async def handle_api_error(e: APIError):
    return jsonify(e.description), e.status_code

def init_app(app: Quart):
    app.register_error_handler(APIError, handle_api_error)