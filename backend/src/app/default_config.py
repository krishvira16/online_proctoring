from dataclasses import InitVar, dataclass, field
from os import environ
from pathlib import Path

from sqlalchemy import URL


@dataclass
class Config:
    instance_folder: InitVar[Path]
    DB_URI: str | URL = field(init=False)
    SECRET_KEY: str = field(default=environ['QUART_SECRET_KEY'], init=False)
    BCRYPT_LOG_ROUNDS: int = field(init=False)
    BCRYPT_HANDLE_LONG_PASSWORDS: bool = field(default=True, init=False)

@dataclass
class DevelopmentConfig(Config):
    def __post_init__(self, instance_folder: Path):
        self.DB_URI = URL.create(
            drivername='sqlite+aiosqlite',
            database=str(instance_folder/'db.sqlite')
        )
        environ['QUART_DEBUG'] = 'True'
        self.QUART_AUTH_COOKIE_SECURE = False
        self.BCRYPT_LOG_ROUNDS = 4

@dataclass
class ProductionConfig(Config):
    def __post_init__(self, *args, **kw_args):
        self.DB_URI = URL.create(
            drivername='mysql+aiomysql',
            username=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            host=environ['DB_HOST'],
            port=int(environ['DB_PORT']),
            database=environ['DB_NAME']
        )
        self.BCRYPT_LOG_ROUNDS = int(environ['BCRYPT_LOG_ROUNDS'])

profiles: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}