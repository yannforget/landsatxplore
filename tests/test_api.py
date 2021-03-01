"""Tests for api module."""

import pytest
import os
from datetime import datetime
from shapely.geometry import Polygon
from landsatxplore import api, errors, util


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
    return api.API(
        os.getenv("LANDSATXPLORE_USERNAME"), os.getenv("LANDSATXPLORE_PASSWORD")
    )


def test_api_login(ee_api):
    assert ee_api.session.headers.get("X-Auth-Token")


def test_api_login_error():
    with pytest.raises(errors.USGSAuthenticationError):
        api.API("bad_username", "bad_password")


def test_api_get_scene_id(ee_api):

    # Single Product ID
    PRODUCT_ID = "LT05_L1GS_173058_20111028_20161005_01_T2"
    scene_id = ee_api.get_entity_id(PRODUCT_ID, dataset="landsat_tm_c1")
    assert scene_id == "LT51730582011301MLK00"

    # Multiple Product IDs
    PRODUCT_IDS = [
        "LT05_L1GS_173058_20111028_20161005_01_T2",
        "LT05_L1GS_173057_20010407_20171209_01_T2",
    ]
    scene_ids = ee_api.get_entity_id(PRODUCT_IDS, dataset="landsat_tm_c1")
    assert scene_ids == ["LT51730582011301MLK00", "LT51730572001097LBG00"]


def test_api_metadata(ee_api):

    PRODUCTS = [
        "LT05_L1GS_173058_20111028_20161005_01_T2",
        "LE07_L1TP_173058_20200926_20201022_01_T1",
        "LC08_L1TP_173058_20201004_20201015_01_T1",
        "LT05_L1TP_173058_20111028_20200820_02_T1",
        "LT05_L2SP_173058_20111028_20200820_02_T1",
        "LE07_L1TP_173058_20200926_20201022_02_T1",
        "LE07_L2SP_173058_20200926_20201022_02_T1",
        "LC08_L1TP_173058_20201004_20201015_02_T1",
        "LC08_L2SP_173058_20201004_20201016_02_T1",
        "L1C_T30QXG_A027990_20201031T103908",
    ]

    for display_id in PRODUCTS:
        dataset = util.guess_dataset(display_id)
        entity_id = ee_api.get_entity_id(display_id, dataset)
        metadata = ee_api.metadata(entity_id, dataset)
        assert isinstance(metadata["cloud_cover"], float)
        assert isinstance(metadata["acquisition_date"], datetime)
        if dataset.startswith("landsat"):
            assert util._is_landsat_product_id(metadata["landsat_product_id"])
            assert util._is_landsat_scene_id(metadata["landsat_scene_id"])
        elif dataset.startswith("sentinel"):
            assert util._is_sentinel_display_id(metadata["display_id"])
            assert util._is_sentinel_entity_id(metadata["entity_id"])


def test_api_get_product_id(ee_api):

    SCENE_ID = "LT51730582011301MLK00"

    # Collection 1
    product_id = ee_api.get_display_id(SCENE_ID, "landsat_tm_c1")
    assert product_id == "LT05_L1GS_173058_20111028_20161005_01_T2"

    # Collection 2
    product_id = ee_api.get_display_id(SCENE_ID, "landsat_tm_c2_l2")
    assert product_id == "LT05_L2SP_173058_20111028_20200820_02_T1"


def test_api_search(ee_api):

    # Longitude and Latitude
    scenes = ee_api.search(
        "landsat_8_c1",
        longitude=4.38,
        latitude=50.85,
        start_date="2018-01-01",
        end_date="2018-01-07",
        max_results=5,
    )
    assert len(scenes) >= 1
    assert "cloud_cover" in scenes[0]

    # Bounding box
    scenes = ee_api.search(
        "landsat_8_c1",
        bbox=BRUSSELS_AREA.bounds,
        start_date="2018-01-01",
        end_date="2018-01-07",
        max_results=5,
    )
    assert len(scenes) >= 1
    assert "cloud_cover" in scenes[0]

    # Collection 2
    scenes = ee_api.search(
        "landsat_ot_c2_l2",
        longitude=4.38,
        latitude=50.85,
        start_date="2018-01-01",
        end_date="2018-01-31",
        max_results=10,
    )
    assert len(scenes) >= 1
    assert "cloud_cover" in scenes[0]
    assert scenes[0]["display_id"][5:7] == "L2"
