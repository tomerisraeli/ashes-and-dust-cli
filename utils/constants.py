from data_handlers.local_handlers.population_density_handler import PopulationDensityHandler

from utils.configuration_values import ConfigurationValues

DATE_FORMATS = formats = ["%Y",
                          "%m/%Y", "%m-%Y", "%m.%Y",
                          "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"
                          ]

LOCAL_HANDLERS = [
    PopulationDensityHandler(),
    # DistanceToWaterHandler(),
    # ElevationHandler(),
    # LandUseHandler(),
    # RoadsHandler()
]
DOWNLOAD_HANDLERS = [
    # PBLHandler()
]
CONFIG = ConfigurationValues("aad_config.ini")
