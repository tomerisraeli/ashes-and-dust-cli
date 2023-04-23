import geopandas
from rioxarray import rioxarray

from handlers.handler import Handler
from utils import constants


class TifHandler(Handler):
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
