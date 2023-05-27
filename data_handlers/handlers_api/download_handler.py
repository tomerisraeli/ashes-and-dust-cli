from datetime import datetime

from data_handlers.handlers_api.handler import Handler


class DownloadHandler(Handler):
    """
    handler for data which is available online
    """

    def download(self, path: str, start_date: datetime, end_date: datetime, overwrite: bool):
        """
        download the data to the given path
        :param path:        the path to the root dir holding all data of the project
        :param start_date:  the first date to download
        :param end_date:    the last date to download data to
        :param overwrite:   if the data already exits and overwrite is True, the data should be downloaded again.
                            otherwise, data should be kept untouched
        :return: None
        """
        ...
