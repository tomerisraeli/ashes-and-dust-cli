import os

import geopandas
import numpy as np
from osgeo import gdal
from rich.progress import track
from rioxarray import rioxarray
from tqdm import tqdm

from handlers.handler import LocalHandler
from utils import gdal_utils


class LandUseHandler(LocalHandler):
    """
    land use handler holds two functions to manage the validation and preprocessing of the land use data
    """

    SOURCE: str = "local"
    NAME: str = "Land Use Classification"
    DESCRIPTION: str = "classification of land use over Israel"

    NECESSARY_FILES = [
        "land_use2021e.img"
    ]

    DEFAULT_VALUE = 0

    # Dictionary of reclassification. 19 & 30 doesn't exist in the original data
    RECLASSIFICATION_DICT = {
        1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 2, 12: 2,
        13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2, 20: 2, 21: 1, 22: 1, 23: 2, 24: 2,
        25: 2, 26: 2, 27: 2, 28: 2, 29: 2, 31: 2, 32: 2, 33: 4, 34: 4, 35: 4, 36: 3,
        37: 3, 38: 4, 39: 4
    }

    def confirm_existence(self, path: str):
        missing_files = []
        for file in LandUseHandler.NECESSARY_FILES:
            file_path = os.path.join(self.__get_land_use_dir(path), file)
            if not os.path.isfile(file_path):
                missing_files.append(file_path)
        return missing_files

    def preprocess(self, path):
        src_raster_path = os.path.join(self.__get_land_use_dir(path), LandUseHandler.NECESSARY_FILES[0])
        src_raster = gdal.Open(src_raster_path)
        if not src_raster:
            raise FileExistsError(f"can't open {src_raster}")

        for tile_clip, tile_grid, tile_name in LandUseHandler.CLIP_AND_REPROJECT_FILES:
            nc_path = os.path.join(self.__get_land_use_dir(path),
                                   f"{self.NAME.replace(' ', '_').lower()}_{tile_name}.nc"
                                   )
            tif_path = os.path.join(self.__get_land_use_dir(path),
                                    f"{self.NAME.replace(' ', '_').lower()}_{tile_name}.tif"
                                    )

            self.__preprocess_one_tif(src_raster, tile_grid, tif_path)

            clip_file = geopandas.read_file(tile_clip)

            # open the in-memory raster using rasterio, clip, reproject and save it nicely
            raster = rioxarray.open_rasterio(tif_path)
            raster = raster.rio.clip(clip_file.geometry.values, clip_file.crs, drop=False, invert=False)
            raster = raster.rio.reproject("EPSG:2039")
            raster.to_netcdf(nc_path)

    def __preprocess_one_tif(self, src_raster, reference_tif_path, output_path):

        reference = gdal.Open(reference_tif_path)
        src_data = src_raster.GetRasterBand(1).ReadAsArray()
        reference_trans = reference.GetGeoTransform()
        src_trans = src_raster.GetGeoTransform()

        output_count = {value: np.zeros((reference.RasterYSize, reference.RasterXSize)) for value in
                        LandUseHandler.RECLASSIFICATION_DICT.values()}

        for row in track(range(src_raster.RasterYSize),
                         description="reclassifying land use..."):
            for col in range(src_raster.RasterXSize):
                if self.__reclassify(src_data[row][col]) == LandUseHandler.DEFAULT_VALUE:
                    continue

                # calculate the x,y coordinates and find the matching index on the reference raster
                x, y = gdal_utils.calc_x_y(col, row, src_trans)
                reference_col, reference_row = gdal_utils.calc_cell_index(reference_trans, x, y)
                reference_col, reference_row = int(np.round(reference_col)), int(np.round(reference_row))

                if 0 <= reference_row < reference.RasterYSize and 0 <= reference_col < reference.RasterXSize:
                    output_count[self.__reclassify(src_data[row][col])][reference_row][reference_col] += 1

        output = np.zeros((reference.RasterYSize, reference.RasterXSize))
        for i in track(range(len(output)),
                       description="preparing tif"):
            for j in range(len(output[0])):
                cell_count_by_value = {value: count[i][j] for value, count in output_count.items()}
                if set(cell_count_by_value.values()) == {0}:
                    # didn't count anything
                    output[i][j] = LandUseHandler.DEFAULT_VALUE
                    continue

                output[i][j] = max(cell_count_by_value, key=lambda key: cell_count_by_value[key])

        driver = gdal.GetDriverByName("GTiff")
        output_ds = driver.Create(output_path, reference.RasterXSize, reference.RasterYSize, 1, gdal.GDT_Float32)
        output_ds.SetGeoTransform(reference_trans)
        output_ds.SetProjection(reference.GetProjection())
        output_band = output_ds.GetRasterBand(1)
        output_band.WriteArray(output)
        output_ds.FlushCache()

        reference, output_ds = None, None

    def __get_land_use_dir(self, path: str):
        return os.path.join(path, "land_use")

    def __reclassify(self, value):
        if value not in LandUseHandler.RECLASSIFICATION_DICT.keys():
            return LandUseHandler.DEFAULT_VALUE
        return LandUseHandler.RECLASSIFICATION_DICT[value]
