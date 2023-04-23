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


class tifHandler(Handler):
    def run_tif(self, tif_name, file_name, path):
        tile_list_shp = [f'{path}/{constants.REQUIRED_FILE[0]}',
                         f'{path}/{constants.REQUIRED_FILE[1]}',
                         f'{path}/{constants.REQUIRED_FILE[2]}']

        geotif_of_tile = [f'{path}/{constants.REQUIRED_FILE[3]}',
                          f'{path}/{constants.REQUIRED_FILE[4]}',
                          f'{path}/{constants.REQUIRED_FILE[5]}']
        # geotif_road_all_of_israel
        geotif_land_use = [f"{file_name}"]

        for tile, tile_grid in zip(tile_list_shp, geotif_of_tile):
            geodf = geopandas.read_file(tile)
            to_match = rioxarray.open_rasterio(tile_grid)
            for land in geotif_land_use:
                xds1 = rioxarray.open_rasterio(land)  # land use
                # we clip the raster of the land use
                clipped = xds1.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)  # clip the raster
                xds_repr_match = clipped.rio.reproject_match(to_match)
                data_reprojected = xds_repr_match.rio.reproject("EPSG:2039")
                data_reprojected.to_netcdf(f'{os.path.basename(tile)}-{tif_name}.nc')
                # # visualize data
                # plt.imshow(data_reprojected.squeeze())
                # plt.show()
                # plt.clf()


class LocalHandler(Handler):
    ...


class DownloadHandler(Handler):
    ...


class DistanceFromWaterHandler(LocalHandler, tifHandler):
    def __init__(self, path, start_date, end_date, overwrite):
        super().__init__(path, start_date, end_date, overwrite)
        self.name = "dist_from_water"
        self.source = "source"

    def confirm_existence(self):
        required_files = set(constants.REQUIRED_FILE)
        existing_files = set(os.listdir(self.path))
        return len(required_files & existing_files) == len(required_files)

    def preprocess(self):
        geotif_land_use = [f"{self.path}/dist_massive_water.tif"
            , f"{self.path}/dist_to_water.tif"]
        for tif in geotif_land_use:
            self.run_tif(self.name, tif, self.path)



def generate_classes(path, start_date, end_date, overwrite):
    for name in constants.HANDLERS:
        class_obj = globals().get(name)
        instance_obj = class_obj(path, start_date, end_date, overwrite)
        instance_obj.preprocess()


