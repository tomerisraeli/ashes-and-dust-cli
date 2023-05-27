import ashes_and_dust
from utils import constants

from datetime import datetime
import rich


def download(path: str, start_date: datetime, end_date: datetime, overwrite: bool):
    """
    download all the data to the given path, if the data is local, it won't be downloaded but its existence will
    be checked
    :param path:
    :param start_date:
    :param end_date:
    :param overwrite: if true, existing data will be overwritten, otherwise, it won't be downloaded
    :return:
    """

    rich.print(f"[bold]validating and downloading data to '{path}' from {start_date} to {end_date}. "
               f"overwriting data: {overwrite}")

    rich.print("[bold]validating local data")

    missing_files = set()
    for local_handler in constants.LOCAL_HANDLERS:
        rich.print(f"  validating {local_handler.NAME}")
        for file in local_handler.confirm_existence(path):
            rich.print(f"[red]  {local_handler.NAME} is missing {file}")
            missing_files.add(file)
    if len(missing_files) > 0:
        rich.print(f"[red bold]missing {len(missing_files)} files\nmissing file are marked in red on the next tree")
        ashes_and_dust.list_dir(path, missing_files)

    rich.print("[bold]downloading data from remote locations")
    for download_handler in constants.DOWNLOAD_HANDLERS:
        rich.print(f"   downloading {download_handler.NAME} from {download_handler.SOURCE}")
        download_handler.download(path, start_date, end_date, overwrite)
