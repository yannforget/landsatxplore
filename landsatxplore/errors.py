class USGSError(Exception):
    """General error with USGS API."""

    pass


class USGSInvalidEndpoint(Exception):
    """Endpoint is invalid."""

    pass


class USGSInvalidParametersError(Exception):
    """Provided parameters are invalid."""

    pass


class USGSUnauthorizedError(Exception):
    """User does not have access to the requested endpoint."""

    pass


class USGSAuthenticationError(Exception):
    """User credentials verification failed or API key is invalid."""

    pass


class USGSRateLimitError(Exception):
    """Account does not support multiple requests at a time."""

    pass


class EarthExplorerError(Exception):
    """Exception for errors raised by the Earth Explorer API."""

    pass


class LandsatxploreError(Exception):
    """Base landsatxplore error."""

    pass
