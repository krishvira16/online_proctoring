from os import environ
from pathlib import Path

from quart import Quart
from sqlalchemy import URL


class Config:
    def __init__(self, app: Quart) -> None:
        self.DB_URI: str | URL
        self.SECRET_KEY: str
        self.BCRYPT_LOG_ROUNDS: int
        self.BCRYPT_HANDLE_LONG_PASSWORDS: bool = True

class DevelopmentConfig(Config):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        instance_folder = Path(app.instance_path)
        self.DB_URI = URL.create(
            drivername='sqlite+aiosqlite',
            database=str(instance_folder/'db.sqlite')
        )
        self.SECRET_KEY = 'dev'
        environ['QUART_DEBUG'] = 'True'
        self.QUART_AUTH_COOKIE_SECURE = False
        self.BCRYPT_LOG_ROUNDS = 4
        
        @app.cli.command('create-instance-folder')
        def create_instance_folder():
            instance_folder.mkdir(parents=True)

class TestingConfig(DevelopmentConfig):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        self.TESTING: bool = True
        self.DB_URI: str = 'sqlite+aiosqlite:///:memory:'

class ProductionConfig(Config):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        self.DB_URI = URL.create(
            drivername='mysql+aiomysql',
            username=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            host=environ['DB_HOST'],
            port=int(environ['DB_PORT']),
            database=environ['DB_NAME']
        )
        self.SECRET_KEY = environ['QUART_SECRET_KEY']
        self.BCRYPT_LOG_ROUNDS = int(environ['BCRYPT_LOG_ROUNDS'])

profile_config_type: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}