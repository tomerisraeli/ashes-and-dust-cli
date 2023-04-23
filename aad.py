import typer
import rich
from rich import box
from rich.table import Table

from datetime import datetime

from utils import constants
import ashes_and_dust
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

    ashes_and_dust.download(path, start_date, end_date, overwrite)


@app.command()
def preprocess(
        path: str
):
    """
    preprocess the data needed


    :parameter path: a directory with the data to preprocess
    """

    ashes_and_dust.preprocess(path)


@app.command()
def list_data():
    """
    print a list of all data handlers


    :return:
    """
    # TODO: get a real data from backend
    table = Table(box=rich.box.HORIZONTALS)

    table.add_column("", justify="left")
    table.add_column("source", style="grey37")
    table.add_column("description", style="grey37")

    for handler in constants.DOWNLOAD_HANDLERS + constants.LOCAL_HANDLERS:
        table.add_row(
            handler.NAME,
            handler.SOURCE,
            handler.DESCRIPTION
        )

    console.print(table)


if __name__ == "__main__":
    app()
