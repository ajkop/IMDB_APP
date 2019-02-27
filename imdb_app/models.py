from datetime import datetime

from imdb_app import db


class Titles(db.Model):
    __tablename__ = 'titles'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    release_year = db.Column(db.String(80))
    end_year = db.Column(db.String(80))
    genres = db.Column(db.String(255))
    rating = db.Column(db.Float)
    num_rating = db.Column(db.Integer)
    runtime = db.Column(db.Integer, default=0)
    is_adult = db.Column(db.Boolean, default=False)
    title_type = db.Column(db.String(80))
    owned = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnownFor(db.Model):
    __tablename__ = 'known_for'

    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.BigInteger, db.ForeignKey('titles.id'), nullable=False)
    title = db.relationship('Titles', backref=db.backref('appears_in', lazy=True))
    name_id = db.Column(db.BigInteger, db.ForeignKey('names.id'), nullable=False)
    name = db.relationship('Names', backref=db.backref('known_for', lazy=True))
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Names(db.Model):
    __tablename = 'names'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255))
    birth_year = db.Column(db.String(255))
    death_year = db.Column(db.String(255))
    primary_profession = db.Column(db.String(255))
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
