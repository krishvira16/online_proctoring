from os import environ

from quart import Quart
from quart_auth import QuartAuth
from quart_cors import cors
from quart_schema import QuartSchema

from . import blueprints, database, error_handling, password_hashing
from .config.profile import profile_config_type


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

    app = cors(app)

    QuartSchema(app, convert_casing=True)

    error_handling.init_app(app)
    
    for bp_module in blueprints.bp_modules:
        app.register_blueprint(bp_module.bp)

    return app