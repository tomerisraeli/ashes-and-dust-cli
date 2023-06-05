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
        clip = geopandas.read_file(tile_clip)
        grid = rioxarray.open_rasterio(tile_grid)
        path_of_result = os.path.join(dir_path, f"{result_file_name}_{tile_name}.nc".replace(" ", "_").lower())
        results_paths.append((tile_name, path_of_result))

        clip_and_reproject(src_path, grid, clip, path_of_result, src_crs)

    return results_paths


def clip_and_reproject(input_tif_path, grid, clip, output_tif_path, src_crs=None):
    """
    clip and reproject a single file
    :param input_tif_path:  the path of file to operate
    :param grid:            the grid to reproject to, rioxarray.open_rasterio()
    :param clip:            the shp file to clip to, use geopandas.read_file()
    :param output_tif_path: the path to save the result at
    :param src_crs:         (optional) if given the crs of the file at src_path will be treated as the given crs
    :returns:               None
    """

    print(f"grid: {type(grid)}")
    print(f"clip: {type(clip)}")

    data = rioxarray.open_rasterio(input_tif_path)
    print(data)
    if src_crs:
        print("updateing crs")
        data = data.rio.write_crs(src_crs, inplace=True)
    # ensure .nc files have attribute crs
    data = data.rio.reproject("EPSG:2039")

    data = data.rio.clip(clip.geometry.values, clip.crs, drop=False, invert=False)  # clip the raster
    data = data.rio.reproject_match(grid)
    data.to_netcdf(output_tif_path)
