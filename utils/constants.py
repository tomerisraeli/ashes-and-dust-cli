from data_handlers.download_handlers.modis_handler import ModisHandler
from data_handlers.download_handlers.pbl_handler import PBLHandler
from data_handlers.local_handlers.distance_to_water_handler import DistanceToWaterHandler
from data_handlers.local_handlers.elevation_handler import ElevationHandler
from data_handlers.local_handlers.land_use_handler import LandUseHandler
from data_handlers.local_handlers.population_density_handler import PopulationDensityHandler
from data_handlers.local_handlers.roads_handler import RoadsHandler

from utils.configuration_values import ConfigurationValues

# CLI constants

DATE_FORMATS = formats = ["%Y",
                          "%m/%Y", "%m-%Y", "%m.%Y",
                          "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"
                          ]


# lists of program handlers

LOCAL_HANDLERS = [
    # PopulationDensityHandler(),
    # DistanceToWaterHandler(),
    # ElevationHandler(),
    # LandUseHandler(),
    # RoadsHandler()
]
DOWNLOAD_HANDLERS = [
    # PBLHandler()
    ModisHandler()
]

# config values

CONFIG = ConfigurationValues("aad_config.ini")
