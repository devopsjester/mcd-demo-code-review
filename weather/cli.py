"""Click CLI command definitions for the Weather app."""

import click

from weather.api import get_current_weather, get_location


@click.group()
def cli():
    """Weather CLI - Get weather information from the command line."""


@cli.command("where-is")
@click.option("--zipcode", default=None, help="US zip code to look up.")
def where_is(zipcode):
    """Display the city and state for a given location."""
    try:
        location, used_zipcode = get_location(zipcode)
        city = location["city"]
        state = location["state"]

        if used_zipcode:
            click.echo(f"{location['zipcode']} is in {city}, {state}.")
        else:
            click.echo(f"Your current location is {city}, {state}.")
    except RuntimeError as exc:
        raise click.ClickException(str(exc))


@cli.command("current")
@click.option("--zipcode", default=None, help="US zip code to look up.")
def current(zipcode):
    """Display current temperature and weather conditions for a given location."""
    try:
        location, _ = get_location(zipcode)
        weather = get_current_weather(
            location["latitude"], location["longitude"]
        )

        city = location["city"]
        state = location["state"]
        temp = weather["temperature_f"]
        condition = weather["condition"]

        click.echo(
            f"It is currently {temp}ºF, and {condition} in {city}, {state}."
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc))


def main():
    """Entry point for the Weather CLI."""
    cli()


if __name__ == "__main__":
    main()
