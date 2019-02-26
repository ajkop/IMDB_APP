from setuptools import setup

setup(
    name='IMDBP_APP',
    version='1.0',
    packages=['bs4', 'click', 'Flask', 'Flask-SQLAlchemy', 'requests', 'urllib3', 'Flask-Caching'],
    url='https://thevoid.space',
    license='MIT',
    author='AJ Kop',
    author_email='aj.kopczynski@gmail.com',
    description='A Flask app containing public IMDB data'
)
