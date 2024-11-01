"""Command line interface for gocam_modular."""
import logging

from pathlib import Path

from kghub_downloader.download_utils import download_from_yaml
from koza.cli_utils import transform_source
import typer

from gocam import __version__
from gocam.datamodel import Model
from gocam.translation import MinervaWrapper
from gocam.translation.cx2 import model_to_cx2

import json
import yaml

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.callback()
def callback(version: bool = typer.Option(False, "--version", is_eager=True),
):
    """gocam_modular CLI."""
    if version:
        from gocam_modular import __version__
        typer.echo(f"gocam_modular version: {__version__}")
        raise typer.Exit()


@app.command()
def download(format:str = "json",
             force: bool = typer.Option(False, help="Force download of data, even if it exists")):
    """Download data for gocam_modular."""
    typer.echo("Downloading data for gocam_modular...")
    download_config = Path(__file__).parent / "download.yaml"
    try:
        download_from_yaml(yaml_file=download_config, output_dir=".", ignore_cache=force)
    except TypeError as e:
        warn("Couldn't download anything from download.yaml (empty?)")

    # download GOCAMs
    """Fetch GO-CAM models."""
    wrapper = MinervaWrapper()

    model_ids = wrapper.models_ids()

    downloaded_models = None
    for model_id in model_ids:
        model = wrapper.fetch_model(model_id)
        model_dict = model.model_dump(exclude_none=True)

        if format == "json":
            downloaded_models = json.dumps(model_dict, indent=2)
        elif format == "yaml":
            downloaded_models = yaml.dump(model_dict, sort_keys=False)
        else:
            downloaded_models = model.model_dump()

    print(downloaded_models)

@app.command()
def transform(
    output_dir: str = typer.Option("output", help="Output directory for transformed data"),
    row_limit: int = typer.Option(None, help="Number of rows to process"),
    verbose: int = typer.Option(False, help="Whether to be verbose"),
):
    """Run the Koza transform for gocam_modular."""
    typer.echo("Transforming data for gocam_modular...")
    transform_code = Path(__file__).parent / "transform.yaml"
    transform_source(
        source=transform_code,
        output_dir=output_dir,
        output_format="tsv",
        row_limit=row_limit,
        verbose=verbose,
    )


if __name__ == "__main__":
    app()
