import functools
import os.path
from datetime import datetime, timedelta
from typing import Dict, Tuple, List

import h5py
from osgeo import gdal
from rich.progress import track
import rich
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
    SOURCE = "https://modis.gsfc.nasa.gov"
    NAME = "modis"  # TODO: move to NDVI, AOD

    # TODO: change to ...
    _MODIS_DATA_NAME = "MCD19A2"
    _MODIS_DATA_VERSION = "006"

    # MODIS CONSTANTS
    __MODIS_BBOX = [33, 28, 38, 36]
    __MODIS_DATE_FORMAT = '%Y-%m-%d'
    __TIF_FILES_FORMAT = "%Y-%m-%d-%H-%M-%S"

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

        self.__convert_files_to_tif(path_of_data_dir, temp_data_path)

        # TODO: for each file in data_dir, convert it to a tif holding the data of the tile
        #  it will be better if each file will generate 3 tiffs, one for each tile
        #  when all the files are saved as tiffs
        #  save the tiffs on the temp_data_path dir

    def __convert_files_to_tif(self, path_of_data_dir: str, temp_data_path: str) -> None:
        """
        convert all necessary hdf files to tiffs
        :param path_of_data_dir:    dir of hdf files
        :param temp_data_path:      dir of tiffs
        """
        kicked_tiles = set()
        for short_hdf_path in track(os.listdir(path_of_data_dir), description="converting hdf files to tif"):
            if ".hdf" not in short_hdf_path:
                continue

            full_hdf_path = os.path.join(path_of_data_dir, short_hdf_path)
            full_tif_path, tile = self.__generate_tif_name(short_hdf_path, temp_data_path)

            if tile not in self.__get_tiles_names():
                kicked_tiles.add(tile)
                continue

            ModisHandler.__convert_hdf_to_tif(full_hdf_path, full_tif_path)
        rich.print(f"converted to tiff, ignored files of {', '.join(kicked_tiles)}")

    def __generate_data_path(self, path: str) -> str:
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

    @staticmethod
    def __convert_hdf_to_tif(hdf_file: str, path_of_output: str) -> None:
        """
        convert hdf to tif file
        :param hdf_file:        the path to hdf file to convert
        :param path_of_output:  path to save the result at
        """

        hdf_file = gdal.Open(hdf_file, gdal.GA_ReadOnly)

        # Get the specific band you want to convert
        band_number = 1  # Change this to the desired band number
        band = hdf_file.GetRasterBand(band_number)

        driver = gdal.GetDriverByName('GTiff')
        output_dataset = driver.CreateCopy(path_of_output, band)

        band, hdf_file, output_dataset= None, None, None

    def __generate_tif_name(self, hdf_short_name: str, dir_of_tif: str) -> Tuple[str, str]:
        """
        given the hdf short name (as downloaded from NASA), generate the path of matching tif
        :param hdf_short_name:  name of hdf file
        :param dir_of_tif:      the dir of the output tif
        :return:                tuple of the generated name (with .tif) and the tile of the file
        """

        # example to hdf name: MCD19A2.A2021001.h20v05.006.2021003032218.hdf
        # format of date is YYYYDDDHHMMSS

        tile = hdf_short_name.split(".")[2]

        date_str = hdf_short_name.split(".")[4]
        year, ddd = int(date_str[0:4]), int(date_str[4:7])
        hour, minute, second = int(date_str[7:9]), int(date_str[9:11]), int(date_str[11:13])
        date = datetime(year=year, month=1, day=1, hour=hour, minute=minute, second=second) + timedelta(days=ddd)

        file_name = f"{tile}_{date.strftime(ModisHandler.__TIF_FILES_FORMAT)}.tif"

        return os.path.join(dir_of_tif, file_name), tile

    @functools.cache
    def __get_tiles_names(self) -> List[str]:
        """
        get a list of all the tiles in the project
        :return:    list of tiles in the project
        """

        return [tile_name for _, _, tile_name in self.CLIP_AND_REPROJECT_FILES]
