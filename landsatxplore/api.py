"""Python implementation of the Earth Explorer API."""

import json

import requests

from landsatxplore.datamodels import spatial_filter, temporal_filter
from landsatxplore.exceptions import EarthExplorerError
from landsatxplore.util import is_product_id

# API_ENDPOINT = 'https://earthexplorer.usgs.gov/inventory/json/v/{version}/'
API_ENDPOINT = 'https://m2m.cr.usgs.gov/api/api/json/stable/'

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
        # self.endpoint = API_ENDPOINT.format(version=version)
        self.endpoint = API_ENDPOINT
        self.key = self.login(username, password)

    def request(self, request_code, kwargs):
        """Perform a request to the EE API.
        Possible request codes are listed here:
        https://earthexplorer.usgs.gov/inventory/documentation/json-api
        """
        url = self.endpoint + request_code
        # if 'apiKey' not in kwargs:
        #     kwargs.update(apiKey=self.key)
        params = json.dumps(kwargs)
        headers = {'X-Auth-Token': self.key}
        response = requests.post(url, params, headers=headers).text
        response = json.loads(response)
        if response['errorMessage']:
            raise EarthExplorerError('EE: {}'.format(response['error']))
        else:
            output = response
        return output['data']

    def login(self, username, password):
        """Get an API key."""
        data = {'username':username, 'password':password}
        json_data = json.dumps(data)
        response = requests.post(self.endpoint + 'login', data=json_data)
        # if response['error']:
        #     raise EarthExplorerError('EE: {}'.format(response['error']))

        try:
            httpStatusCode = response.status_code
            if response == None:
                print("No output from service")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            output = json.loads(response.text)
            if output['errorCode'] != None:
                print(output['errorCode'], "- ", output['errorMessage'])
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            if httpStatusCode == 404:
                print("404 Not Found")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            elif httpStatusCode == 401:
                print("401 Unauthorized")
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
            elif httpStatusCode == 400:
                print("Error Code", httpStatusCode)
                if exitIfNoResponse:
                    sys.exit()
                else:
                    return False
        except Exception as e:
            response.close()
            print(e)
            if exitIfNoResponse:
                sys.exit()
            else:
                return False
        response.close()

        return output['data']

    def logout(self):
        """Log out."""
        headers = {'X-Auth-Token': self.key}
        requests.post(self.endpoint + 'logout', None, headers=headers)


    def search(
            self,
            dataset,
            latitude=None,
            longitude=None,
            bbox=None,
            max_cloud_cover=None,
            start_date=None,
            end_date=None,
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
            (lonmin, latmin, lonmax, latmax) of the bounding box.
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
        # payload = {
        #             'datasetName' : '', # dataset alias
        #             'maxResults' : 10, # max results to return
        #             'startingNumber' : 1,
        #             'sceneFilter' : {} # scene filter
        #           }
        sceneFilter = {}
        if latitude and longitude:
            sceneFilter.update(spatialFilter=spatial_filter(latitude, longitude))
        if bbox:
            # spatialFilter = {'filterType': "mbr",
            #                  'lowerLeft': {'latitude': bbox[1], 'longitude': bbox[0]},
            #                  'upperRight': {'latitude': bbox[3], 'longitude': bbox[2]}}
            sceneFilter.update(spatialFilter=spatial_filter(*bbox))
        if max_cloud_cover:
            sceneFilter.update(cloudCoverFilter={'max':max_cloud_cover,
                                                 'min':0,
                                                 'incloudUnknown':False})
        if start_date:
            sceneFilter.update(acquisitionFilter=temporal_filter(start_date, end_date))

        params = {
            'datasetName': dataset,
            'maxResults': max_results,
            'sceneFilter':sceneFilter
        }

        response = self.request('scene-search', params)
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
