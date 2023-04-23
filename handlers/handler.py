from datetime import datetime


class Handler:
    SOURCE: str = ...  # the source of the data handled by the Handler
    NAME: str = ...  # a short name for data handled by the Handler

    CLIP_AND_REPROJECT_FILES = [
        # (clip file - shp, reproject file - tif, tile name)
        ("tiles/h21v06_crs2039.shp", "tiles/h21v06.tif", "h21v06"),
        ("tiles/h21v05_crs2039.shp", "tiles/h21v05.tif", "h21v05"),
        ("tiles/h20v05_crs2039.shp", "tiles/h20v05.tif", "h20v05")
    ]

    def preprocess(self, path):
        """
        preprocess the raw data: clip, reproject and save as a new netcdf file at path near the raw data


        :param path:    the path to the root dir holding all data of the project
        :return:        None
        """
        ...


class LocalHandler(Handler):
    """
    handler for data which isn't available online and should be available locally.
    instead of downloading the data, it will confirm the existence of it at the given path
    """

    def confirm_existence(self, path: str) -> bool:
        """
        confirm that all the needed files for this handler exits, with the right names and paths


        :param path:    the path to the root dir holding all data of the project
        :return:        True if confirmed, False otherwise
        """
        ...


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
