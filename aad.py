import typer
import rich

app = typer.Typer()
console = rich.console.Console()


@app.command()
def download(
        path: str,
        start_date: str,
        end_date: str
):
    """
    download the data needed
    :param start_date:  the first date to download data to. format: DD/MM/YYYY or YYYY for 01.01.YYYY
    :param end_date:    the last date to download data to. format: DD/MM/YYYY or YYYY for 31.12.YYYY
    :param path:        a path to download the data to, if the data already exists it won't be downloaded
    """

    console.print(f"[bold]starting to download data to '{path}'")
    con

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
