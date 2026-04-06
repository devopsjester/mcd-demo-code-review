# Weather CLI

A command-line interface application for looking up locations and checking current weather conditions.

## Requirements

- Python 3.7 or higher

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mcd-demo-code-review
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Install dev dependencies for running tests:
   ```bash
   pip install -r dev-requirements.txt
   ```

## Usage

Run the CLI using `python -m weather.cli`:

### `where-is` — Look up a location

Display the city and state for a given zip code or your current location.

```bash
# Look up by zip code
python -m weather.cli where-is --zipcode 90210
# Output: 90210 is in Beverly Hills, California.

# Use current location (based on IP)
python -m weather.cli where-is
# Output: Your current location is San Francisco, California.
```

### `current` — Get current weather

Display the current temperature and weather conditions.

```bash
# Weather for a zip code
python -m weather.cli current --zipcode 90210
# Output: It is currently 72.5ºF, and Clear sky in Beverly Hills, California.

# Weather for current location
python -m weather.cli current
# Output: It is currently 58.0ºF, and Partly cloudy in San Francisco, California.
```

### Help

```bash
python -m weather.cli --help
python -m weather.cli where-is --help
python -m weather.cli current --help
```

## APIs Used

This application uses the following free APIs that require no registration or API keys:

- **[ip-api.com](http://ip-api.com/)** — IP-based geolocation to determine current location
- **[zippopotam.us](https://api.zippopotam.us/)** — US zip code to city/state/coordinates lookup
- **[Open-Meteo](https://open-meteo.com/)** — Weather forecast data by coordinates

## Running Tests

```bash
pip install -r dev-requirements.txt
pytest tests/ -v
```

## Project Structure

```
weather/
├── __init__.py    # Package init
├── api.py         # API interaction logic (geolocation, zip codes, weather)
└── cli.py         # Click CLI command definitions
tests/
├── __init__.py
├── test_api.py    # Tests for API module
└── test_cli.py    # Tests for CLI commands
requirements.txt       # Runtime dependencies
dev-requirements.txt   # Development/test dependencies
```
