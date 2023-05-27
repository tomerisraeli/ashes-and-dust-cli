import rasterio
import typer
import rich
from matplotlib import pyplot as plt
from rich import box
from rich.table import Table
from datetime import datetime

from utils import constants
import ashes_and_dust

# aad.py is the main file of the CLI. it defines the different commands
# NOTE: the implementations of the different commands should appear at this file but on designated file on the
# 'ashes_and_dust' dir
# NOTE: make sure to add help and descriptions to the functions and parameters, those will appear on the cli help

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
        path: str = typer.Argument(..., help="path of root directory"),
):
    """
    preprocess the data needed


    :parameter path: a directory with the data to preprocess
    """

    ashes_and_dust.preprocess(path)


@app.command()
def list_data():
    """
    print a list of all data data_handlers


    :return:
    """
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


@app.command()
def plot(path: str):
    """
    show 2-D netCDF or tif file


    :return:
    """
    with rasterio.open(path, 'r') as src:
        # read the data variable
        data_var = src.read(1)

        # plot the data
        plt.imshow(data_var, cmap='jet')
        plt.colorbar()
        plt.show()


@app.command()
def list_dir():
    """
    print the structure of the root dir


    :return: None
    """
    rich.print("[bold]structure of root directory")
    ashes_and_dust.list_dir()


if __name__ == "__main__":
    app()
