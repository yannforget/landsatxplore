"""Implementation of Earth Explorer API data models.
https://earthexplorer.usgs.gov/inventory/documentation/datamodel
"""


def coordinate(latitude, longitude):
    """Coordinate data model.

    Parameters
    ----------
    latitude : float
        Decimal degree coordinate in EPSG:4326 projection.
    longitude : float
        Decimal degree coordinate in EPSG:4326 projection.

    Returns
    -------
    coordinate : dict
        Coordinate data model as a dictionnary.
    """
    return {
        'latitude': latitude,
        'longitude': longitude
    }


def spatial_filter(xmin, ymin, xmax=None, ymax=None):
    """SpatialFilter data model.

    Parameters
    ----------
    xmin : float
        Min. x coordinate (min longitude).
    ymin : float
        Min. y coordinate (min latitude).
    xmax : float, optional
        Max. x coordinate (max longitude).
    ymax : float, optional
        Max. y coordinate (max latitude).
    
    Returns
    -------
    spatial_filter : dict
        SpatialFilter data model as a dictionnary.
    """
    if not xmax and not ymax:
        xmax = xmin + 0.1
        ymax = ymin + 0.1
    lower_left = coordinate(xmin, ymin)
    upper_right = coordinate(xmax, ymax)
    return {
        'filterType': 'mbr',
        'lowerLeft': lower_left,
        'upperRight': upper_right
    }


def temporal_filter(start_date, end_date=None):
    """TemporalFilter data model.

    Parameters
    ----------
    start_date : str
        ISO 8601 formatted date.
    end_date : str, optional
        ISO 8601 formatted date.
    
    Returns
    -------
    temporal_filter : dict
        TemporalFilter data model as a dictionnary.
    """
    if not end_date:
        end_date = start_date
    return {
        'startDate': start_date,
        'endDate': end_date
    }