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

    def _download_files(self, file_links, needed_files=None):
        parsed_files = {}
        download_files = {}
        for url in file_links:
            parsed_file = urlparse(url).path.strip('/')
            unzipped_file_name = parsed_file.rstrip('.gz')
            if needed_files:
                if unzipped_file_name in needed_files:
                    download_files = {url: {'parsed_file': parsed_file, 'unzipped_file_name': unzipped_file_name}}
                    break
                else:
                    raise FileRefreshError(f'One or more of the requested files not on site: {parsed_file}')
            else:
                download_files.update({url: {'parsed_file': parsed_file, 'unzipped_file_name': unzipped_file_name}})

        for url, values in download_files.items():
            r = requests.get(url, allow_redirects=True)
            with open(f'self.put_dir/file', 'wb') as write_file:
                write_file.write(r.content)
            parsed_files.update({values['parsed_file']: values['unzipped_file_name']})
        return parsed_files

    def _unzip_files(self, file_map):
        for key, value in file_map.items():
            with gzip.open(f'{self.put_dir}/{key}', 'rb') as in_file:
                with open(f'{self.put_dir}/{value}', 'wb') as out_file:
                    shutil.copyfileobj(in_file, out_file)
            os.remove(f'{self.put_dir}/{key}')

    def refresh(self, needed_files=None):
        file_links = self._get_links()
        file_map = self._download_files(file_links, needed_files=needed_files)
        self._unzip_files(file_map)
