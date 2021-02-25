"""Python implementation of the Earth Explorer API."""

import json
from urllib.parse import urljoin
import string
import random
import time

import requests
from shapely.geometry import Point

from landsatxplore.errors import USGSAuthenticationError, USGSError, USGSRateLimitError


API_URL = "https://m2m.cr.usgs.gov/api/api/json/stable/"


def _random_string(length=10):
    """Generate a random string."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class API(object):
    """EarthExplorer API."""

    def __init__(self, username, password):
        """EarthExplorer API.

        Parameters
        ----------
        username : str
            USGS EarthExplorer username.
        password : str
            USGS EarthExplorer password.
        """
        self.url = API_URL
        self.session = requests.Session()
        self.login(username, password)

    @staticmethod
    def raise_api_error(response):
        """Parse API response and return the appropriate exception.

        Parameters
        ----------
        response : requests response
            Response from USGS API.
        """
        data = response.json()
        error_code = data.get("errorCode")
        error_msg = data.get("errorMessage")
        if error_code:
            if error_code in ("AUTH_INVALID", "AUTH_UNAUTHROIZED", "AUTH_KEY_INVALID"):
                raise USGSAuthenticationError(f"{error_code}: {error_msg}.")
            elif error_code == "RATE_LIMIT":
                raise USGSRateLimitError(f"{error_code}: {error_msg}.")
            else:
                raise USGSError(f"{error_code}: {error_msg}.")

    def request(self, endpoint, params=None):
        """Perform a request to the USGS M2M API.

        Parameters
        ----------
        endpoint : str
            API endpoint.
        params : dict, optional
            API parameters.

        Returns
        -------
        data : dict
            JSON data returned by the USGS API.

        Raises
        ------
        USGSAuthenticationError
            If credentials are not valid of if user lacks permission.
        USGSError
            If the USGS API returns a non-null error code.
        """
        url = urljoin(self.url, endpoint)
        data = json.dumps(params)
        r = self.session.get(url, data=data)
        try:
            self.raise_api_error(r)
        except USGSRateLimitError:
            time.sleep(3)
            r = self.session.get(url, data=data)
        self.raise_api_error(r)
        return r.json().get("data")

    def login(self, username, password):
        """Get an API key.

        Parameters
        ----------
        username : str
            EarthExplorer username.
        password : str
            EarthExplorer password.
        """
        login_url = urljoin(self.url, "login")
        payload = {"username": username, "password": password}
        r = self.session.post(login_url, json.dumps(payload))
        self.raise_api_error(r)
        self.session.headers["X-Auth-Token"] = r.json().get("data")

    def logout(self):
        """Logout from USGS M2M API."""
        self.request("logout")
        self.session = requests.Session()

    def get_scene_id(self, product_id, dataset):
        """Get scene ID from product ID.

        Note
        ----
        As the lookup endpoint has been removed in API v1.5, the function makes
        successive calls to scene-list-add and scene-list-get in order to retrieve
        the scene IDs. A temporary sceneList is created and removed at the end of the
        process.

        Parameters
        ----------
        product_id : str or list of str
            Input product ID. Can also be a list of product IDs.
        dataset : str
            Dataset alias.

        Returns
        -------
        scene_id : str or list of str
            Output scene ID. Can also be a list of scene IDs depending on input.
        """
        # scene-list-add support both entityId and entityIds input parameters
        param = "entityId"
        if isinstance(product_id, list):
            param = "entityIds"

        # a random scene list name is created -- better error handling is needed
        # to ensure that the temporary scene list is removed even if scene-list-get
        # fails.
        list_id = _random_string()
        self.request(
            "scene-list-add",
            params={
                "listId": list_id,
                "datasetName": dataset,
                "idField": "displayId",
                param: product_id,
            },
        )
        r = self.request("scene-list-get", params={"listId": list_id})
        scene_id = [scene["entityId"] for scene in r]
        self.request("scene-list-remove", params={"listId": list_id})

        if param == "entityId":
            return scene_id[0]
        else:
            return scene_id

    @staticmethod
    def parse_metadata(response):
        """Parse metadata from API response.

        Parameters
        ----------
        response : requests response
            As returned by api.request("scene-metadata").

        Returns
        -------
        scene_metadata : dict
            Metadata parsed into a dict.
        """
        scene_metadata = {}
        for key, value in response.items():
            if key in ("browse", "metadata"):
                continue
            else:
                scene_metadata[key] = value

        for field in response["metadata"]:
            label = field["dictionaryLink"].split("#")[-1].strip()
            if label in ("coordinate_degrees", "coordinate_decimal"):
                continue
            scene_metadata[label] = field["value"]

        return scene_metadata

    def metadata(self, scene_id, dataset):
        """Get metadata for a given scene.

        Parameters
        ----------
        scene_id : str
            Landsat scene identifier.
        dataset : str
            Dataset alias.

        Returns
        -------
        meta : dict
            Scene metadata.
        """
        r = self.request(
            "scene-metadata",
            params={
                "datasetName": dataset,
                "entityId": scene_id,
                "metadataType": "full",
            },
        )
        return self.parse_metadata(r)

    def get_product_id(self, scene_id, dataset):
        """Get product ID from scene ID.

        Parameters
        ----------
        scene_id : str
            Landsat scene identifier.
        dataset : str
            Dataset alias.

        Returns
        -------
        product_id : str
            Landsat product identifier.
        """
        meta = self.metadata(scene_id, dataset)
        return meta["displayId"]

    def search(
        self,
        dataset,
        longitude=None,
        latitude=None,
        bbox=None,
        max_cloud_cover=None,
        start_date=None,
        end_date=None,
        months=None,
        max_results=100,
    ):
        """Search for scenes.

        Parameters
        ----------
        dataset : str
            Case-insensitive dataset alias (e.g. landsat_tm_c1).
        longitude : float, optional
            Longitude of the point of interest.
        latitude : float, optional
            Latitude of the point of interest.
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
            Max. number of results. Defaults to 100.

        Returns
        -------
        scenes : list of dict
            Matching scenes as a list of dict containing metadata.
        """
        spatial_filter = None
        if longitude and latitude:
            spatial_filter = SpatialFilterMbr(*Point(longitude, latitude).bounds)
        elif bbox:
            spatial_filter = SpatialFilterMbr(*bbox)

        acquisition_filter = None
        if start_date and end_date:
            acquisition_filter = AcquisitionFilter(start_date, end_date)

        cloud_cover_filter = None
        if max_cloud_cover:
            cloud_cover_filter = CloudCoverFilter(
                max=max_cloud_cover, include_unknown=False
            )

        scene_filter = SceneFilter(
            acquisition_filter, spatial_filter, cloud_cover_filter, months=months
        )

        r = self.request(
            "scene-search",
            params={
                "datasetName": dataset,
                "sceneFilter": scene_filter,
                "maxResults": max_results,
                "metadataType": "full",
            },
        )
        return [self.parse_metadata(scene) for scene in r.get("results")]


class Coordinate(dict):
    """A coordinate object as expected by the USGS M2M API.

    Parameters
    ----------
    longitude : float
        Decimal longitude.
    latitude : float
        Decimal latitude.
    """

    def __init__(self, longitude, latitude):
        self["longitude"] = longitude
        self["latitude"] = latitude


class GeoJson(dict):
    """A GeoJSON object as expected by the USGS M2M API.

    Parameters
    ----------
    shape : dict
        Input geometry as a geojson-like dict.
    """

    def __init__(self, shape):
        self["type"] = shape["type"]
        self["coordinates"] = self.transform(shape["type"], shape["coordinates"])

    @staticmethod
    def transform(type, coordinates):
        """Convert geojson-like coordinates as expected by the USGS M2M API.

        Essentially converts tuples of coordinates to api.Coordinate objects.
        """
        if type == "MultiPolygon":
            return [
                [Coordinate(*point) for point in polygon] for polygon in coordinates[0]
            ]
        elif type == "Polygon":
            return [Coordinate(*point) for point in coordinates[0]]
        elif type == "LineString":
            return [Coordinate(*point) for point in coordinates]
        elif type == "Point":
            return Coordinate(*coordinates)
        else:
            raise ValueError(f"Geometry type `{type}` not supported.")


class SpatialFilterMbr(dict):
    """Bounding box spatial filter.

    Parameters
    ----------
    xmin : float
        Min. decimal longitude.
    ymin : float
        Min. decimal latitude.
    xmax : float
        Max. decimal longitude.
    ymax : float
        Max. decimal latitude.
    """

    def __init__(self, xmin, ymin, xmax, ymax):
        self["filterType"] = "mbr"
        self["lowerLeft"] = Coordinate(xmin, ymin)
        self["upperRight"] = Coordinate(xmax, ymax)


class SpatialFilterGeoJSON(dict):
    """GeoJSON-based spatial filter.

    Parameters
    ----------
    shape : dict
        Input shape as a geojson-like dict.
    """

    def __init__(self, shape):
        self["filterType"] = "geoJson"
        self["geoJson"] = GeoJson(shape)


class AcquisitionFilter(dict):
    """Acquisition date filter.

    Parameters
    ----------
    start : str
        ISO 8601 start date.
    end : str
        ISO 8601 end date.
    """

    def __init__(self, start, end):
        self["start"] = start
        self["end"] = end


class CloudCoverFilter(dict):
    """Cloud cover filter.

    Parameters
    ----------
    min : int, optional
        Min. cloud cover in percents (default=0).
    max : int, optional
        Max. cloud cover in percents (default=100).
    include_unknown : bool, optional
        Include scenes with unknown cloud cover (default=False).
    """

    def __init__(self, min=0, max=100, include_unknown=False):
        self["min"] = min
        self["max"] = max
        self["includeUnknown"] = include_unknown


class MetadataValue(dict):
    """Metadata filter.

    Parameters
    ----------
    field_id : str
        ID of the field.
    value : str, float or int
        Value of the field.
    """

    def __init__(self, field_id, value):
        self["filterType"] = "value"
        self["filterId"] = field_id
        self["value"] = value
        if isinstance(value, str):
            self["operand"] = "like"
        else:
            self["operand"] = "="


class SceneFilter(dict):
    """Scene search filter.

    Parameters
    ----------
    acquisition_filter : AcquisitionFilter, optional
        Acquisition date filter.
    spatial_filter : SpatialFilterMbr or SpatialFilterGeoJson, optional
        Spatial filter.
    cloud_cover_filter : CloudCoverFilter, optional
        Cloud cover filter.
    metadata_filter : MetadataValue, optional
        Metadata filter.
    months : list of int, optional
        Seasonal filter (month numbers from 1 to 12).
    """

    def __init__(
        self,
        acquisition_filter=None,
        spatial_filter=None,
        cloud_cover_filter=None,
        metadata_filter=None,
        months=None,
    ):
        if acquisition_filter:
            self["acquisitionFilter"] = acquisition_filter
        if spatial_filter:
            self["spatialFilter"] = spatial_filter
        if cloud_cover_filter:
            self["cloudCoverFilter"] = cloud_cover_filter
        if metadata_filter:
            self["metadataFilter"] = metadata_filter
        if months:
            self["seasonalFilter"] = months
