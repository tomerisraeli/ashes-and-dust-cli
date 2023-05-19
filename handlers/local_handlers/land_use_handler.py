import os

import geopandas
import numpy as np
import rich
from osgeo import gdal
from rich.progress import track
from rioxarray import rioxarray
from tqdm import tqdm

from handlers.convert_handler import ConvertHandler
from handlers.handler import LocalHandler
from utils import gdal_utils


class LandUseHandler(ConvertHandler):
    """
    land use handler holds two functions to manage the validation and preprocessing of the land use data
    """

    SOURCE: str = "local"
    NAME: str = "Land Use"
    DESCRIPTION: str = "classification of land use over Israel"

    __NECESSARY_FILES = [
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

    def _single_tile_preprocess(self, path, tile_clip, tile_grid, tile_name, output_tif,
                                task_progress, progress_bar):

        src_raster = gdal.Open(os.path.join(self._get_data_dir(path), self.__NECESSARY_FILES[0]))
        reference = gdal.Open(tile_grid)

        src_data = src_raster.GetRasterBand(1).ReadAsArray()
        reference_trans = reference.GetGeoTransform()
        src_trans = src_raster.GetGeoTransform()

        output_count = {value: np.zeros((reference.RasterYSize, reference.RasterXSize)) for value in
                        LandUseHandler.RECLASSIFICATION_DICT.values()}

        rows = src_raster.RasterYSize
        cols = src_raster.RasterXSize
        __progress_bar_delta = 1 / (rows * cols)

        for row in range(rows):
            for col in range(cols):
                if self.__reclassify(src_data[row][col]) == LandUseHandler.DEFAULT_VALUE:
                    progress_bar.update(task_progress, advance=__progress_bar_delta)
                    continue

                # calculate the x,y coordinates and find the matching index on the reference raster
                x, y = gdal_utils.calc_x_y(col, row, src_trans)
                reference_col, reference_row = gdal_utils.calc_cell_index(reference_trans, x, y)
                reference_col, reference_row = int(np.round(reference_col)), int(np.round(reference_row))

                if 0 <= reference_row < reference.RasterYSize and 0 <= reference_col < reference.RasterXSize:
                    output_count[self.__reclassify(src_data[row][col])][reference_row][reference_col] += 1
                progress_bar.update(task_progress, advance=__progress_bar_delta)

        rich.print("creating tif")
        output = np.zeros((reference.RasterYSize, reference.RasterXSize))
        for i in range(len(output)):
            for j in range(len(output[0])):
                cell_count_by_value = {value: count[i][j] for value, count in output_count.items()}
                if set(cell_count_by_value.values()) == {0}:
                    # didn't count anything
                    output[i][j] = LandUseHandler.DEFAULT_VALUE
                    continue
                output[i][j] = max(cell_count_by_value, key=lambda key: cell_count_by_value[key])

        self._create_tif(reference, output_tif, output)

        reference, output_ds = None, None

    def __reclassify(self, value):
        if value not in LandUseHandler.RECLASSIFICATION_DICT:
            return LandUseHandler.DEFAULT_VALUE
        return LandUseHandler.RECLASSIFICATION_DICT[value]


if __name__ == '__main__':
    os.chdir("/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli")
    LandUseHandler().preprocess('/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/data_preprocess')