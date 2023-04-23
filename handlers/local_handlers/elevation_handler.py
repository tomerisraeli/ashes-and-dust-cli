from handlers.tif_handler import TifHandler
import os


class ElevationHandler(TifHandler):
    NAME = "elevation"
    SOURCE = "local"
    DESCRIPTION = "height above sea level in meters"
    TIF_PATH = os.path.join("elevation", "elevation.tif")
