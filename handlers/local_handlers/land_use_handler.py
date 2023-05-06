import numpy
import numpy as np
import rasterio
from osgeo import gdal
from rasterio.plot import show
from tqdm import tqdm

from utils import gdal_utils

INPUT_LANDUSE = '/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/land_use2021e.img'
OUTPUT = '/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/land_use_out.tif'
REFERENCE_TIF = "/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/tiles/h20v05.tif"
DEFAULT_VALUE = 0
with rasterio.open(INPUT_LANDUSE, "r") as t:
    show(t)

# Dictionary of reclassification's. 19 & 30 doesn't exist in the original data
RECLASSIFICATION_DICT = {
    1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 2, 12: 2,
    13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2, 20: 2, 21: 1, 22: 1, 23: 2, 24: 2,
    25: 2, 26: 2, 27: 2, 28: 2, 29: 2, 31: 2, 32: 2, 33: 4, 34: 4, 35: 4, 36: 3,
    37: 3, 38: 4, 39: 4,
}


def reclassify(value):
    if value not in RECLASSIFICATION_DICT.keys():
        return DEFAULT_VALUE
    return RECLASSIFICATION_DICT[value]


def find_most_common_value(arr):
    unique_values, value_counts = np.unique(arr, return_counts=True)
    max_count_idx = np.argmax(value_counts)
    return unique_values[max_count_idx]


# open the original data
src = gdal.Open(INPUT_LANDUSE)
reference = gdal.Open(REFERENCE_TIF)

src_data = src.GetRasterBand(1).ReadAsArray()

reference_trans = reference.GetGeoTransform()
src_trans = src.GetGeoTransform()

output_count = {value: np.zeros((reference.RasterYSize, reference.RasterXSize)) for value in
                RECLASSIFICATION_DICT.values()}

for row in tqdm(range(src.RasterYSize)):
    for col in range(src.RasterXSize):
        if reclassify(src_data[row][col]) == DEFAULT_VALUE:
            continue

        # calculate the x,y coordinates and find the matching index on the reference raster
        x, y = gdal_utils.calc_x_y(col, row, src_trans)
        reference_col, reference_row = gdal_utils.calc_cell_index(reference_trans, x, y)
        reference_col, reference_row = int(np.round(reference_col)), int(np.round(reference_row))

        if 0 <= reference_row < reference.RasterYSize and 0 <= reference_col < reference.RasterXSize:
            output_count[reclassify(src_data[row][col])][reference_row][reference_col] += 1

output = np.zeros((reference.RasterYSize, reference.RasterXSize))
for i in tqdm(range(len(output))):
    for j in range(len(output[0])):
        cell_count_by_value = {value: count[i][j] for value, count in output_count.items()}
        if set(cell_count_by_value.values()) == {0}:
            # didn't count anything
            output[i][j] = DEFAULT_VALUE
            continue

        output[i][j] = max(cell_count_by_value, key=lambda key: cell_count_by_value[key])

driver = gdal.GetDriverByName("GTiff")
output_ds = driver.Create(OUTPUT, reference.RasterXSize, reference.RasterYSize, 1, gdal.GDT_Float32)
output_ds.SetGeoTransform(reference_trans)
output_ds.SetProjection(reference.GetProjection())
output_band = output_ds.GetRasterBand(1)
output_band.WriteArray(output)
output_ds.FlushCache()

src, reference, output_ds = None, None, None

with rasterio.open(OUTPUT, "r") as t:
    show(t)
