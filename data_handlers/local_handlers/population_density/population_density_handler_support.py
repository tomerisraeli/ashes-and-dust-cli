from osgeo import gdal, ogr
import numpy as np
from rich.progress import Progress

from utils import gdal_utils
from utils.gdal_utils import get_cell_geometry


def polygons_to_raster(raster_path, polygon_path, field, output_raster):
    """
    convert the given polygons to a raster matching the geographic characteristic of the reference raster


    :param raster_path: the reference raster
    :param polygon_path: the path to the polygons .shp file
    :param field: the field of the data on the polygon file
    :param output_raster: the path to save the result at
    :return: None
    """

    # to make the conversion faster, the code loops over all the polygons and finds the cells that a relevant to
    # this polygon instead of finding the polygons that are relevant to the cell which is harder

    # Load the input raster and vector files
    raster_ds = gdal.Open(raster_path)
    vector_ds = ogr.Open(polygon_path)

    layer = vector_ds.GetLayer()

    # get some basic values of the reference raster
    transform = raster_ds.GetGeoTransform()
    projection = raster_ds.GetProjection()

    pixel_width = transform[1]
    pixel_height = transform[5]
    rows = raster_ds.RasterYSize
    cols = raster_ds.RasterXSize

    # generate all the cells coordinates in the raster
    output_data = np.zeros((rows, cols))
    dist = (pixel_width ** 2 + pixel_height ** 2) ** 0.5  # the max distance between two points in a cell
    cells = gdal_utils.get_cells(raster_ds)

    with Progress() as progress:
        features_iteration_progress = progress.add_task("[bold]converting polygons...", total=layer.GetFeatureCount())
        for feature in layer:
            progress.update(features_iteration_progress, advance=1)
            if feature.GetFieldIndex(field) == -1:
                # features doesn't hold the wanted field, no need to ran than
                continue

            geometry = feature.GetGeometryRef()
            x_min, x_max, y_min, y_max = geometry.GetEnvelope()

            # to make sure we don't miss any cell, we will make the bbox bigger at each direction
            x_min -= dist
            x_max += dist
            y_min -= dist
            y_max += dist

            # we now want to get all the cells that are in the bounding box
            filtered_cells = [cell for cell in cells if x_min <= cell[2] <= x_max and y_min <= cell[3] <= y_max]

            feature_intersections_progress = progress.add_task("[grey]current polygon calculation ",
                                                               total=len(filtered_cells))
            value = feature.GetField(field)
            feature_area = geometry.Area()

            for row, col, _, _ in filtered_cells:
                progress.update(feature_intersections_progress, advance=1)

                cell_geom = get_cell_geometry(col, row, transform)

                intersection = geometry.Intersection(cell_geom)
                weight = intersection.Area() / feature_area
                output_data[row][col] += np.float32(weight * value)

            progress.remove_task(feature_intersections_progress)

    # Create the output raster file
    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(output_raster, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)
    output_ds.SetGeoTransform(transform)
    output_ds.SetProjection(projection)
    output_band = output_ds.GetRasterBand(1)
    output_band.WriteArray(output_data)
    output_ds.FlushCache()

    # free objects and close them
    raster_ds, vector_ds, output_raster = None, None, None
