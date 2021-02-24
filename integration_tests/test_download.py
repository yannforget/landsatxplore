"""Test downloads for all datasets."""

import os
import pytest
import tempfile
from landsatxplore.earthexplorer import EarthExplorer, EarthExplorerError


TIMEOUT = 100


@pytest.fixture(scope="module")
def api():
    return EarthExplorer(
        os.getenv("LANDSATXPLORE_USERNAME"), os.getenv("LANDSATXPLORE_PASSWORD")
    )


def test_dataset_not_available(api):
    pid = "LE717305820INVALIDPID"
    with pytest.raises(EarthExplorerError):
        with tempfile.TemporaryDirectory() as tmpdir:
            api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)


def test_landsat_tm_c1(api):
    pid = "LT05_L1GS_173058_20111028_20161005_01_T2"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_etm_c1(api):
    pid = "LE07_L1TP_173058_20200926_20201022_01_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_8_c1(api):
    pid = "LC08_L1TP_173058_20201004_20201015_01_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_tm_c2_l1(api):
    pid = "LT05_L1TP_173058_20111028_20200820_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_tm_c2_l2(api):
    pid = "LT05_L2SP_173058_20111028_20200820_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_etm_c2_l1(api):
    pid = "LE07_L1TP_173058_20200926_20201022_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_etm_c2_l2(api):
    pid = "LE07_L2SP_173058_20200926_20201022_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_ot_c2_l1(api):
    pid = "LC08_L1TP_173058_20201004_20201015_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_landsat_ot_c2_l2(api):
    pid = "LC08_L2SP_173058_20201004_20201016_02_T1"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname


def test_sentinel_2a(api):
    pid = "11352455"
    with tempfile.TemporaryDirectory() as tmpdir:
        fname = api.download(pid, tmpdir, timeout=TIMEOUT, skip=True)
    assert fname
