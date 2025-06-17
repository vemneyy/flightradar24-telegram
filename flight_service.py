import os
import functools
import logging
from typing import Any, Dict, Iterable, Optional

from FlightRadar24 import FlightRadar24API


logger = logging.getLogger(__name__)


class FlightService:
    """Wrapper around :class:`FlightRadar24API`."""

    def __init__(self) -> None:
        username = os.getenv("FR24_USERNAME")
        password = os.getenv("FR24_PASSWORD")
        if username and password:
            logger.info("Using provided FR24 credentials")
            self._api = FlightRadar24API(username, password)
        else:
            self._api = FlightRadar24API()

    @functools.lru_cache(maxsize=64)
    def get_airport(self, airport_code: str) -> Any:
        """Return cached airport data."""
        logger.debug("Fetching airport %s", airport_code)
        return self._api.get_airport(airport_code)

    def search(self, flight_num: str) -> Dict[str, Any]:
        return self._api.search(flight_num)

    def get_flights(self, **kwargs: Any) -> Iterable[Any]:
        return self._api.get_flights(**kwargs)

    def get_flight_details(self, flight: Any) -> Dict[str, Any]:
        return self._api.get_flight_details(flight)

    def get_bounds_by_point(self, lat: float, lon: float, distance: int) -> Any:
        return self._api.get_bounds_by_point(lat, lon, distance)
