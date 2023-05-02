from handlers.local_handlers.distance_to_water_handler import DistanceToWaterHandler
from handlers.local_handlers.elevation_handler import ElevationHandler
from handlers.local_handlers.population_density.population_density_handler import PopulationDensityHandler
from utils.configuration_values import ConfigurationValues

DATE_FORMATS = formats = ["%Y",
                          "%m/%Y", "%m-%Y", "%m.%Y",
                          "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"
                          ]

LOCAL_HANDLERS = [PopulationDensityHandler(), DistanceToWaterHandler(), ElevationHandler()]
DOWNLOAD_HANDLERS = []
CONFIG = ConfigurationValues("add_config.config")
