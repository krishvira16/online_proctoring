from os import environ
from pathlib import Path

from quart import Quart
from sqlalchemy import URL


class ProfileConfig:
    def __init__(self, app: Quart) -> None:
        self.DB_URI: str | URL
        self.SECRET_KEY: str
        self.BCRYPT_LOG_ROUNDS: int
        self.BCRYPT_HANDLE_LONG_PASSWORDS: bool = True

    @staticmethod
    def get_postgresql_connect_URL():
        return URL.create(
            drivername='postgresql+asyncpg',
            username=environ['DB_USERNAME'],
            password=environ['DB_PASSWORD'],
            host=environ['DB_HOST'],
            port=int(environ['DB_PORT']),
            database=environ['DB_NAME']
        )

class DevelopmentConfig(ProfileConfig):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        instance_folder = Path(app.instance_path)
        DB_SYSTEM = environ.get('DB_SYSTEM', 'sqlite')
        match DB_SYSTEM:
            case 'sqlite':
                self.DB_URI = URL.create(
                    drivername='sqlite+aiosqlite',
                    database=str(instance_folder/'db.sqlite')
                )
            case 'postgresql':
                self.DB_URI = ProfileConfig.get_postgresql_connect_URL()
            case _:
                raise ValueError(f'Unsupported database system: {DB_SYSTEM}')
        self.SECRET_KEY = 'dev'
        environ['QUART_DEBUG'] = 'True'
        self.QUART_AUTH_COOKIE_SECURE = False
        self.BCRYPT_LOG_ROUNDS = 4
        
        @app.cli.command('create_instance_folder')
        def create_instance_folder():
            instance_folder.mkdir(parents=True)

class TestingConfig(DevelopmentConfig):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        self.TESTING: bool = True
        self.DB_URI: str = 'sqlite+aiosqlite:///:memory:'

class ProductionConfig(ProfileConfig):
    def __init__(self, app: Quart) -> None:
        super().__init__(app)
        self.DB_URI = ProfileConfig.get_postgresql_connect_URL()
        self.SECRET_KEY = environ['QUART_SECRET_KEY']
        self.BCRYPT_LOG_ROUNDS = int(environ['BCRYPT_LOG_ROUNDS'])

profile_config_type: dict[str, type[ProfileConfig]] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}