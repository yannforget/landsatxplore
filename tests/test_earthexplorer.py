"""Tests for earthexplorer module."""

import os
import pytest
import vcr

from landsatxplore.earthexplorer import EarthExplorer
from landsatxplore.errors import EarthExplorerError


@pytest.fixture(scope="module")
def ee():
    def _filter_credentials(request):
        if "password" in str(request.body):
            request.body = None
        return request

    with vcr.use_cassette(
        "tests/fixtures/vcr_cassettes/ee_login.yaml",
        before_record_request=_filter_credentials,
    ):
        ee_ = EarthExplorer(
            os.getenv("LANDSATXPLORE_USERNAME"), os.getenv("LANDSATXPLORE_PASSWORD")
        )
    return ee_


def test_ee_login(ee):
    assert ee.logged_in()


def test_ee_login_error():
    with vcr.use_cassette("tests/fixtures/vcr_cassettes/ee_login_error.yaml"):
        with pytest.raises(EarthExplorerError):
            EarthExplorer("bad_username", "bad_password")
