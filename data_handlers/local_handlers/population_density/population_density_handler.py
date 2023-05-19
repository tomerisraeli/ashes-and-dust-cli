import os

import geopandas
import rich
from rioxarray import rioxarray

from data_handlers.handler import LocalHandler
from data_handlers.local_handlers.population_density import population_density_handler_support
from data_handlers.tif_handler import TifHandler
from utils import constants


class PopulationDensityHandler(LocalHandler):
    SOURCE: str = "local"
    NAME: str = "Population Density 2011"
    DESCRIPTION: str = "the population density over israel in 2011, units=1000[peoples]"

    NECESSARY_FILES = [
        "LAMS2011_2039.shp",
        "LAMS2011_2039.cpg",
        "LAMS2011_2039.dbf",
        "LAMS2011_2039.prj",
        "LAMS2011_2039.qmd",
        "LAMS2011_2039.shx"
    ]

    def confirm_existence(self, path: str):
        missing_files = []
        for file in PopulationDensityHandler.NECESSARY_FILES:
            file_path = os.path.join(self.__get_population_density_dir(path), file)
            if not os.path.isfile(file_path):
                missing_files.append(file_path)
        return missing_files

    def preprocess(self, path):
        polygon_file = os.path.join(self.__get_population_density_dir(path),
                                    PopulationDensityHandler.NECESSARY_FILES[0]
                                    )
        rich.print("converting population density to .tif")
        for _, tile_grid, tile_name in PopulationDensityHandler.CLIP_AND_REPROJECT_FILES:
            population_density_handler_support.polygons_to_raster(
                raster_path=tile_grid,
                polygon_path=polygon_file,
                field=constants.CONFIG.get_key(constants.CONFIG.Keys.population_density_value_key),
                output_raster=os.path.join(self.__get_population_density_dir(path), f"{self.NAME}_{tile_name}.tif")
            )
        # converting to nc and clipping data
        for tile_clip, _, tile_name in PopulationDensityHandler.CLIP_AND_REPROJECT_FILES:
            tif_path = os.path.join(self.__get_population_density_dir(path), f"{self.NAME}_{tile_name}.tif")
            geodf = geopandas.read_file(tile_clip)

            output = rioxarray.open_rasterio(tif_path)
            output = output.rio.clip(geodf.geometry.values, geodf.crs, drop=False, invert=False)
            output = output.rio.reproject("EPSG:2039")
            output.to_netcdf(os.path.join(self.__get_population_density_dir(path),
                                          f"{self.NAME.replace(' ', '_').lower()}_{tile_name}.nc"))

    def __get_population_density_dir(self, path: str):
        return os.path.join(path, "population_density")
