import functools
import os.path
import shutil
from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Any

import geopandas
from osgeo import gdal
from rich.progress import track
import rich
from modis_tools.auth import ModisSession
from modis_tools.resources import CollectionApi, GranuleApi
from modis_tools.granule_handler import GranuleHandler
import xarray as xr
from rioxarray import rioxarray

from data_handlers.handlers_api.download_handler import DownloadHandler
from utils import constants, gdal_utils, preprocess_utils


class ModisHandler(DownloadHandler):
    """
    a handler for data downloaded from modis

    to implement the modis handler protocol all you have to do is fill the _MODIS_DATA_<var> variables,
    the NAME and DESCRIPTION. other than this, all the functions and vars are already implemented here
    """

    SOURCE = "https://modis.gsfc.nasa.gov"
    NAME = "modis"  # TODO: move to NDVI, AOD

    """
    MODIS DATA VARIABLES
    
    
    """
    _MODIS_DATA_NAME: str = "MCD19A2"  # short name of data, used for modis query
    _MODIS_DATA_VERSION: str = "006"  # the version of the data, used for modis query
    _MODIS_DATA_BAND: int = 1  # the band the data is saved at on the hdf files from MODIS

    # MODIS CONSTANTS
    __MODIS_BBOX = [33, 28, 38, 36]  # the
    __MODIS_DATE_FORMAT = '%Y-%m-%d'
    __TIF_FILES_FORMAT = "%Y-%m-%d-%H-%M-%S"
    __MODIS_FILES_PROJECTION = "GCTP_SNSOID"    # from the hdf projection

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
        # for tile_grid, tile_shp, tile_name in self.CLIP_AND_REPROJECT_FILES:
        #     self.__create_netcdf(temp_data_path, tile_grid, tile_shp, tile_name)
        # self.__clear_temp_data(temp_data_path)

        # TODO: for each file in data_dir, convert it to a tif holding the data of the tile
        #  it will be better if each file will generate 3 tiffs, one for each tile
        #  when all the files are saved as tiffs
        #  save the tiffs on the temp_data_path dir

    def __convert_files_to_tif(self, path_of_data_dir: str, temp_data_path: str) -> None:
        """
        convert all necessary hdf files to tiff
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

            self.__convert_hdf_to_tif(full_hdf_path, full_tif_path)
            self.__clip_and_reproject_file(full_tif_path, *self.__get_tile_grid_and_clip(tile))

        rich.print(f"converted to tiff, ignored files of {', '.join(kicked_tiles)}")

    def __create_netcdf(self, data_path: str, tile_grid: str, tile_shp: str, tile_name: str, output_path) -> None:
        """
        merge all the tif files in the given directory to one netcdf file holding all the data of the tile
        :param data_path:   dir of all tif file to convert
        :param tile_grid:   path to tile grid
        :param tile_shp:    path to tile shp file (clip)
        :param tile_name:   tile name
        :param output_path: path of output - results will be saved at this file
        :returns:           None
        """
        rich.print("merging data to .nc file, this may take some time")
        modified_datasets = []
        for file_name in os.listdir(data_path):
            if ".tif" not in file_name:
                continue

            with xr.open_dataset(os.path.join(data_path, file_name)) as data:
                data['time'] = [self.__get_date_from_tif(file_name)]
                modified_datasets.append(data)

        merged_data = xr.concat(modified_datasets, dim='time')
        merged_data.to_netcdf(output_path)

    def __get_date_from_tif(self, tif_name: str) -> datetime:
        pass

    @staticmethod
    def __clear_temp_data(data_path: str) -> None:
        """
        clear all temp data created from memory
        :param data_path:   dir of all tif files to remove
        :returns:           None
        """

        shutil.rmtree(data_path)

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
        dataset_file = hdf_file.GetSubDatasets()[0][0]
        dataset = gdal.Open(dataset_file, gdal.GA_ReadOnly)

        gdal.Translate(path_of_output, dataset, format="GTiff", outputSRS="EPSG:2039", bandList=[1])

        # output_raster = gdal.GetDriverByName("GTiff").Create(
        #     path_of_output,
        #     dataset.RasterXSize,
        #     dataset.RasterYSize,
        #     1,
        #     gdal.GDT_Float32
        # )
        # output_raster.SetGeoTransform(dataset.GetGeoTransform())
        # output_raster.SetProjection(dataset.GetProjection())
        # output_raster.GetRasterBand(1).WriteArray(dataset.ReadAsArray()[0])


        # output_raster = gdal.Translate(path_of_output, dataset, format="GTiff")
        # output_raster.SetProjection(dataset.GetProjection())
        dataset, hdf_file, output_raster = None, None, None

    @staticmethod
    def __clip_and_reproject_file(tif_file, tile_grid, tile_shp):
        """
        clip and reproject the given file
        :param tif_file:    path of file to operate
        :param tile_grid:   the grid to reproject to
        :param tile_shp:    the shp to clip to
        """

        preprocess_utils.clip_and_reproject(
            tif_file, tile_grid, tile_shp, tif_file,
            # src_crs=ModisHandler.__MODIS_FILES_PROJECTION
        )

    @staticmethod
    def __generate_tif_name(hdf_short_name: str, dir_of_tif: str) -> Tuple[str, str]:
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

    @functools.cache
    def __get_tile_grid_and_clip(self, tile_name: str) -> Tuple[Any, Any]:
        """
        get the grid and clip objects of the given tile
        :param tile_name:   the tile to get file for
        :returns:           tuple of tile_grid and tile_chp
        """

        for tile_clip, tile_grid, current_tile_name in self.CLIP_AND_REPROJECT_FILES:
            if tile_name == current_tile_name:
                clip = geopandas.read_file(tile_clip)
                grid = rioxarray.open_rasterio(tile_grid)
                return grid, clip

        raise KeyError(f"{tile_name} is not a valid tile name")
