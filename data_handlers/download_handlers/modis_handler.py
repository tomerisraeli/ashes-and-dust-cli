import os.path
from datetime import datetime

from data_handlers.handlers_api.download_handler import DownloadHandler


class ModisHandler(DownloadHandler):
    """
    a handler for data downloaded from modis
    """

    # some modis constants should appear here
    SOURCE = ""  # TODO: insert link to modis api
    # constants that are different between the data downloaded should appear here
    _MODIS_DATA_NAME = ""

    def get_required_files_list(self, root_dir):
        # the modis handler doesn't require any file
        return []

    def download(self, path: str, start_date: datetime, end_date: datetime, overwrite: bool):
        path_of_data_dir = self.__generate_data_path(path)

        # TODO: download data to path_pf_data_dir
        #  range of dates to download is start_date to end_date
        #  if overwrite is True download again all the data, if False, download only missing data

    def preprocess(self, path):
        path_of_data_dir = self.__generate_data_path(path)
        temp_data_path = self.__generate_temp_data_path(path)
        # TODO: for each file in data_dir, convert it to a tif holding the data of the tile
        #  it will be better if each file will generate 3 tiffs, one for each tile
        #  when all the files are saved as tiffs
        #  save the tiffs on the temp_data_path dir

    def __generate_data_path(self, path):
        """
        generate the path of dir to download data to and make sure it exists
        :param path:    the path of root dir
        :return:        the path to data dir as str
        """

        dir_path = os.path.join(path, self.NAME.replace(" ", "_").lower())
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path

    def __generate_temp_data_path(self, path):
        """
        generate the path of dir to download data to and make sure it exists
        :param path:    the path of root dir
        :return:        the path to data dir as str
        """

        data_path = self.__generate_data_path(path)
        path = os.path.join(data_path, "support")
        if not os.path.isdir(path):
            os.makedirs(path)
        return path
