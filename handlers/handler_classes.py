import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))
from utils import constants
import rioxarray
import geopandas
from datetime import datetime


class Handler:
    def __init__(self, path: str, start_date, end_date, overwrite: bool):
        self.path = path
        self.start_date = start_date
        self.end_date = end_date
        self.overwrite = overwrite


class LocalHandler(Handler):
    def __init__(self, path, start_date, end_date, overwrite):
        super().__init__(path, start_date, end_date, overwrite)


class DownloadHandler(Handler):
    def __init__(self, path, start_date, end_date, overwrite):
        super().__init__(path, start_date, end_date, overwrite)


class DistanceFromWaterHandler(LocalHandler):
    def __init__(self, path, start_date, end_date, overwrite):
        super().__init__(path, start_date, end_date, overwrite)
        self.name = "dist_from_water"
        self.source = "source"

    def confirm_existence(self):
        print("confirm_existence")

    def preprocess(self):
        current_working_dir = os.getcwd()
        tile_list_shp = [f'{self.path}/h20v05.shp',
                         f'{self.path}/h21v05.shp',
                         f'{self.path}/h21v06.shp']

        geotif_of_tile = [f'{self.path}/h20v05.tif',
                          f'{self.path}/h21v05.tif',
                          f'{self.path}/h21v06.tif']
        # geotif_road_all_of_israel
        geotif_land_use = [f"{self.path}/dist_massive_water.tif"
            , f"{self.path}/dist_to_water.tif"]

        for tile, tile_grid in zip(tile_list_shp, geotif_of_tile):
            geodf = geopandas.read_file(tile)
            to_match = rioxarray.open_rasterio(tile_grid)
            for land in geotif_land_use:
                xds1 = rioxarray.open_rasterio(land)  # land use
                # we clip the raster of the land use
                clipped = xds1.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)  # clip the raster
                xds_repr_match = clipped.rio.reproject_match(to_match)
                data_reprojected = xds_repr_match.rio.reproject("EPSG:2039")
                data_reprojected.to_netcdf(f'{self.path}/dist_from_water/', f'{os.path.basename(tile)}-{os.path.basename(land)}.nc')
                # # visualize data
                # plt.imshow(data_reprojected.squeeze())
                # plt.show()
                # plt.clf()


def generate_classes(path, start_date, end_date, overwrite):
    for name in constants.HANDLERS:
        class_obj = globals().get(name)
        instance_obj = class_obj(path, start_date, end_date, overwrite)
        instance_obj.confirm_existence()


