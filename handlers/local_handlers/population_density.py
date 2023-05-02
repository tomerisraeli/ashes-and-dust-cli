from functools import cache

from osgeo import gdal
from osgeo import ogr
import numpy as np
from tqdm import tqdm


def __generate_ring(px, py, geotransform):
    """
    generate the ring of the given coordinate


    :param px: the x value of the pixel
    :param py: the y value of the pixel
    :param geotransform: the geotransform of the reference raster
    :return:
    """

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(px - geotransform[1] / 2, py - geotransform[5] / 2)
    ring.AddPoint(px + geotransform[1] / 2, py - geotransform[5] / 2)
    ring.AddPoint(px + geotransform[1] / 2, py + geotransform[5] / 2)
    ring.AddPoint(px - geotransform[1] / 2, py + geotransform[5] / 2)
    ring.AddPoint(px - geotransform[1] / 2, py - geotransform[5] / 2)
    return ring


def __calc_cell_dimensions(x, y, geotransform):
    """
    calculate the dimensions of the cell


    :param x: the x coordinate of the cell
    :param y: the y coordinate of the cell
    :param geotransform:
    :return: dx, dy
    """

    return (
        geotransform[0] + (x + 0.5) * geotransform[1] + (y + 0.5) * geotransform[2],
        geotransform[3] + (x + 0.5) * geotransform[4] + (y + 0.5) * geotransform[5]
    )


@cache
def __get_tif_geometry(reference):
    """
    get the reference tif geometry


    :param reference:
    :return:
    """

    gt = reference.GetGeoTransform()
    # Get the width and height of the raster
    cols = reference.RasterXSize
    rows = reference.RasterYSize

    # Get the corner coordinates
    min_x = gt[0]
    max_y = gt[3]
    max_x = min_x + gt[1] * cols
    min_y = max_y + gt[5] * rows

    # Create a polygon geometry using the corner coordinates
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(min_x, min_y)
    ring.AddPoint(max_x, min_y)
    ring.AddPoint(max_x, max_y)
    ring.AddPoint(min_x, max_y)
    ring.AddPoint(min_x, min_y)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    return poly


def __is_feature_relevant(feature, raster_ds, field):
    """
    check if the given feature is relevant to the raster


    :param feature:
    :param raster_ds:
    :param field:
    :return:
    """

    poly_geom = feature.geometry()
    tif_geom = __get_tif_geometry(raster_ds)
    return poly_geom.Intersects(tif_geom) and (feature.GetFieldIndex(field) != -1)


def __calc_cell_value(features, cell_geom, field):
    """
    calc the new cell value


    :param features:
    :param cell_geom:
    :param field:
    :return:
    """
    pixel_value = np.float32(0)
    for feature in features:
        poly_geom = feature.geometry()
        if poly_geom.Intersects(cell_geom):
            intersection = poly_geom.Intersection(cell_geom)
            weight = intersection.Area() / poly_geom.Area()
            value = feature.GetField(field)
            pixel_value += np.float32(weight * value)
    return pixel_value


def polygons_to_raster(raster_path, polygon_path, field, output_raster):
    """
    convert the given polygons to a raster matching the geographic characteristic of the reference raster


    :param raster_path: the reference raster
    :param polygon_path: the path to the polygons .shp file
    :param field: the field of the data on the polygon file
    :param output_raster: the path to save the result at
    :return: None
    """

    # Load the input raster and vector files
    raster_ds = gdal.Open(raster_path)
    vector_ds = ogr.Open(polygon_path)
    layer = vector_ds.GetLayer()

    # Get the raster geotransform and projection
    geotransform = raster_ds.GetGeoTransform()
    projection = raster_ds.GetProjection()

    features = [feature for feature in layer if __is_feature_relevant(feature, raster_ds, field)]
    output_data = np.zeros((raster_ds.RasterYSize, raster_ds.RasterXSize))

    for y in tqdm(range(raster_ds.RasterYSize)):
        for x in range(raster_ds.RasterXSize):
            # Get the coordinates of the current cell
            px, py = __calc_cell_dimensions(x, y, geotransform)
            ring = __generate_ring(px, py, geotransform)

            cell_geom = ogr.Geometry(ogr.wkbPolygon)
            cell_geom.AddGeometry(ring)

            output_data[y][x] = __calc_cell_value(features, cell_geom, field)

    # Create the output raster file
    driver = gdal.GetDriverByName("GTiff")
    output_ds = driver.Create(output_raster, raster_ds.RasterXSize, raster_ds.RasterYSize, 1, gdal.GDT_Float32)
    output_ds.SetGeoTransform(geotransform)
    output_ds.SetProjection(projection)
    output_band = output_ds.GetRasterBand(1)
    output_band.WriteArray(output_data)
    output_ds.FlushCache()

    raster_ds, vector_ds = None, None
    return output_ds


if __name__ == '__main__':
    r = polygons_to_raster(
        raster_path="/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/test/h21v05.tif",
        polygon_path="/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/test/LAMS2011_2039.shp",
        field="Pop_Total",
        output_raster="/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/local_handlers/test/out.tif"
    )
