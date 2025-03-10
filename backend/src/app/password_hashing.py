from quart import Quart, current_app
from quart_bcrypt import Bcrypt


async def generate_password_hash(password: str):
    bcrypt: Bcrypt = getattr(current_app, 'bcrypt')
    password_hash_bytes = await bcrypt.async_generate_password_hash(password)
    return password_hash_bytes.decode('utf-8')

async def check_password_hash(password_hash: str, password: str):
    bcrypt: Bcrypt = getattr(current_app, 'bcrypt')
    return await bcrypt.async_check_password_hash(password_hash, password)

async def mitigate_against_timing_attack():
    """Simulate a password checking operation, to protect against timing attacks."""
    bcrypt: Bcrypt = getattr(current_app, 'bcrypt')
    timeholder_password: str = getattr(current_app, 'timeholder_password')
    timeholder_password_hash: str = getattr(current_app, 'timeholder_password_hash')
    await bcrypt.async_check_password_hash(timeholder_password_hash, timeholder_password)

def init_app(app: Quart):
    bcrypt = Bcrypt(app)
    setattr(app, 'bcrypt', bcrypt)
    timeholder_password = 'timeholder password'
    timeholder_password_hash = bcrypt.generate_password_hash(timeholder_password).decode('utf-8')
    setattr(app, 'timeholder_password', timeholder_password)
    setattr(app, 'timeholder_password_hash', timeholder_password_hash)