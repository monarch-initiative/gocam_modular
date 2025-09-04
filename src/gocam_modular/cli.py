"""CLI interface for gocam_modular."""

import typer
from typing_extensions import Annotated

app = typer.Typer(help="gocam_modular: A fairly trivial ingest of Translator's GOCAM ingest, so we have something to ingest ")


@app.command()
def run(
    name: Annotated[str, typer.Option(help="Name of the person to greet")],
):
    typer.echo(f"Hello, {name}!")

def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
