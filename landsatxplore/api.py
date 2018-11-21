"""Python implementation of the Earth Explorer API."""

import json

import requests

from landsatxplore.datamodels import spatial_filter, temporal_filter
from landsatxplore.exceptions import EarthExplorerError
from landsatxplore.util import is_product_id

API_ENDPOINT = 'https://earthexplorer.usgs.gov/inventory/json/v/{version}/'


def to_json(**kwargs):
    """Convert input arguments to a formatted JSON string
    as expected by the EE API.
    """
    return {'jsonRequest': json.dumps(kwargs)}


class API(object):
    """EarthExplorer API."""

    def __init__(self, username, password, version='1.4.1'):
        """EarthExplorer API."""
        self.version = version
        self.endpoint = API_ENDPOINT.format(version=version)
        self.key = self.login(username, password)

    def request(self, request_code, **kwargs):
        """Perform a request to the EE API.
        Possible request codes are listed here:
        https://earthexplorer.usgs.gov/inventory/documentation/json-api
        """
        url = self.endpoint + request_code
        if 'apiKey' not in kwargs:
            kwargs.update(apiKey=self.key)
        params = to_json(**kwargs)
        response = requests.get(url, params=params).json()
        if response['error']:
            raise EarthExplorerError('EE: {}'.format(response['error']))
        else:
            return response['data']

    def login(self, username, password):
        """Get an API key."""
        data = to_json(username=username, password=password, catalogID='EE')
        response = requests.post(self.endpoint + 'login?', data=data).json()
        if response['error']:
            raise EarthExplorerError('EE: {}'.format(response['error']))
        return response['data']

    def logout(self):
        """Log out."""
        self.request('logout')

    def search(
            self,
            dataset,
            latitude=None,
            longitude=None,
            bbox=None,
            max_cloud_cover=None,
            start_date=None,
            end_date=None,
            months=None,
            max_results=20):
        """Search for scenes.

        Parameters
        ----------
        dataset : str
            LANDSAT_TM_C1, LANDSAT_ETM_C1, or LANDSAT_8_C1.
        latitude : float, optional
            Latitude of the point of interest.
        longitude : float, optional
            Longitude of the point of interest.
        bbox : tuple, optional
            (xmin, ymin, xmax, ymax) of the bounding box.
        max_cloud_cover : int, optional
            Max. cloud cover in percent (1-100).
        start_date : str, optional
            YYYY-MM-DD
        end_date : str, optional
            YYYY-MM-DD. Equal to start_date if not provided.
        months : list of int, optional
            Limit results to specific months (1-12).
        max_results : int, optional
            Max. number of results. Defaults to 20.

        Returns
        -------
        results : dict
            Results as a dictionnary.
        """
        params = {
            'datasetName': dataset,
            'includeUnknownCloudCover': False,
            'maxResults': max_results
        }

        if latitude and longitude:
            params.update(spatialFilter=spatial_filter(latitude, longitude))
        if bbox:
            params.update(spatialFilter=spatial_filter(*bbox))
        if max_cloud_cover:
            params.update(maxCloudCover=max_cloud_cover)
        if start_date:
            params.update(temporalFilter=temporal_filter(start_date, end_date))
        if months:
            params.update(months=months)

        response = self.request('search', **params)
        return response['results']

    def lookup(self, dataset, id_list, inverse=False):
        """Convert a list of legacy scene identifier to product identifiers.

        Parameters
        ----------
        dataset : str
            LANDSAT_TM_C1, LANDSAT_ETM_C1, or LANDSAT_8_C1.
        id_list : list of str
            List of scene id if inverse if False. List of product id if
            inverse is True.
        inverse : bool, optional
            If set to true, convert product id to scene id.

        Returns
        -------
        new_id_list : list of str
            List of translated id.
        """
        params = {'datasetName': dataset,
                  'idList': id_list, 'inputField': 'entityId'}
        if inverse:
            params.update(inputField='displayId')
        response = self.request('idlookup', **params)
        return list(response.values())

    def metadata(self, dataset, id_list):
        """Request metadata for a given list of scenes.

        Parameters
        ----------
        dataset : str
            LANDSAT_TM_C1, LANDSAT_ETM_C1 or LANDSAT_8_C1.
        id_list : list of str
            List of product id or legacy scene id.

        Returns
        -------
        results : dict
            Results as a dictionnary.
        """
        if is_product_id(id_list[0]):
            id_list = self.lookup(dataset, id_list, inverse=True)
        params = {'datasetName': dataset, 'entityIds': id_list}
        response = self.request('metadata', **params)
        return response['data']
