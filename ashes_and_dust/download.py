from utils import constants

from datetime import datetime
import rich


def download(path: str, start_date: datetime, end_date: datetime, overwrite: bool):
    """
    download all the data to the given path
    :param path:
    :param start_date:
    :param end_date:
    :param overwrite: if true, existing data will be overwritten, otherwise, it won't be downloaded
    :return:
    """

    rich.print(f"[bold]validating and downloading data to '{path}' from {start_date} to {end_date}. "
               f"overwriting data: {overwrite}")

    rich.print("[bold]validating local data")

    for local_handler in constants.LOCAL_HANDLERS:
        rich.print(f"validating {local_handler.NAME}")
        if not local_handler.confirm_existence(path):
            rich.print(f"[red bold]{local_handler.NAME} is invalid")

    rich.print("[bold]downloading data")

    for download_handler in constants.DOWNLOAD_HANDLERS:
        rich.print(f"downloading {download_handler.NAME} from {download_handler.SOURCE}")
        download_handler.download(path, start_date, end_date, overwrite)
