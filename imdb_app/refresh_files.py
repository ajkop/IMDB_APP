import os
import requests
import shutil
import gzip
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from imdb_app.exceptions import FileRefreshError
from imdb_app import app


class RefreshFiles:

    def __init__(self):
        self.site_url = app.config.get('IMDB_DOWNLOAD_URL')
        self.put_dir = app.config.get('IMDB_DATA_DOWNLOAD_DIR', '/root/')

        self.site = requests.get(self.site_url)
        if self.site.status_code != 200:
            raise FileRefreshError(f'Unable to load IMDB content URL: {self.site_url}. Status Code is '
                                   f'{self.site.status_code}')

    @property
    def modify_time(self):
        try:
            return self.site.headers['Last-Modified']
        except KeyError:
            return False

    def _get_links(self):
        soup = BeautifulSoup(self.site.text, 'html.parser')
        link_list = []
        for a in soup.find_all('a', href=True, text=True):
            link_text = a['href']
            if ".gz" in link_text:
                link_list.append(link_text)
        return link_list

    def _get_files_to_download(self, file_links, needed_files=None):
        found_file_map = {}
        download_files_dict = {}
        for url in file_links:
            parsed_file = urlparse(url).path.strip('/')
            found_file_map.update({parsed_file.rstrip('.gz'): {'url': url, 'parsed_file': parsed_file}})

        for unzipped, value_dict in found_file_map.items():
            if needed_files:
                if unzipped in needed_files:
                    download_files_dict.update({unzipped: value_dict})
            else:
                download_files_dict.update({unzipped: value_dict})

        # Ensure we collected all the requested files.
        if needed_files:
            if not all([needed_file in download_files_dict for needed_file in needed_files]):
                raise FileRefreshError('One or more requested files were not found on the site.')

        return download_files_dict

    def _download_files(self, files_map):
        parsed_files = {}

        for unzipped, values in files_map.items():
            zipped = values['parsed_file']
            r = requests.get(values['url'], allow_redirects=True)

            with open(f'{self.put_dir}/{zipped}', 'wb') as write_file:
                write_file.write(r.content)

            parsed_files.update({zipped: unzipped})
        return parsed_files

    def _unzip_files(self, file_map):
        for key, value in file_map.items():
            with gzip.open(f'{self.put_dir}/{key}', 'rb') as in_file:
                with open(f'{self.put_dir}/{value}', 'wb') as out_file:
                    shutil.copyfileobj(in_file, out_file)
            os.remove(f'{self.put_dir}/{key}')

    def refresh(self, needed_files=None):
        file_links = self._get_links()
        download_files_map = self._get_files_to_download(file_links, needed_files=needed_files)
        file_map = self._download_files(download_files_map)
        self._unzip_files(file_map)
