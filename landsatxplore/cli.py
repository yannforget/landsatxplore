"""Command-line interface."""

import os

import click

from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer

DATASETS = ['LANDSAT_TM_C1', 'LANDSAT_ETM_C1', 'LANDSAT_8_C1']


@click.group()
def cli():
    pass


@click.command()
@click.option('--username', type=click.STRING, help='EarthExplorer username.')
@click.option('--password', type=click.STRING, help='EarthExplorer password.')
@click.option(
    '--dataset', type=click.Choice(DATASETS), help='Landsat data set.',
    default='LANDSAT_8_C1'
)
@click.option('--location', type=click.FLOAT, nargs=2, help='Point of interest (latitude, longitude).')
@click.option('--bbox', type=click.FLOAT, nargs=4, help='Bounding box (xmin, ymin, xmax, ymax).')
@click.option('--clouds', type=click.INT, help='Max. cloud cover (1-100).')
@click.option('--start', type=click.STRING, help='Start date (YYYY-MM-DD).')
@click.option('--end', type=click.STRING, help='End date (YYYY-MM-DD).')
@click.option('--limit', type=click.INT, help='Max. results returned.')
def search(username, password, dataset, location, bbox, clouds, start, end, limit):
    """Search for Landsat scenes."""
    api = API(username, password)

    where = {'dataset': dataset}
    if location:
        latitude, longitude = location
        where.update(latitude=latitude, longitude=longitude)
    if bbox:
        where.update(bbox=bbox)
    if clouds:
        where.update(max_cloud_cover=clouds)
    if start:
        where.update(start_date=start)
    if end:
        where.update(end_date=end)
    if limit:
        where.update(max_results=limit)

    results = api.search(**where)
    api.logout()

    for scene in results:
        click.echo(scene['entityId'])


@click.command()
@click.option('--username', '-u', type=click.STRING, help='EarthExplorer username.')
@click.option('--password', '-p', type=click.STRING, help='EarthExplorer password.')
@click.option('--output', '-o', type=click.Path(exists=True, dir_okay=True), help='Output directory.')
@click.argument('scenes', type=click.STRING, nargs=-1)
def download(username, password, output, scenes):
    """Download one or several Landsat scenes."""
    ee = EarthExplorer(username, password)
    output_dir = os.path.abspath(output)
    for scene in scenes:
        if not ee.logged_in():
            ee = EarthExplorer(username, password)
        ee.download(scene, output_dir)
    ee.logout()


cli.add_command(search)
cli.add_command(download)


if __name__ == '__main__':
    cli()
