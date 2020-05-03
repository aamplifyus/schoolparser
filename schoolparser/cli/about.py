import os

import click

from eztrack.cli.base.config import EZTRACK_HOME, help_colors
from eztrack.cli.base.config import logger as logger


@click.command(**help_colors)
def about():
    """Return system information about EZTrack."""
    with open(os.path.join(EZTRACK_HOME, "__init__.py"), "r") as fid:
        for line in (line.strip() for line in fid):
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip("'").strip('"')
                break
    if version is None:  # pragma: no cover
        raise RuntimeError("Could not determine version")
    click.echo("EZTrack Version: " + version)
    click.echo("Authors: Adam Li and Patrick Myers")
    click.echo("Contact: support@neurologicsolutions.co")
    click.echo("UDI: Placeholder")
    click.echo("Summary: To fill in.")

    logger.info("ez about")
