import os.path
import geopandas
from rioxarray import rioxarray

from handlers.handler import Handler


def clip_and_reproject_one_file(src_path, dir_path, result_file_name):
    """
    clip and reproject the given file to the different tiles on Handler.CLIP_AND_REPROJECT_FILES
    :param src_path:            the path to the file to clip and reproject
    :param dir_path:            the path the save the results at
    :param result_file_name:    the name of the result file, the name of the tile and the .nc ending are added
                                automatically
    :return:                    None
    """

    for tile_clip, tile_grid, tile_name in Handler.CLIP_AND_REPROJECT_FILES:
        geodf = geopandas.read_file(tile_clip)
        to_match = rioxarray.open_rasterio(tile_grid)

        xds1 = rioxarray.open_rasterio(src_path)
        # ensure .nc files have attribute crs
        xds1 = xds1.rio.write_crs("EPSG:2039", inplace=True)
        clipped = xds1.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)  # clip the raster
        xds_repr_match = clipped.rio.reproject_match(to_match)
        data_reprojected = xds_repr_match.rio.reproject("EPSG:2039")
        data_reprojected.to_netcdf(
            os.path.join(dir_path, f"{result_file_name}_{tile_name}.nc".replace(" ", "_").lower())
        )
