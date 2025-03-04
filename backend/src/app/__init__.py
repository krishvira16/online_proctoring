from collections.abc import Mapping
import importlib
from os import environ
from pathlib import Path
from typing import Any, Optional

from quart import Quart
from quart_bcrypt import Bcrypt
from quart_auth import QuartAuth
from quart_schema import QuartSchema

from .default_config import profiles
from . import database
from . import error_handling
from . import blueprints


def create_app(testing_config: Optional[Mapping[str, Any]] = None):
    app = Quart(__name__)
    
    instance_folder = Path(app.instance_path)
    
    @app.cli.command('create-instance-folder')
    def create_instance_folder():
        instance_folder.mkdir(parents=True)
    
    config_type = profiles[environ['PROFILE']]
    config = config_type(instance_folder=instance_folder)
    app.config.from_object(config)

    if testing_config is not None:
        app.config.from_mapping(testing_config)
    
    database.init_app(app)

    QuartSchema(app, convert_casing=True)

    bcrypt = Bcrypt(app)
    setattr(app, 'bcrypt', bcrypt)
    QuartAuth(app) # type: ignore

    error_handling.init_app(app)
    
    for blueprint_module_name in blueprints.__all__:
        blueprint_module = importlib.import_module(f'.{blueprint_module_name}', package=blueprints.__name__)
        app.register_blueprint(blueprint_module.bp)

    return app