"""Handle login and downloading from the EarthExplorer portal."""

import os
import re
import shutil

import requests
from tqdm import tqdm

from landsatxplore.api import API
from landsatxplore.exceptions import EarthExplorerError
from landsatxplore.util import guess_dataset, is_product_id


EE_URL = 'https://earthexplorer.usgs.gov/'
EE_LOGIN_URL = 'https://ers.cr.usgs.gov/login/'
EE_LOGOUT_URL = 'https://earthexplorer.usgs.gov/logout'
EE_DOWNLOAD_URL = 'https://earthexplorer.usgs.gov/download/{folder}/{sid}/STANDARD/EE'
EE_FOLDER = {
    'LANDSAT_TM_C1': '12266',
    'LANDSAT_ETM_C1': '12267',
    'LANDSAT_8_C1': '12864'
}
SIZES = {
    'LANDSAT_TM_C1': 150 * 1024**2,
    'LANDSAT_ETM_C1': 235 * 1024**2,
    'LANDSAT_8_C1': 919 * 1024**2
}


def _get_tokens(body):
    """Get `csrf_token` and `__ncforminfo`."""
    csrf = re.findall(r'name="csrf_token" value="(.+?)"', body)
    ncform = re.findall(r'name="__ncforminfo" value="(.+?)"', body)

    if not csrf:
        raise EarthExplorerError('EE: login failed (csrf token not found).')
    if not ncform:
        raise EarthExplorerError('EE: login failed (ncforminfo not found).')

    return csrf, ncform


class EarthExplorer(object):
    """Access Earth Explorer portal."""

    def __init__(self, username, password):
        """Access Earth Explorer portal."""
        self.session = requests.session()
        self.login(username, password)

    def logged_in(self):
        """Check if the log-in has been successfull. Search for
        the log-out URL in the portal html body.
        """
        rsp = self.session.get(EE_URL)
        return EE_LOGOUT_URL in rsp.text

    def login(self, username, password):
        """Login to Earth Explorer."""
        rsp = self.session.get(EE_LOGIN_URL)
        csrf, ncform = _get_tokens(rsp.text)
        payload = {
            'username': username,
            'password': password,
            'csrf_token': csrf,
            '__ncforminfo': ncform}
        rsp = self.session.post(
            EE_LOGIN_URL, data=payload, allow_redirects=False)

        if not self.logged_in():
            raise EarthExplorerError('EE: login failed.')

    def logout(self):
        """Log out from Earth Explorer."""
        self.session.get(EE_LOGOUT_URL)

    def _download(self, url, output_dir, file_size, chunk_size=1024):
        """Download remote file given its URL."""
        with tqdm(total=file_size, unit_scale=True, unit='B') as pbar:
            with self.session.get(url, stream=True, allow_redirects=True) as r:
                local_filename = r.headers['Content-Disposition'].split(
                    '=')[-1]
                local_filename = os.path.join(output_dir, local_filename)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(chunk_size)

    def download(self, scene_id, output_dir):
        """Download a Landsat scene given its identifier and an output
        directory.
        """
        dataset = guess_dataset(scene_id)
        url = EE_DOWNLOAD_URL.format(folder=EE_FOLDER[dataset], sid=scene_id)
        self._download(url, output_dir, file_size=SIZES[dataset])
