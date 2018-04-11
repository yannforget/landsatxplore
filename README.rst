Description
===========

The **landsatxplore** Python package provides an interface to the
`EarthExplorer <http://earthexplorer.usgs.gov/>`__ portal to search and
download `Landsat
Collections <https://landsat.usgs.gov/landsat-collections>`__ scenes
through a command-line interface or a Python API.

It supports three data sets: ``LANDSAT_TM_C1``, ``LANDSAT_ETM_C1`` and
``LANDSAT_8_C1``.

Installation
============

The package can be installed using pip.

::

    pip install landsatxplore

Usage
=====

**landsatxplore** can be used both through its command-line interface
and as a Python module.

Command-line interface
----------------------

::

    landsatxplore --help

    Usage: landsatxplore [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      download  Download one or several Landsat scenes.
      search    Search for Landsat scenes.

Searching
~~~~~~~~~

::

    Usage: landsatxplore search [OPTIONS]

      Search for Landsat scenes.

    Options:
      --username TEXT                 EarthExplorer username.
      --password TEXT                 EarthExplorer password.
      --dataset [LANDSAT_TM_C1|LANDSAT_ETM_C1|LANDSAT_8_C1]
                                      Landsat data set.
      --location FLOAT...             Point of interest (latitude, longitude).
      --bbox FLOAT...                 Bounding box (xmin, ymin, xmax, ymax).
      --clouds INTEGER                Max. cloud cover (1-100).
      --start TEXT                    Start date (YYYY-MM-DD).
      --end TEXT                      End date (YYYY-MM-DD).
      --limit INTEGER                 Max. results returned.
      --help                          Show this message and exit.

Downloading
~~~~~~~~~~~

::

    Usage: landsatxplore download [OPTIONS] [SCENES]...

      Download one or several Landsat scenes.

    Options:
      -u, --username TEXT  EarthExplorer username.
      -p, --password TEXT  EarthExplorer password.
      -o, --output PATH    Output directory.
      --help               Show this message and exit.

API
---

EarthExplorer API
~~~~~~~~~~~~~~~~~

**landsatxplore** provides an interface to the Earth Explorer JSON API.
Please refer to the official
(`documentation <https://earthexplorer.usgs.gov/inventory/documentation/json-api>`__)
for possible request codes and parameters.

Basic usage
^^^^^^^^^^^

.. code:: python

    import landsatxplore.api

    # Initialize a new API instance and get an access key
    api = landsatxplore.api.API(username, password)

    # Perform a request. Results are returned in a dictionnary
    response = api.request('<request_code>', parameter1=value1, parameter2=value2)

    # Log out
    api.logout()

Searching for scenes
^^^^^^^^^^^^^^^^^^^^

.. code:: python

    import landsatxplore.api

    # Initialize a new API instance and get an access key
    api = landsatxplore.api.API(username, password)

    # Request
    scenes = api.search(
        dataset='LANDSAT_ETM_C1',
        latitude=19.53,
        longitude=-1.53,
        start_date='1995-01-01',
        end_date='1997-01-01',
        max_cloud_cover=10)

    print('{} scenes found.'.format(len(scenes)))

    for scene in scenes:
        print(scene['acquisitionDate'])

    api.logout()

Output:

::

    8 scenes found.
    1995-05-10
    1995-05-26
    1995-06-11
    1995-06-11
    1995-06-27
    1995-07-29
    1995-08-14
    1995-08-14

Downloading scenes
^^^^^^^^^^^^^^^^^^

.. code:: python

    from landsatxplore.earthexplorer import EarthExplorer

    ee = EarthExplorer(username, password)

    ee.download(scene_id='LT51960471995178MPS00', output_dir='./data')

    ee.logout()
