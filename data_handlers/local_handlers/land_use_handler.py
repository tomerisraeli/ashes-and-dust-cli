import os

import numpy as np
import rich
from osgeo import gdal

from data_handlers.local_handlers.convert_handler import ConvertHandler
from utils import gdal_utils


class LandUseHandler(ConvertHandler):
    """
    land use handler holds two functions to manage the validation and preprocessing of the land use data

    land_use2021e.img is a raster holding the LAMAS classification of Israel land
    """

    SOURCE: str = "local"
    NAME: str = "Land Use"
    DESCRIPTION: str = "classification of land use over Israel"

    _NECESSARY_FILES = [
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

        src_raster = gdal.Open(os.path.join(self._get_data_dir(path), self._NECESSARY_FILES[0]))

        reference = gdal.Open(tile_grid)
        output_count = self.__count_after_classification(src_raster, reference, task_progress, progress_bar)

        # after counting the data, the code now generate the new raster
        # the value for each cell is set to be the value that appears the most at the cell

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

    def __count_after_classification(self, src_raster, reference, task_progress, progress_bar):
        """
        reclassify the data than count the number of times each value appears in each cell
        :param src_raster:      the src data raster holding the original classification
        :param reference:       the reference raster
        :param task_progress:   id of the task associated with the calculation
        :param progress_bar:    the progress bar to update
        :return:                np array holding a dict with the count for each value on every cell
        """

        rows = src_raster.RasterYSize
        cols = src_raster.RasterXSize
        __progress_bar_delta = 1 / (rows * cols)

        src_data = src_raster.GetRasterBand(1).ReadAsArray()
        src_trans = src_raster.GetGeoTransform()

        reference_trans = reference.GetGeoTransform()

        output_count = {value: np.zeros((rows, cols)) for value in LandUseHandler.RECLASSIFICATION_DICT.values()}

        for row in range(rows):
            for col in range(cols):
                progress_bar.update(task_progress, advance=__progress_bar_delta)

                if self.__reclassify(src_data[row][col]) == LandUseHandler.DEFAULT_VALUE:
                    continue

                # calculate the x,y coordinates and find the matching index on the reference raster
                x, y = gdal_utils.calc_x_y(col, row, src_trans)
                reference_col, reference_row = gdal_utils.calc_cell_index(reference_trans, x, y)
                reference_col, reference_row = round(reference_col), round(reference_row)

                if 0 <= reference_row < reference.RasterYSize and 0 <= reference_col < reference.RasterXSize:
                    output_count[self.__reclassify(src_data[row][col])][reference_row][reference_col] += 1
        return output_count

    @staticmethod
    def __reclassify(value):
        """
        get the reclassification of the data
        :param value:   the value to reclassify
        :return:        the reclassification value, if the given value doesn't exist on the RECLASSIFICATION_DICT the
                        default value is returned
        """
        if value not in LandUseHandler.RECLASSIFICATION_DICT:
            return LandUseHandler.DEFAULT_VALUE
        return LandUseHandler.RECLASSIFICATION_DICT[value]


if __name__ == '__main__':
    os.chdir("/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli")
    LandUseHandler().preprocess(
        '/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/data_preprocess')
