import os.path
from datetime import datetime
from typing import Dict

from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler

from data_handlers.handlers_api.download_handler import DownloadHandler
from utils import constants


class ModisHandler(DownloadHandler):
    """
    a handler for data downloaded from modis
    """

    # some modis constants should appear here
    SOURCE = ""  # TODO: insert link to modis api
    NAME = "modis" # TODO: move to NDVI, AOD

    # TODO: change to ...
    _MODIS_DATA_NAME = "MCD19A2"
    _MODIS_DATA_VERSION = "006"

    # MODIS CONSTANTS
    __MODIS_BBOX = [33, 28, 38, 36.00]
    __MODIS_DATE_FORMAT = '%Y-%m-%d'

    def get_required_files_list(self, root_dir):
        # the modis handler doesn't require any file
        return []

    def download(self, path: str, start_date: datetime, end_date: datetime, overwrite: bool):
        path_of_data_dir = self.__generate_data_path(path)
        ModisHandler.__clear_if_necessary(overwrite, path_of_data_dir)

        # with  as session:
        session = ModisSession(**self.__get_modis_credentials())
        collection_client = CollectionApi(session=session)
        collections = collection_client.query(short_name=self._MODIS_DATA_NAME, version=self._MODIS_DATA_VERSION)

        granule_client = GranuleApi.from_collection(collections[0], session=session)
        granules = granule_client.query(
            start_date=start_date.strftime(ModisHandler.__MODIS_DATE_FORMAT),
            end_date=end_date.strftime(ModisHandler.__MODIS_DATE_FORMAT),
            bounding_box=ModisHandler.__MODIS_BBOX)

        GranuleHandler.download_from_granules(granules, session, path=path_of_data_dir)

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

    def __generate_temp_data_path(self, path: str) -> str:
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

    @staticmethod
    def __get_modis_credentials() -> Dict[str, str]:
        """
        get credentials of MODIS api from config file
        :return: dict of credentials
        """

        return {
            "username": constants.CONFIG.get_key(constants.CONFIG.Keys.modis_api_user),
            "password": constants.CONFIG.get_key(constants.CONFIG.Keys.modis_api_password)
        }

    @staticmethod
    def __clear_if_necessary(overwrite: bool, path_of_dir: str) -> None:
        """
        clear the given dir if overwrtie is on
        if overwrite is True, clear the given folder
        """

        if not overwrite:
            return

        _ = [os.remove(file) for file in os.listdir(path_of_dir)]
