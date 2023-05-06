from functools import cache

import numpy as np
from osgeo import ogr


def calc_x_y(col, row, transform):
    """
    calculate the xy coordinate of the given index(bottom left)


    :param col:
    :param row:
    :param transform:
    :return:
    """

    x = transform[0] + col * transform[1] + row * transform[2]
    y = transform[3] + col * transform[4] + row * transform[5]
    return x, y


def calc_cell_index(transform, x, y):
    """
    calc the row and col of the given cell in the given transform


    :param transform:
    :param x:
    :param y:
    :return:
    """

    # about this function calculation.
    # as the geo coordinates of cell in the raster are given as
    # X_geo = GT(0) + X_pixel * GT(1) + Y_line * GT(2)
    # Y_geo = GT(3) + X_pixel * GT(4) + Y_line * GT(5)
    # (taken from https://gdal.org/tutorials/geotransforms_tut.html)
    # we can move the free var to the left side and write this as matrix which we can find the opposite of

    mat = [[transform[1], transform[2]],
           [transform[4], transform[5]]
           ]

    inverse_mat = np.linalg.inv(mat)
    vec = [x - transform[0], y - transform[3]]
    col, row = inverse_mat.dot(vec)
    return col, row


@cache
def get_cell_geometry(col, row, geotransform):
    """
    get the geometry of the given cell


    :param row:
    :param col:
    :param geotransform: the geotransform of the reference raster
    :return:
    """

    ring = ogr.Geometry(ogr.wkbLinearRing)

    ring.AddPoint(*calc_x_y(col, row, geotransform))
    ring.AddPoint(*calc_x_y(col + 1, row, geotransform))
    ring.AddPoint(*calc_x_y(col + 1, row + 1, geotransform))
    ring.AddPoint(*calc_x_y(col, row + 1, geotransform))
    ring.AddPoint(*calc_x_y(col, row, geotransform))

    cell_geom = ogr.Geometry(ogr.wkbPolygon)
    cell_geom.AddGeometry(ring)
    return cell_geom


def get_cells(raster):
    """
    get all the cells in the raster


    :param raster: the raster (gdal dataset)
    :return: an array holding all the cell as tuples of (row, col, x, y) where x,y are the bottom left corner of the cell
    """

    transform = raster.GetGeoTransform()
    rows = raster.RasterYSize
    cols = raster.RasterXSize

    cells = []
    for row in range(rows):
        for col in range(cols):
            x, y = calc_x_y(col, row, transform)
            cells.append((row, col, x, y))

    return cells


def get_cells_indexes(raster, x_min, y_min, x_max, y_max):
    """
    get the indices of the cells in the given range


    :param transform:
    :param x_min:
    :param y_min:
    :param x_max:
    :param y_max:
    :return:
    """

    transform = raster.GetGeoTransform()

    min_col, min_row = calc_cell_index(transform, x_min, y_min)
    max_col, max_row = calc_cell_index(transform, x_max, y_max)

    # validate the max, min
    min_col, max_col = min(min_col, max_col), max(min_col, max_col)
    min_row, max_row = min(min_row, max_row), max(min_row, max_row)

    # round results
    min_col, min_row = int(np.floor(min_col)), int(np.floor(min_row))
    max_col, max_row = int(np.ceil(max_col)), int(np.ceil(max_row))

    # validate indices
    min_col, min_row = max(0, min_col), max(0, min_row)
    max_col, max_row = min(raster.RasterXSize - 1, max_col), min(raster.RasterYSize - 1, max_row)

    # Get the row and column indices of all cells within the bounding box
    cols, rows = np.arange(min_col, max_col + 1), np.arange(min_row, max_row + 1)

    return cols, rows
