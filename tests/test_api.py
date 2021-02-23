"""Tests for api module."""

import pytest
import vcr
import os
from shapely.geometry import Polygon
from landsatxplore import api, errors


BRUSSELS_AREA = Polygon(
    [(4.25, 50.75), (4.50, 50.75), (4.50, 50.95), (4.25, 50.95), (4.25, 50.75)]
)


def test__random_string():
    str_a = api._random_string(length=10)
    str_b = api._random_string(length=10)
    assert str_a != str_b
    assert len(str_a) == 10
    assert len(str_b) == 10


def test_coordinate():
    coord = api.Coordinate(4.35, 50.85)
    assert coord == {"longitude": 4.35, "latitude": 50.85}


def test_geojson():
    geojson = api.GeoJson(BRUSSELS_AREA.__geo_interface__)
    assert geojson["type"] == "Polygon"
    assert len(geojson["coordinates"]) == 5
    assert geojson["coordinates"][0] == {"longitude": 4.25, "latitude": 50.75}


def test_spatial_filter_mbr():
    mbr = api.SpatialFilterMbr(*BRUSSELS_AREA.bounds)
    assert mbr["filterType"] == "mbr"
    assert mbr["lowerLeft"] == {"longitude": 4.25, "latitude": 50.75}
    assert mbr["upperRight"] == {"longitude": 4.5, "latitude": 50.95}


def test_spatial_filter_geojson():
    sfilter = api.SpatialFilterGeoJSON(BRUSSELS_AREA.__geo_interface__)
    assert sfilter["filterType"] == "geoJson"


def test_acquisition_filter():
    afilter = api.AcquisitionFilter("2000-01-01", "2001-12-31")
    assert afilter["start"] == "2000-01-01"
    assert afilter["end"] == "2001-12-31"


def test_cloud_cover_filter():
    cfilter = api.CloudCoverFilter(max=10)
    assert cfilter["min"] == 0
    assert cfilter["max"] == 10


def test_metadata_value():
    mfilter = api.MetadataValue(
        field_id="5e83d08fd4594aae", value="LT05_L1GS_173058_20111028_20161005_01_T2"
    )
    assert mfilter["filterType"] == "value"
    assert mfilter["filterId"] == "5e83d08fd4594aae"
    assert mfilter["value"] == "LT05_L1GS_173058_20111028_20161005_01_T2"
    assert mfilter["operand"] == "like"


@pytest.fixture(scope="module")
def ee_api():
    def _filter_credentials(request):
        if "password" in str(request.body):
            request.body = None
        return request

    with vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/api_login.yaml",
        before_record_request=_filter_credentials,
    ):
        ee = api.API(
            os.getenv("LANDSATXPLORE_USERNAME"), os.getenv("LANDSATXPLORE_PASSWORD")
        )
    return ee


def test_api_login(ee_api):
    assert ee_api.session.headers.get("X-Auth-Token")


def test_api_login_error():
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_login_error.yaml"):
        with pytest.raises(errors.USGSAuthenticationError):
            api.API("bad_username", "bad_password")


def test_api_get_scene_id(ee_api):

    # Single Product ID
    PRODUCT_ID = "LT05_L1GS_173058_20111028_20161005_01_T2"
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_scene_id.yaml"):
        scene_id = ee_api.get_scene_id(PRODUCT_ID, dataset="landsat_tm_c1")
    assert scene_id == "LT51730582011301MLK00"

    # Multiple Product IDs
    PRODUCT_IDS = [
        "LT05_L1GS_173058_20111028_20161005_01_T2",
        "LT05_L1GS_173057_20010407_20171209_01_T2",
    ]
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_scene_ids.yaml"):
        scene_ids = ee_api.get_scene_id(PRODUCT_IDS, dataset="landsat_tm_c1")
    assert scene_ids == ["LT51730582011301MLK00", "LT51730572001097LBG00"]


def test_api_metadata(ee_api):

    # Collection 1
    SCENE_ID = "LT51730582011301MLK00"
    DATASET = "landsat_tm_c1"
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_scene_metadata_c1.yaml"):
        metadata = ee_api.metadata(SCENE_ID, DATASET)
    assert metadata["entityId"] == SCENE_ID
    assert metadata["landsat_scene_id"] == SCENE_ID

    # Collection 2
    SCENE_ID = "LT51730582011301MLK00"
    DATASET = "landsat_tm_c2_l1"
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_scene_metadata_c2.yaml"):
        metadata = ee_api.metadata(SCENE_ID, DATASET)
    assert metadata["entityId"] == SCENE_ID
    assert metadata["collection_number"] == 2


def test_api_get_product_id(ee_api):

    SCENE_ID = "LT51730582011301MLK00"

    # Collection 1
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_productid_c1.yaml"):
        product_id = ee_api.get_product_id(SCENE_ID, "landsat_tm_c1")
    assert product_id == "LT05_L1GS_173058_20111028_20161005_01_T2"

    # Collection 2
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_productid_c2.yaml"):
        product_id = ee_api.get_product_id(SCENE_ID, "landsat_tm_c2_l2")
    assert product_id == "LT05_L2SP_173058_20111028_20200820_02_T1"


def test_api_search(ee_api):

    # Longitude and Latitude
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_search_c1_lonlat.yaml"):
        scenes = ee_api.search(
            "landsat_8_c1",
            longitude=4.38,
            latitude=50.85,
            start_date="2018-01-01",
            end_date="2018-01-07",
            max_results=5,
        )
    assert len(scenes) >= 1
    assert "cloudCover" in scenes[0]

    # Bounding box
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_search_c1_bbox.yaml"):
        scenes = ee_api.search(
            "landsat_8_c1",
            bbox=BRUSSELS_AREA.bounds,
            start_date="2018-01-01",
            end_date="2018-01-07",
            max_results=5,
        )
    assert len(scenes) >= 1
    assert "cloudCover" in scenes[0]

    # Collection 2
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/api_search_c2.yaml"):
        scenes = ee_api.search(
            "landsat_ot_c2_l2",
            longitude=4.38,
            latitude=50.85,
            start_date="2018-01-01",
            end_date="2018-01-31",
            max_results=10,
        )
        assert len(scenes) >= 1
        assert "cloudCover" in scenes[0]
        assert scenes[0]["displayId"][5:7] == "L2"
