import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

from imdb_app.exceptions import MissingConfigError
from imdb_app.config import BaseConfig

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
app.config.from_object(BaseConfig)

secret_file = os.environ.get('IMDB_SECRET')
if secret_file:
    try:
        os.stat(secret_file)
    except FileNotFoundError:
        raise MissingConfigError(f'No file found at {secret_file}')
else:
    raise MissingConfigError(f'No secret file specified for app, please make one and set the Env variable to '
                             f'"IMDB_SECRET"')

app.config.from_pyfile(secret_file)

db = SQLAlchemy(app)
