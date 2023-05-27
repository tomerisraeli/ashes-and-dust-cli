import os.path
import geopandas
from rioxarray import rioxarray

from data_handlers.handlers_api.handler import Handler


def clip_and_reproject_one_file(src_path, dir_path, result_file_name, src_crs: str = None):
    """
    clip and reproject the given file to the different tiles on Handler.CLIP_AND_REPROJECT_FILES
    :param src_path:            the path to the file to clip and reproject
    :param dir_path:            the path the save the results at
    :param result_file_name:    the name of the result file, the name of the tile and the .nc ending are added
                                automatically
    :param src_crs:             (optional) if given the crs of the file at src_path will be treated as the given crs
    :returns:                   None
    """

    results_paths = []
    for tile_clip, tile_grid, tile_name in Handler.CLIP_AND_REPROJECT_FILES:
        geodf = geopandas.read_file(tile_clip)
        to_match = rioxarray.open_rasterio(tile_grid)
        data = rioxarray.open_rasterio(src_path)
        if src_crs:
            data = data.rio.write_crs(src_crs, inplace=True)
        # ensure .nc files have attribute crs
        data = data.rio.reproject("EPSG:2039")
        data = data.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)  # clip the raster
        data = data.rio.reproject_match(to_match)
        # data_reprojected = xds_repr_match.rio.reproject("EPSG:2039")

        path_of_result = os.path.join(dir_path, f"{result_file_name}_{tile_name}.nc".replace(" ", "_").lower())
        results_paths.append((tile_name, path_of_result))
        data.to_netcdf(path_of_result)

    return results_paths
