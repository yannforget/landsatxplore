"""Tests for earthexplorer module."""

import os
import pytest

from landsatxplore.earthexplorer import EarthExplorer
from landsatxplore.errors import EarthExplorerError


@pytest.fixture(scope="module")
def ee():
    return EarthExplorer(
        os.getenv("LANDSATXPLORE_USERNAME"), os.getenv("LANDSATXPLORE_PASSWORD")
    )


def test_ee_login(ee):
    assert ee.logged_in()


def test_ee_login_error():
    with pytest.raises(EarthExplorerError):
        EarthExplorer("bad_username", "bad_password")
