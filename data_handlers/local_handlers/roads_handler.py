import functools
import os
import numpy as np
import scipy
from osgeo import ogr, gdal
from data_handlers.convert_handler import ConvertHandler
from utils import gdal_utils


class RoadsHandler(ConvertHandler):
    SOURCE: str = "local"
    NAME: str = "distance form highways"
    DESCRIPTION: str = "distance between the center of the cell to the closest major road in israel"

    _NECESSARY_FILES = [
        "raw_data/highways_l.shp",
        "raw_data/highways_l.cpg",
        "raw_data/highways_l.dbf",
        "raw_data/highways_l.prj",
        "raw_data/highways_l.sbn",
        "raw_data/highways_l.sbx",
        "raw_data/highways_l.shp.xml",
        "raw_data/highways_l.shx"
    ]

    def _single_tile_preprocess(self, path, tile_clip, tile_grid, tile_name, output_tif, task_progress, progress_bar):
        shp_path = os.path.join(self._get_data_dir(path), self.__NECESSARY_FILES[0])

        reference = gdal.Open(tile_grid)
        transform = reference.GetGeoTransform()

        rows = reference.RasterYSize
        cols = reference.RasterXSize

        output_data = np.zeros((rows, cols))
        __progress_bar_delta = 1 / (rows * cols)

        points, shp_spatial_ref = self.__load_all_road_points(shp_path)

        for row in range(rows):
            for col in range(cols):
                cell_center = gdal_utils.calc_x_y(col + 0.5, row + 0.5, transform)
                distances = scipy.spatial.distance.cdist([cell_center], points)[0]
                output_data[row][col] = np.min(distances)
                progress_bar.update(task_progress, advance=__progress_bar_delta)

        self._create_tif(reference, output_tif, output_data)

    @functools.cache
    def __load_all_road_points(self, roads_path: str):
        """
        get a list of the points in the
        :param roads_path:  path to .shp file
        :return:            a list of all road points in .shp file
        """
        roads_shp = ogr.Open(roads_path)

        if not roads_shp:
            raise FileExistsError(f"couldn't open {roads_path}")
        roads_layer = roads_shp.GetLayer()
        spatial_ref = roads_layer.GetExtent()

        points = []
        for road in roads_layer:
            points += road.GetGeometryRef().GetPoints()
        roads_shp = None
        return np.array(points, dtype=float), spatial_ref


if __name__ == '__main__':
    os.chdir("/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli")

    RoadsHandler().preprocess(
        "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My "
        "Drive/year_2/Magdad/data_preprocess")
