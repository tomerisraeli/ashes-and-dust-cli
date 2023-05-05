import numpy
import numpy as np
import rasterio
from rasterio.plot import show
from rasterio.windows import from_bounds
from rich.progress import track
import pyproj

INPUT_LANDUSE = '/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/land_use2021e.img'
OUTPUT = '/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/land_use_out.tif'
REFERENCE_TIF = "/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/tiles/h20v05.tif"

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
    # Get the unique values and their counts in the flattened array
    unique_values, value_counts = np.unique(arr, return_counts=True)

    # Find the index of the maximum count
    max_count_idx = np.argmax(value_counts)

    # Return the most common value
    return unique_values[max_count_idx]


# open the original data
with rasterio.open(INPUT_LANDUSE, 'r') as src, rasterio.open(REFERENCE_TIF, "r") as reference:
    # show(src)
    width = reference.width
    height = reference.height
    output = np.zeros((width, height))

    transformer = pyproj.Transformer.from_crs(reference.crs, src.crs)

    for x in track(range(width)):
        for y in range(height):
            x_min = reference.bounds.left + x * reference.res[0]
            y_min = reference.bounds.bottom + y * reference.res[1]
            x_max = reference.bounds.left + (x + 1) * reference.res[0]
            y_max = reference.bounds.bottom + (y + 1) * reference.res[1]

            x_min, y_min = transformer.transform(x_min, y_min)
            x_max, y_max = transformer.transform(x_max, y_max)
            window = from_bounds(x_min, y_min, x_max, y_max, src.transform)
            cell_data = src.read(window=window)

            cell_data = reclassify_data(cell_data).flatten()
            print(f"number of cells: {len(cell_data)}")
            # cell_data = cell_data[cell_data != 255]  # remove empty values

            if cell_data.size > 0:
                output[x][y] = 1
                # output[x][y] = find_most_common_value(cell_data)

    with rasterio.open(OUTPUT, 'w', **reference.profile) as out:
        out.write(output, 1)
with rasterio.open(OUTPUT, 'r') as ras:
    show(ras)