from datetime import datetime


def download(path: str, start_date: datetime, end_date: datetime, overwrite: bool):
    """
    download all the data to the given path
    :param path:
    :param start_date:
    :param end_date:
    :param overwrite: if true, existing data will be overwritten, otherwise, it won't be downloaded
    :return:
    """

    print(f"[bold]starting to download data to '{path}'")
    print(f"from {start_date.date()} to {end_date.date()}")
    print(f"overwrite: {overwrite}")