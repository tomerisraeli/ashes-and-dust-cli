import typer
import rich
from datetime import datetime

from utils.date_parser import date_parser
from utils import constants

app = typer.Typer()
console = rich.console.Console()


@app.command()
def download(
        path: str = typer.Argument(...,
                                   help="the path to download data to"),
        start_date: datetime = typer.Argument(...,
                                              help="the first date to download data to",
                                              formats=constants.DATE_FORMATS
                                              ),
        end_date: datetime = typer.Argument(...,
                                            help="the last date to download data to",
                                            formats=constants.DATE_FORMATS
                                            ),
        overwrite: bool = typer.Option(False,
                                       help="overwrite the data if its already exits at the given path")
):
    """
    download the data needed


    :parameter overwrite:   (flag) overwrite the data if its already exits at the given path
    :parameter start_date:  the first date to download data to
    :parameter end_date:    the last date to download data to
    :parameter path:        a path to download the data to, if the data already exists it won't be downloaded
    """
    console.print(f"[bold]starting to download data to '{path}'")
    console.print(f"from {start_date.date()} to {end_date.date()}")
    console.print(f"overwrite: {overwrite}")


@app.command()
def preprocess(
        path: str
):
    """
    preprocess the data needed
    :parameter path: a directory with the data to preprocess
    """

    console.print(f"[bold]starting to preprocess data at '{path}'")


if __name__ == "__main__":
    app()
