import os.path
from typing import Tuple

import geopandas
from rioxarray import rioxarray

from handlers.handler import LocalHandler


class TifHandler(LocalHandler):
    """
    a general tif handler implementation
    """

    TIF_PATH: str       # the path from the root dir to tif file

    def confirm_existence(self, path: str):
        file_path, _ = self.__get_paths(path)
        return [] if os.path.isfile(file_path) else [file_path]

    def preprocess(self, path):
        file_path, sub_dir_path = self.__get_paths(path)

        for tile_clip, tile_grid, tile_name in TifHandler.CLIP_AND_REPROJECT_FILES:
            geodf = geopandas.read_file(tile_clip)
            to_match = rioxarray.open_rasterio(tile_grid)

            xds1 = rioxarray.open_rasterio(file_path)
            # ensure .nc files have attribute crs
            xds1 = xds1.rio.write_crs("EPSG:2039", inplace=True)
            # we clip the raster to the tile
            clipped = xds1.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)  # clip the raster
            xds_repr_match = clipped.rio.reproject_match(to_match)
            data_reprojected = xds_repr_match.rio.reproject("EPSG:2039")
            data_reprojected.to_netcdf(os.path.join(sub_dir_path, f"processed/{tile_name}_{os.path.basename(path)}"))

            # visualize data
            # plt.imshow(data_reprojected.squeeze())
            # plt.show()
            # plt.clf()

    def __get_paths(self, path: str) -> Tuple[str, str]:
        """
        get the full path for the tif file and the directory of the data


        :param path: the path of the root directory
        :return: tuple of (tif path, data's dir path)
        """
        sub_dir_path = os.path.dirname(path)
        return path, sub_dir_path
