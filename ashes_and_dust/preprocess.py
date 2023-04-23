import rich

from utils import constants


def preprocess(path: str):
    """
    preprocess all the data at the given path
    :param path:
    :return:
    """

    rich.print(f"[bold]preprocessing data at '{path}'")

    for local_handler in constants.LOCAL_HANDLERS:
        rich.print(f"preprocessing {local_handler.NAME}")

    for download_handler in constants.DOWNLOAD_HANDLERS:
        rich.print(f"preprocessing {download_handler.NAME}")
        download_handler.preprocess(path)
