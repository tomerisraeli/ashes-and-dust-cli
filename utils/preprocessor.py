import os.path
from typing import Tuple

import geopandas
from rioxarray import rioxarray

from handlers.handler import Handler

def preprocess(path):
    file_path = path
    sub_dir_path = os.path.dirname(path)

    for tile_clip, tile_grid, tile_name in Handler.CLIP_AND_REPROJECT_FILES:
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