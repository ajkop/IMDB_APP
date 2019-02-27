import logging
import csv
import os

from imdb_app import app
from imdb_app.models import db, Titles, Names, KnownFor
from imdb_app.refresh_files import RefreshFiles

logger = logging.getLogger(__name__)


class DBRefresh:
    def __init__(self):
        self.titles_file_full = app.config.get('IMDB_TITLES_FILE')
        self.ratings_file_full = app.config.get('IMDB_RATINGS_FILE')
        self.names_file_full = app.config.get('IMDB_NAMES_FILE')

        # Get the base file name for use in file refresh
        self.titles_file = os.path.basename(self.titles_file_full)
        self.names_file = os.path.basename(self.names_file_full)
        self.ratings_file = os.path.basename(self.ratings_file_full)

    def _gen_rating_dict(self):
        rating_dict = {}
        with open(self.ratings_file_full, 'r') as infile:
            ratings = csv.reader(infile, delimiter='\t')
            next(ratings, None)

            for rating in ratings:
                title_id = rating[0].split('tt')[1]
                rating_dict.update({title_id: {'rating': rating[1], 'num_rating': rating[2]}})
        return rating_dict

    def _get_model_oldest_modified(self, model):
        modified_list = model.query.with_entities(model.last_modified).all()
        if modified_list:
            return min(modified_list)
        return False

    def _get_site_time(self):
        self.refresh = RefreshFiles()
        return self.refresh.modify_time

    def _check_modified_times(self, site_time, model_time):
        if site_time < model_time:
            return True
        return False

    def _check_and_refresh_files(self, model, needed_files=None):
        site_time = self._get_site_time()
        model_time = self._get_model_oldest_modified(model)
        if model_time:
            if self._check_modified_times(site_time, model_time):
                self.refresh.refresh(needed_files=needed_files or [])
        else:
            self.refresh.refresh(needed_files=needed_files or [])

    def _handle_commit(self):
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f'Error encountered during commit, rolling back : {e}')
            db.session.rollback()

    def insert_titles(self, with_commit=True, refresh_files=False):

        model = Titles

        if refresh_files:
            self._check_and_refresh_files(model, needed_files=[self.titles_file, self.ratings_file])

        title_ratings_dict = self._gen_rating_dict()

        with open(self.titles_file_full) as infile:
            titles = csv.reader(infile, delimiter='\t')
            next(titles, None)

            for title in titles:
                title_id = title[0].split('tt')[1]
                try:
                    title_rating = title_ratings_dict[title_id]
                except KeyError:
                    title_rating = {'rating': None, 'num_rating': None}

                title_data = {'id': title_id, 'title_type': title[1], 'name': title[2],
                              'is_adult': True if title[4] == 1 else False, 'release_year': title[5],
                              'end_year': title[6], 'runtime': title[7], 'genres': title[8],
                              'rating': title_rating['rating'], 'num_rating': title_rating['num_rating']}

                title_session = model(**title_data)
                db.session.add(title_session)

        if with_commit:
            self._handle_commit()

    def insert_names(self, with_commit=True, refresh_files=False):
        model = Names

        if refresh_files:
            self._check_and_refresh_files(model, needed_files=[self.names_file])

        with open(self.names_file_full) as infile:
            names = csv.reader(infile, delimiter='\t')
            next(names, None)

            for name in names:
                name_id = names[0].split('tt')[1]
                name_data = {'id': name_id, 'name': name[1], 'birth_year': name[2], 'death_year': name[3],
                             'primary_profession': name[4]}

                name_insert = Names(**name_data)
                db.session.add(name_insert)

        if with_commit:
            self._handle_commit()

    def insert_known_for(self, with_commit=True, refresh_files=False):
        model = KnownFor

        if refresh_files:
            self._check_and_refresh_files(model, needed_files=[self.titles_file, self.names_file, self.ratings_file])

        with open(self.names_file_full) as infile:
            names = csv.reader(infile, delimiter='\t')
            next(names, None)

            for name in names:
                name_id = names[0].split('tt')[1]
                known_fors = name[5].split(',')
                for title in known_fors:
                    title_id = title.split('tt')[1]
                    known_data = {'title_id': title_id, 'name_id': name_id}
                    known_insert = KnownFor(**known_data)
                    db.session.add(known_insert)

        if with_commit:
            self._handle_commit()
