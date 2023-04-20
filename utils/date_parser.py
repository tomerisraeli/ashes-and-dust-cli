from datetime import datetime

from utils import constants


def date_parser(date: str) -> datetime:
    """
    get a
    :param date:
    :return:
    """
    return datetime.strptime(date, constants.DATE_FORMAT)
