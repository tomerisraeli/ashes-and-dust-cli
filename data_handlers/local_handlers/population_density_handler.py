import os

import numpy as np
from osgeo import ogr, gdal
from data_handlers.local_handlers.convert_handler import ConvertHandler
from utils import constants, gdal_utils
from utils.gdal_utils import get_cell_geometry


class PopulationDensityHandler(ConvertHandler):
    SOURCE: str = "local"
    NAME: str = "Population Density"
    DESCRIPTION: str = "the population density over israel in 2011, units=1000[peoples]"

    _NECESSARY_FILES = [
        "LAMS2011_2039.shp",
        "LAMS2011_2039.cpg",
        "LAMS2011_2039.dbf",
        "LAMS2011_2039.prj",
        "LAMS2011_2039.qmd",
        "LAMS2011_2039.shx"
    ]

    def _single_tile_preprocess(self, path, tile_clip, tile_grid, tile_name, output_tif,
                                task_progress, progress_bar):

        polygon_path = os.path.join(self._get_data_dir(path), self._NECESSARY_FILES[0])
        field = constants.CONFIG.get_key(constants.CONFIG.Keys.population_density_value_key)

        # convert the given polygons to a raster matching the geographic characteristic of the reference raster
        #
        # to make the conversion faster, the code loops over all the polygons and finds the cells that are relevant to
        # the current polygon instead of finding the polygons that are relevant to the cell which is harder

        # Load the input raster and vector files
        raster_ds = gdal.Open(tile_grid)
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

        __task_advancement = 1 / (layer.GetFeatureCount())
        for feature in layer:
            if feature.GetFieldIndex(field) == -1:
                # features doesn't hold the wanted field, no need to ran than
                progress_bar.update(task_progress, advance=__task_advancement)
                continue

            geometry = feature.GetGeometryRef()
            x_min, x_max, y_min, y_max = geometry.GetEnvelope()

            # to make sure we don't miss any cell, we will make the bbox bigger at each direction
            x_min -= dist
            x_max += dist
            y_min -= dist
            y_max += dist

            # we now want to get only the cells that are in the bounding box
            filtered_cells = [cell for cell in cells if x_min <= cell[2] <= x_max and y_min <= cell[3] <= y_max]

            feature_intersections_progress = progress_bar.add_task("[grey]current polygon calculation ",
                                                                   total=len(filtered_cells))
            value = feature.GetField(field)
            feature_area = geometry.Area()

            for row, col, _, _ in filtered_cells:
                cell_geom = get_cell_geometry(col, row, transform)

                intersection = geometry.Intersection(cell_geom)
                weight = intersection.Area() / feature_area
                output_data[row][col] += np.float32(weight * value)
                progress_bar.update(feature_intersections_progress, advance=1)

            progress_bar.remove_task(feature_intersections_progress)
            progress_bar.update(task_progress, advance=__task_advancement)

        self._create_tif(raster_ds, output_tif, output_data)

        # free objects and close them
        raster_ds, vector_ds, output_raster = None, None, None
