"""Tests for the weather API module."""

from unittest.mock import MagicMock, patch

import pytest

from weather.api import (
    get_current_weather,
    get_location,
    get_location_by_ip,
    get_location_by_zipcode,
)


class TestGetLocationByZipcode:
    """Tests for get_location_by_zipcode."""

    @patch("weather.api.requests.get")
    def test_valid_zipcode(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "post code": "90210",
            "country": "United States",
            "places": [
                {
                    "place name": "Beverly Hills",
                    "state": "California",
                    "latitude": "34.0901",
                    "longitude": "-118.4065",
                }
            ],
        }
        mock_get.return_value = mock_response

        result = get_location_by_zipcode("90210")

        assert result["city"] == "Beverly Hills"
        assert result["state"] == "California"
        assert result["latitude"] == 34.0901
        assert result["longitude"] == -118.4065
        assert result["zipcode"] == "90210"

    @patch("weather.api.requests.get")
    def test_invalid_zipcode(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="Invalid zip code"):
            get_location_by_zipcode("00000")

    @patch("weather.api.requests.get")
    def test_network_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException("Connection failed")

        with pytest.raises(RuntimeError, match="Failed to look up zip code"):
            get_location_by_zipcode("90210")


class TestGetLocationByIp:
    """Tests for get_location_by_ip."""

    @patch("weather.api.requests.get")
    def test_successful_lookup(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "city": "San Francisco",
            "regionName": "California",
            "zip": "94102",
            "lat": 37.7749,
            "lon": -122.4194,
        }
        mock_get.return_value = mock_response

        result = get_location_by_ip()

        assert result["city"] == "San Francisco"
        assert result["state"] == "California"
        assert result["latitude"] == 37.7749
        assert result["longitude"] == -122.4194
        assert result["zipcode"] == "94102"

    @patch("weather.api.requests.get")
    def test_failed_lookup(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "fail",
            "message": "reserved range",
        }
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="Could not determine current location"):
            get_location_by_ip()

    @patch("weather.api.requests.get")
    def test_network_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException("Timeout")

        with pytest.raises(RuntimeError, match="Failed to connect to geolocation"):
            get_location_by_ip()


class TestGetCurrentWeather:
    """Tests for get_current_weather."""

    @patch("weather.api.requests.get")
    def test_successful_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 72.5,
                "weathercode": 0,
            }
        }
        mock_get.return_value = mock_response

        result = get_current_weather(34.0901, -118.4065)

        assert result["temperature_f"] == 72.5
        assert result["condition"] == "Clear sky"

    @patch("weather.api.requests.get")
    def test_unknown_weather_code(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current_weather": {
                "temperature": 65.0,
                "weathercode": 999,
            }
        }
        mock_get.return_value = mock_response

        result = get_current_weather(34.0901, -118.4065)

        assert result["condition"] == "Unknown conditions"

    @patch("weather.api.requests.get")
    def test_network_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException("Timeout")

        with pytest.raises(RuntimeError, match="Failed to fetch weather data"):
            get_current_weather(34.0901, -118.4065)


class TestGetLocation:
    """Tests for get_location helper."""

    @patch("weather.api.get_location_by_zipcode")
    def test_with_zipcode(self, mock_zip):
        mock_zip.return_value = {"city": "Beverly Hills"}

        result, used_zip = get_location("90210")

        assert used_zip is True
        assert result["city"] == "Beverly Hills"
        mock_zip.assert_called_once_with("90210")

    @patch("weather.api.get_location_by_ip")
    def test_without_zipcode(self, mock_ip):
        mock_ip.return_value = {"city": "San Francisco"}

        result, used_zip = get_location()

        assert used_zip is False
        assert result["city"] == "San Francisco"
        mock_ip.assert_called_once()
