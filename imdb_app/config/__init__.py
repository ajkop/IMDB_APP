class BaseConfig(object):
    DEBUG = False
    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://imdb_sqlalc:OmErmiNDefac@localhost/einventory'

    IMDB_DOWNLOAD_URL = 'https://datasets.imdbws.com'
    IMDB_DATA_DOWNLOAD_DIR = '/root/imdb-data/'
    IMDB_TITLES_FILE = f'{IMDB_DATA_DOWNLOAD_DIR}/title.basics.tsv'
    IMDB_NAMES_FILE = f'{IMDB_DATA_DOWNLOAD_DIR}/name.basics.tsv'
    IMDB_RATINGS_FILE = f'{IMDB_DATA_DOWNLOAD_DIR}/title.ratings.tsv'
