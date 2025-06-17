import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

logger = logging.getLogger(__name__)


def find_aircraft_data(registration_number: str, aircraft_data: Iterable[Any]) -> Any:
    for aircraft in aircraft_data:
        if registration_number == aircraft.registration:
            return aircraft
    return None


def format_data(data: Any) -> str:
    if data:
        formatted_data = ""
        try:
            formatted_data += f"  Altitude: {data.altitude}\n"
        except (KeyError, TypeError):
            formatted_data += "  Altitude: N/A \n"
        try:
            formatted_data += f"  Ground Speed: {data.ground_speed}\n"
        except (KeyError, TypeError):
            formatted_data += "  Ground Speed: N/A \n"
        try:
            formatted_data += f"  Heading: {data.heading}\n"
        except (KeyError, TypeError):
            formatted_data += "  Heading: N/A \n"
        return formatted_data
    return "Aircraft data not found."


def status_data(data: Any) -> str:
    if data:
        try:
            if data.altitude is not None and data.altitude > 100:
                return "  Status: In Flight\n"
            return "  Status: On Ground\n"
        except (KeyError, TypeError):
            return "  Status: N/A \n"
    return ""


def format_flight_details(
    flight_details: Dict[str, Any],
    registration_number: str,
    current_flight: Any,
    service: Any,
) -> str:
    formatted_info = "<b>Flight Details:</b>\n"
    try:
        formatted_info += f"  Callsign: {flight_details['identification']['callsign']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Callsign: N/A\n"
    try:
        formatted_info += f"  Flight number: {flight_details['identification']['number']['default']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Flight number: N/A\n"
    try:
        aircraft_data = service.get_flights(flight_details['airline']['code']['icao'])
        found_data = find_aircraft_data(registration_number, aircraft_data)
        formatted_info += status_data(found_data)
    except Exception:
        pass
    try:
        formatted_info += f"  Aircraft Model: {flight_details['aircraft']['model']['text']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Aircraft Model: N/A\n"
    try:
        formatted_info += f"  Registration: {flight_details['aircraft']['registration']}\n"
    except (KeyError, TypeError):
        formatted_info += "  Registration: N/A\n"
    try:
        formatted_info += (
            f"  Airline: {flight_details['airline']['name']} "
            f"({flight_details['airline']['code']['iata']}/{flight_details['airline']['code']['icao']})\n\n"
        )
    except (KeyError, TypeError):
        formatted_info += "  Airline: N/A\n\n"

    formatted_info += "<b>Aircraft Details:</b>\n"
    try:
        formatted_info += f"  Flight level: {current_flight.get_flight_level()}\n"
    except (KeyError, TypeError):
        formatted_info += "  Flight level: N/A\n"
    try:
        aircraft_data = service.get_flights(flight_details['airline']['code']['icao'])
        found_data = find_aircraft_data(registration_number, aircraft_data)
        formatted_info += format_data(found_data)
    except Exception:
        pass
    try:
        formatted_info += f"  Vertical speed: {current_flight.get_vertical_speed()}\n"
    except (KeyError, TypeError):
        formatted_info += "  Vertical speed: N/A\n"
    try:
        formatted_info += f"  Squawk: {current_flight.squawk}"
    except (KeyError, TypeError):
        formatted_info += "  Squawk: N/A"

    formatted_info += "\n\n<b>Airports Details:</b>\n"
    try:
        formatted_info += (
            f"  Origin Airport: {flight_details['airport']['origin']['name']} "
            f"({flight_details['airport']['origin']['code']['iata']}/{flight_details['airport']['origin']['code']['icao']})\n"
        )
    except (KeyError, TypeError):
        formatted_info += "  Origin Airport: N/A\n"
    try:
        formatted_info += (
            f"  Destination Airport: {flight_details['airport']['destination']['name']} "
            f"({flight_details['airport']['destination']['code']['iata']}/{flight_details['airport']['destination']['code']['icao']})\n\n"
        )
    except (KeyError, TypeError):
        formatted_info += "  Destination Airport: N/A\n\n"

    formatted_info += "<b>Time Details:</b>\n"
    try:
        scheduled_departure = datetime.fromtimestamp(flight_details['time']['scheduled']['departure']).astimezone(timezone.utc)
        formatted_info += f"  Scheduled Departure: {scheduled_departure.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Scheduled Departure: N/A\n"
    try:
        real_departure = datetime.fromtimestamp(flight_details['time']['real']['departure']).astimezone(timezone.utc)
        formatted_info += f"  Real Departure: {real_departure.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Real Departure: N/A\n"
    try:
        scheduled_arrival = datetime.fromtimestamp(flight_details['time']['scheduled']['arrival']).astimezone(timezone.utc)
        formatted_info += f"  Scheduled Arrival: {scheduled_arrival.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Scheduled Arrival: N/A\n"
    try:
        estimated_arrival = datetime.fromtimestamp(flight_details['time']['estimated']['arrival']).astimezone(timezone.utc)
        formatted_info += f"  Estimated Arrival: {estimated_arrival.strftime('%H:%M')} (UTC)\n"
    except (KeyError, TypeError, OSError):
        formatted_info += "  Estimated Arrival: N/A\n"
    try:
        formatted_info += f"\nhttps://www.flightradar24.com/{flight_details['identification']['id']}\n\n"
    except (KeyError, TypeError, IndexError):
        pass
    return formatted_info


def format_flight_details_location(flight_details: Dict[str, Any]) -> str:
    formatted_info = ""
    try:
        formatted_info = (
            f"<b>{flight_details['identification']['callsign']} ({flight_details['identification']['number']['default']})</b>\n"
        )
    except (KeyError, TypeError):
        formatted_info += "N/A (N/A)\n"
    try:
        formatted_info += f"   Aircraft Model: {flight_details['aircraft']['model']['text']}\n"
    except (KeyError, TypeError):
        formatted_info += "Aircraft Model: N/A\n"
    try:
        formatted_info += f"   Registration: {flight_details['aircraft']['registration']}\n"
    except (KeyError, TypeError):
        formatted_info += "   Registration: N/A\n"
    try:
        formatted_info += (
            f"   {flight_details['airport']['origin']['code']['icao']} — {flight_details['airport']['destination']['code']['icao']}\n"
        )
    except (KeyError, TypeError):
        formatted_info += "   N/A — N/A\n"
    return formatted_info
