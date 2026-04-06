"""Tests for the weather CLI commands."""

from unittest.mock import patch

from click.testing import CliRunner

from weather.cli import cli


class TestWhereIsCommand:
    """Tests for the where-is CLI command."""

    @patch("weather.cli.get_location")
    def test_with_zipcode(self, mock_location):
        mock_location.return_value = (
            {
                "city": "Beverly Hills",
                "state": "California",
                "zipcode": "90210",
                "latitude": 34.0901,
                "longitude": -118.4065,
            },
            True,
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["where-is", "--zipcode", "90210"])

        assert result.exit_code == 0
        assert "90210 is in Beverly Hills, California." in result.output

    @patch("weather.cli.get_location")
    def test_without_zipcode(self, mock_location):
        mock_location.return_value = (
            {
                "city": "San Francisco",
                "state": "California",
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
            False,
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["where-is"])

        assert result.exit_code == 0
        assert "Your current location is San Francisco, California." in result.output

    @patch("weather.cli.get_location")
    def test_error_handling(self, mock_location):
        mock_location.side_effect = RuntimeError("Invalid zip code: 00000")

        runner = CliRunner()
        result = runner.invoke(cli, ["where-is", "--zipcode", "00000"])

        assert result.exit_code != 0
        assert "Invalid zip code: 00000" in result.output


class TestCurrentCommand:
    """Tests for the current CLI command."""

    @patch("weather.cli.get_current_weather")
    @patch("weather.cli.get_location")
    def test_with_zipcode(self, mock_location, mock_weather):
        mock_location.return_value = (
            {
                "city": "Beverly Hills",
                "state": "California",
                "zipcode": "90210",
                "latitude": 34.0901,
                "longitude": -118.4065,
            },
            True,
        )
        mock_weather.return_value = {
            "temperature_f": 72.5,
            "condition": "Clear sky",
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["current", "--zipcode", "90210"])

        assert result.exit_code == 0
        assert "It is currently 72.5°F, and Clear sky in Beverly Hills, California." in result.output

    @patch("weather.cli.get_current_weather")
    @patch("weather.cli.get_location")
    def test_without_zipcode(self, mock_location, mock_weather):
        mock_location.return_value = (
            {
                "city": "San Francisco",
                "state": "California",
                "latitude": 37.7749,
                "longitude": -122.4194,
            },
            False,
        )
        mock_weather.return_value = {
            "temperature_f": 58.0,
            "condition": "Partly cloudy",
        }

        runner = CliRunner()
        result = runner.invoke(cli, ["current"])

        assert result.exit_code == 0
        assert "It is currently 58.0°F, and Partly cloudy in San Francisco, California." in result.output

    @patch("weather.cli.get_location")
    def test_location_error(self, mock_location):
        mock_location.side_effect = RuntimeError("Failed to connect")

        runner = CliRunner()
        result = runner.invoke(cli, ["current", "--zipcode", "90210"])

        assert result.exit_code != 0
        assert "Failed to connect" in result.output

    @patch("weather.cli.get_current_weather")
    @patch("weather.cli.get_location")
    def test_weather_error(self, mock_location, mock_weather):
        mock_location.return_value = (
            {
                "city": "Beverly Hills",
                "state": "California",
                "latitude": 34.0901,
                "longitude": -118.4065,
            },
            True,
        )
        mock_weather.side_effect = RuntimeError("Failed to fetch weather data")

        runner = CliRunner()
        result = runner.invoke(cli, ["current", "--zipcode", "90210"])

        assert result.exit_code != 0
        assert "Failed to fetch weather data" in result.output


class TestCLIHelp:
    """Tests for CLI help messages."""

    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "where-is" in result.output
        assert "current" in result.output

    def test_where_is_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["where-is", "--help"])

        assert result.exit_code == 0
        assert "--zipcode" in result.output

    def test_current_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["current", "--help"])

        assert result.exit_code == 0
        assert "--zipcode" in result.output
