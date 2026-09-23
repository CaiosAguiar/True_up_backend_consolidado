from flask import Flask
from .config import Config
from .db import build_engine
from .errors import register_errors
from .security import register_security
from .routes import blueprints

def create_app(config_object=Config,engine=None):
    app=Flask(__name__); app.config.from_object(config_object)
    if not app.config.get('TESTING'):
        for key in ('SECRET_KEY','DATABASE_URL','OWNER_TOKEN','OWNER_ID'):
            if not app.config.get(key): raise RuntimeError(f'{key} nao configurada')
    app.extensions['db_engine']=engine or build_engine(app.config)
    register_security(app); register_errors(app)
    for bp in blueprints: app.register_blueprint(bp)
    return app
