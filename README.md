# Description

![CLI Demo](https://raw.githubusercontent.com/yannforget/landsatxplore/master/demo.gif?s=0.5)

The **landsatxplore** Python package provides an interface to the [EarthExplorer](http://earthexplorer.usgs.gov/) portal to search and download [Landsat Collections](https://landsat.usgs.gov/landsat-collections) scenes through a command-line interface or a Python API.

It supports three data sets: `LANDSAT_TM_C1`, `LANDSAT_ETM_C1` and `LANDSAT_8_C1`.

# Quick start

Searching for Landsat 5 TM scenes that contains the location (12.53, -1.53) acquired during the year 1995.

```
landsatxplore search --dataset LANDSAT_TM_C1 --location 12.53 -1.53 \
    --start 1995-01-01 --end 1995-12-31
```

Search for Landsat 7 ETM scenes in Brussels with less than 5% of clouds. Save the returned results in a `.csv` file.

```
landsatxplore search --dataset LANDSAT_ETM_C1 \
    --location 50.83 4.38 --clouds 5 > results.csv
```

Downloading three Landsat scenes from different datasets in the current directory.

```
landsatxplore download LT51960471995178MPS00 LC80390222013076EDC00 LC82150682015350LGN01
```

To use the package, Earth Explorer credentials are required ([registration](https://ers.cr.usgs.gov/register/)).

# Installation

The package can be installed using pip.

```
pip install landsatxplore
```

# Usage

**landsatxplore** can be used both through its command-line interface and as a Python module.

## Command-line interface

```
landsatxplore --help
```

```
Usage: landsatxplore [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  download  Download one or several Landsat scenes.
  search    Search for Landsat scenes.
```

### Credentials

Credentials for the Earth Explorer portal can be obtained [here](https://ers.cr.usgs.gov/register/).

`--username` and `--password` can be provided as command-line options or as environment variables:

``` shell
export LANDSATXPLORE_USERNAME=<your_username>
export LANDSATXPLORE_PASSWORD=<your_password>
```

### Searching

```
landsatxplore search --help
```

```
Usage: landsatxplore search [OPTIONS]

  Search for Landsat scenes.

Options:
  -u, --username TEXT             EarthExplorer username.
  -p, --password TEXT             EarthExplorer password.
  -d, --dataset [LANDSAT_TM_C1|LANDSAT_ETM_C1|LANDSAT_8_C1]
                                  Landsat data set.
  -l, --location FLOAT...         Point of interest (latitude, longitude).
  -b, --bbox FLOAT...             Bounding box (xmin, ymin, xmax, ymax).
  -c, --clouds INTEGER            Max. cloud cover (1-100).
  -s, --start TEXT                Start date (YYYY-MM-DD).
  -e, --end TEXT                  End date (YYYY-MM-DD).
  -o, --output [scene_id|product_id|json|csv]
                                  Output format.
  -m, --limit INTEGER             Max. results returned.
  --help                          Show this message and exit.
```

### Downloading

```
landsatxplore download --help
```

```
Usage: landsatxplore download [OPTIONS] [SCENES]...

  Download one or several Landsat scenes.

Options:
  -u, --username TEXT  EarthExplorer username.
  -p, --password TEXT  EarthExplorer password.
  -o, --output PATH    Output directory (default to current).
  --help               Show this message and exit.
```

## API

### EarthExplorer API

**landsatxplore** provides an interface to the Earth Explorer JSON API. Please refer to the official ([documentation](https://earthexplorer.usgs.gov/inventory/documentation/json-api)) for possible request codes and parameters.

#### Basic usage

``` python
import landsatxplore.api

# Initialize a new API instance and get an access key
api = landsatxplore.api.API(username, password)

# Perform a request. Results are returned in a dictionnary
response = api.request('<request_code>', parameter1=value1, parameter2=value2)

# Log out
api.logout()
```

#### Searching for scenes

``` python
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
```

Output:

```
8 scenes found.
1995-05-10
1995-05-26
1995-06-11
1995-06-11
1995-06-27
1995-07-29
1995-08-14
1995-08-14
```

#### Downloading scenes

``` python
from landsatxplore.earthexplorer import EarthExplorer

ee = EarthExplorer(username, password)

ee.download(scene_id='LT51960471995178MPS00', output_dir='./data')

ee.logout()
```
