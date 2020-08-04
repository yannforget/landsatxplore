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
EE_DOWNLOAD_URL = "https://earthexplorer.usgs.gov/download/{dataset_id}/{scene_id}/EE/"
DATASETS = {
    "LANDSAT_TM_C1": "5e83d08fd9932768",
    "LANDSAT_ETM_C1": "5e83a507d6aaa3db",
    "LANDSAT_8_C1": "5e83d0b84df8d8c2"
}


def _get_tokens(body):
    """Get `csrf_token` and `__ncforminfo`."""
    csrf = re.findall(r'name="csrf" value="(.+?)"', body)[0]
    ncform = re.findall(r'name="__ncforminfo" value="(.+?)"', body)[0]

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
        self.api = API(username, password)

    def logged_in(self):
        """Check if the log-in has been successfull based on session cookies."""
        eros_sso = self.session.cookies.get("EROS_SSO_production_secure")
        return bool(eros_sso)

    def login(self, username, password):
        """Login to Earth Explorer."""
        rsp = self.session.get(EE_LOGIN_URL)
        csrf, ncform = _get_tokens(rsp.text)
        payload = {
            'username': username,
            'password': password,
            'csrf': csrf,
            '__ncforminfo': ncform}
        rsp = self.session.post(
            EE_LOGIN_URL, data=payload, allow_redirects=True)

        if not self.logged_in():
            raise EarthExplorerError('EE: login failed.')

    def logout(self):
        """Log out from Earth Explorer."""
        self.session.get(EE_LOGOUT_URL)

    def _download(self, url, output_dir, chunk_size=1024):
        """Download remote file given its URL."""
        with self.session.get(url, stream=True, allow_redirects=True) as r:
            file_size = int(r.headers.get("Content-Length"))
            with tqdm(total=file_size, unit_scale=True, unit='B', unit_divisor=1024) as pbar:
                local_filename = r.headers['Content-Disposition'].split('=')[-1]
                local_filename = local_filename.replace("\"", "")
                local_filename = os.path.join(output_dir, local_filename)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(chunk_size)
        return local_filename

    def download(self, scene_id, output_dir):
        """Download a Landsat scene given its identifier and an output
        directory.
        """
        os.makedirs(output_dir, exist_ok=True)
        dataset = guess_dataset(scene_id)
        if is_product_id(scene_id):
            scene_id = self.api.lookup(dataset, [scene_id], inverse=True)[0]
        url = EE_DOWNLOAD_URL.format(dataset_id=DATASETS[dataset], scene_id=scene_id)
        filename = self._download(url, output_dir)
        return filename
