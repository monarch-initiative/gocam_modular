"""Command line interface for gocam_modular."""
import time
import json
import os
from pathlib import Path
import typer
from tqdm import tqdm
from warnings import warn

import logging
from kghub_downloader.download_utils import download_from_yaml
from koza.cli_utils import transform_source
import typer
from gocam.translation import MinervaWrapper

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
def download(download_dir: str = "data",
             force: bool = typer.Option(False, help="Force download of data, even if it exists")):
    """Download data for gocam_modular."""
    typer.echo("Downloading data for gocam_modular...")
    download_config = Path(__file__).parent / "download.yaml"
    download_from_yaml(yaml_file=download_config, output_dir=".", ignore_cache=force)

    # download GOCAMs
    """Fetch GO-CAM models."""
    wrapper = MinervaWrapper()
    model_ids = wrapper.models_ids()

    downloaded_models = []
    for model_id in tqdm(model_ids, desc="fetching GO-CAM models"):
        model_dict = fetch_model_with_retry(wrapper, model_id)
        if model_dict is not None:
            downloaded_models.append(model_dict)

    # save the models to a file
    with open(os.path.join(download_dir, "gocam_models.json"), "w") as f:
        json.dump(downloaded_models, f, indent=2)


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


def fetch_model_with_retry(wrapper, model_id, max_retries=5):
    """Fetch model with exponential backoff retry."""
    retries = 0
    wait_time = 1  # initial wait time in seconds

    while retries < max_retries:
        try:
            model = wrapper.fetch_model(model_id)
            return model.model_dump(exclude_none=True)
        except Exception as e:
            if "429" in str(e):  # check for too many requests error
                retries += 1
                typer.echo(f"429 Too Many Requests - Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2  # exponential backoff
            else:
                typer.echo(f"Failed to fetch model {model_id}: {e}")
                break  # break if it's not a rate-limiting error
    warn(f"Exceeded maximum retries for model {model_id}")
    return None
