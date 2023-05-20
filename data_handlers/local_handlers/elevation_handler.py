from data_handlers.tif_handler import TifHandler
import os


class ElevationHandler(TifHandler):
    NAME = "elevation"
    SOURCE = "local"
    DESCRIPTION = "height above sea level in meters"
    TIF_PATH = os.path.join("elevation", "elevation.tif")


if __name__ == '__main__':
    os.chdir("/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli")

    ElevationHandler().preprocess(
        "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/data_preprocess")