"""API interaction logic for weather and geolocation services."""

import requests

# Timeout for all HTTP requests (seconds)
REQUEST_TIMEOUT = 10

# WMO Weather interpretation codes mapped to human-readable descriptions
# Reference: https://open-meteo.com/en/docs
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def get_location_by_ip():
    """Determine the user's current location using their IP address.

    Uses the ip-api.com free geolocation API.

    Returns:
        dict: A dictionary with keys 'city', 'state', 'latitude', 'longitude',
              and optionally 'zipcode'.

    Raises:
        RuntimeError: If the location cannot be determined.
    """
    try:
        response = requests.get(
            "http://ip-api.com/json/",
            params={"fields": "status,message,city,regionName,zip,lat,lon"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "success":
            raise RuntimeError(
                f"Could not determine current location: {data.get('message', 'Unknown error')}"
            )

        return {
            "city": data["city"],
            "state": data["regionName"],
            "latitude": data["lat"],
            "longitude": data["lon"],
            "zipcode": data.get("zip"),
        }
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to connect to geolocation service: {exc}"
        ) from exc


def get_location_by_zipcode(zipcode):
    """Look up city, state, and coordinates for a US zip code.

    Uses the zippopotam.us free API.

    Args:
        zipcode: A US zip code string (e.g., '90210').

    Returns:
        dict: A dictionary with keys 'city', 'state', 'latitude', 'longitude',
              and 'zipcode'.

    Raises:
        RuntimeError: If the zip code is invalid or the lookup fails.
    """
    try:
        response = requests.get(
            f"https://api.zippopotam.us/us/{zipcode}",
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 404:
            raise RuntimeError(f"Invalid zip code: {zipcode}")

        response.raise_for_status()
        data = response.json()

        place = data["places"][0]
        return {
            "city": place["place name"],
            "state": place["state"],
            "latitude": float(place["latitude"]),
            "longitude": float(place["longitude"]),
            "zipcode": data["post code"],
        }
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to look up zip code {zipcode}: {exc}"
        ) from exc
    except (KeyError, IndexError, ValueError) as exc:
        raise RuntimeError(
            f"Unexpected response when looking up zip code {zipcode}: {exc}"
        ) from exc


def get_current_weather(latitude, longitude):
    """Fetch current weather conditions for given coordinates.

    Uses the Open-Meteo free API (no API key required).

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.

    Returns:
        dict: A dictionary with keys 'temperature_f' (Fahrenheit) and
              'condition' (human-readable weather description).

    Raises:
        RuntimeError: If the weather data cannot be fetched.
    """
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "temperature_unit": "fahrenheit",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        current = data["current_weather"]
        weather_code = current["weathercode"]
        condition = WMO_WEATHER_CODES.get(weather_code, "Unknown conditions")

        return {
            "temperature_f": current["temperature"],
            "condition": condition,
        }
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to fetch weather data: {exc}"
        ) from exc
    except (KeyError, ValueError) as exc:
        raise RuntimeError(
            f"Unexpected response from weather service: {exc}"
        ) from exc


def get_location(zipcode=None):
    """Get location information, either by zip code or by IP geolocation.

    Args:
        zipcode: Optional US zip code string.

    Returns:
        tuple: (location_dict, used_zipcode) where used_zipcode is a boolean
               indicating whether a zipcode was provided.
    """
    if zipcode:
        return get_location_by_zipcode(zipcode), True
    return get_location_by_ip(), False
