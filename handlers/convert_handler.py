import os

import geopandas
from osgeo import gdal
from rioxarray import rioxarray

from handlers.handler import LocalHandler


class ConvertHandler(LocalHandler):
    """
    a general implementation of a handler that create the tiff from other sources
    """

    __NECESSARY_FILES = []  # relative paths from the data dir

    def confirm_existence(self, path: str):
        missing_files = []
        for file in self.__NECESSARY_FILES:
            file_path = os.path.join(self.__get_data_dir(path), file)
            if not os.path.isfile(file_path):
                missing_files.append(file_path)
        return missing_files

    def preprocess(self, path):
        for tile_clip, tile_grid, tile_name in self.CLIP_AND_REPROJECT_FILES:
            nc_path, tif_path = self.__get_files_paths_of_tile(path, tile_name)

            self.__single_tile_preprocess(tile_clip, tile_grid, tile_name, tif_path)

            clip_file = geopandas.read_file(tile_clip)
            raster = rioxarray.open_rasterio(tif_path)
            raster = raster.rio.clip(clip_file.geometry.values, clip_file.crs, drop=False, invert=False)
            raster = raster.rio.reproject("EPSG:2039")
            raster.to_netcdf(nc_path)

    def __single_tile_preprocess(self, tile_clip, tile_grid, tile_name, output_tif):
        """
        make all preprocess calculations on just one tile.
        the generated tif will be clipped than saved as .nc file, you may want to use the `__create_tif` function
        :param tile_clip:   path of the tile .shp clip file
        :param tile_grid:   path of the tile grid .tif file
        :param tile_name:   the name of the tile
        :param output_tif:  the path to save the result tif at
        :return:
        """
        ...

    def __create_tif(self, reference, output_path, tif_data):
        """
        create a tiff file with the transform and projection of the reference raster but with tif_data
        :param reference:   the gdal object of the reference tif
        :param output_path: the path of the tiff created
        :param tif_data:    the data to store on the tiff, must be with the same dimensions as the reference raster
        :return:            None
        """

        driver = gdal.GetDriverByName("GTiff")
        output_ds = driver.Create(output_path, reference.RasterXSize, reference.RasterYSize, 1, gdal.GDT_Float32)
        output_ds.SetGeoTransform(reference.GetGeoTransform())
        output_ds.SetProjection(reference.GetProjection())
        output_band = output_ds.GetRasterBand(1)
        output_band.WriteArray(tif_data)
        output_ds.FlushCache()

    def __get_data_dir(self, path: str):
        """
        get the path of the sub dir holding the all the data of the handler
        :param path:    path of root dir
        :return:        path of data dir as str
        """
        return os.path.join(path, self.NAME.replace(" ", "_"))

    def __get_files_paths_of_tile(self, path, tile_name):
        """
        get the output tif and nc files paths for the given tile name
        :param path:        path of root dir
        :param tile_name:   the name of the tile
        :return:            nc_path, tif_path
        """

        general_path = os.path.join(self.__get_data_dir(path), f"{self.NAME}_{tile_name}.nc".replace(" ", "_").lower())
        return f"{general_path}.nc", f"{general_path}.tif"
