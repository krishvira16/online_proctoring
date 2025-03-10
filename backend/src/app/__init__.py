import importlib
from os import environ

from quart import Quart
from quart_auth import QuartAuth
from quart_schema import QuartSchema

from .default_config import profile_config_type
from . import database
from . import password_hashing
from . import error_handling
from . import blueprints


def create_app(use_testing_profile: bool = False):
    app = Quart(__name__)
    
    profile = 'testing' if use_testing_profile else environ['PROFILE']
    config_type = profile_config_type[profile]
    config = config_type(app)
    app.config.from_object(config)

    database.init_app(app)

    password_hashing.init_app(app)
    auth_manager = QuartAuth(app) # type: ignore
    setattr(app, 'auth_manager', auth_manager)

    QuartSchema(app, convert_casing=True)

    error_handling.init_app(app)
    
    for blueprint_module_name in blueprints.__all__:
        blueprint_module = importlib.import_module(f'.{blueprint_module_name}', package=blueprints.__name__)
        app.register_blueprint(blueprint_module.bp)

    return app