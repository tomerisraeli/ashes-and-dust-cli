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

with rasterio.open(INPUT_LANDUSE, "r") as t:
    show(t)

# Dictionary of reclassification's. 19 & 30 doesn't exist in the original data
RECLASSIFICATION_DICT = {
    1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1, 11: 2, 12: 2,
    13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2, 20: 2, 21: 1, 22: 1, 23: 2, 24: 2,
    25: 2, 26: 2, 27: 2, 28: 2, 29: 2, 31: 2, 32: 2, 33: 4, 34: 4, 35: 4, 36: 3,
    37: 3, 38: 4, 39: 4,
}

NUMBER_OF_VARS = len(set(RECLASSIFICATION_DICT.values()))


def reclassify_data(data):
    for key, value in RECLASSIFICATION_DICT.items():
        data[numpy.where(data == key)] = value
    return data


def find_most_common_value(arr):
    unique_values, value_counts = np.unique(arr, return_counts=True)
    max_count_idx = np.argmax(value_counts)
    return unique_values[max_count_idx]


# open the original data
src = gdal.Open(INPUT_LANDUSE)
reference = gdal.Open(REFERENCE_TIF)

# generate all the cells coordinates in the raster
src_cells = gdal_utils.get_cells(src)
src_data = src.GetRasterBand(1).ReadAsArray()
src_data = reclassify_data(src_data)

reference_cells = gdal_utils.get_cells(reference)

reference_trans = reference.GetGeoTransform()
src_trans = src.GetGeoTransform()

reference_cell_height = reference_trans[5]
reference_cell_width = reference_trans[1]
reference_cell_max_dist = (reference_cell_width ** 2 + reference_cell_height ** 2) ** 0.5

output_data = np.zeros((reference.RasterYSize, reference.RasterXSize))
for row, col, x, y in tqdm(reference_cells):
    # create cell geometry
    cell_geo = gdal_utils.get_cell_geometry(col, row, reference_trans)

    # generate bbox
    x_min = x - reference_cell_max_dist
    x_max = x + reference_cell_width + reference_cell_max_dist
    y_min = y - reference_cell_max_dist
    y_max = y + reference_cell_height + reference_cell_max_dist

    bbox_cols, bbox_rows = gdal_utils.get_cells_indexes(src, x_min, y_min, x_max, y_max)
    # if bbox_rows.size > 0 and bbox_cols.size > 0:
    #     print(bbox_cols[0], " -> ", bbox_cols[-1], ", ", bbox_rows[0], " -> ", bbox_rows[-1])
    # else:
    #     print("Nine")
    # filtered_cells = [cell for cell in src_cells if x_min <= cell[2] <= x_max and y_min <= cell[3] <= y_max]
    # print(f"checking {len(filtered_cells)} cells")
    total_area_per_value = {value: 0 for value in set(RECLASSIFICATION_DICT.values())}
    for src_row in bbox_rows:
        for src_col in bbox_cols:
            if src_data[src_row][src_col] == 255:
                # invalid value or empty
                continue
            # src_cell_geo = gdal_utils.get_cell_geometry(src_col, src_row, src_trans)
            # intersection = cell_geo.Intersection(src_cell_geo)
            total_area_per_value[src_data[src_row][src_col]] += 1
                # intersection.Area()
    output_data[row][col] = max(total_area_per_value, key=lambda k: total_area_per_value[k])
# Create the output raster file
driver = gdal.GetDriverByName("GTiff")
output_ds = driver.Create(OUTPUT, reference.RasterXSize, reference.RasterYSize, 1, gdal.GDT_Float32)
output_ds.SetGeoTransform(reference_trans)
output_ds.SetProjection(reference.GetProjection())
output_band = output_ds.GetRasterBand(1)
output_band.WriteArray(output_data)
output_ds.FlushCache()

src, reference = None, None

with rasterio.open(OUTPUT, "r") as t:
    show(t)
