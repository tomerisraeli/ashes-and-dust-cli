import rich

from utils import constants


def preprocess(path: str):
    """
    preprocess all the data at the given path
    :param path:
    :return:
    """

    rich.print(f"[bold]preprocessing data at '{path}'")

    for handler in constants.LOCAL_HANDLERS + constants.DOWNLOAD_HANDLERS:
        rich.print(f"preprocessing {handler.NAME}")
        handler.preprocess(path)

