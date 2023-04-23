from utils import constants
from handlers.tif_handler import TifHandler
import os


class DistanceToWaterHandler(TifHandler):
    NAME = "distance_to_water"
    SOURCE = "local"
    TIF_PATH = os.path.join("distance_to_water", "distance_to_water.tif")


if __name__ == '__main__':
    root_path = "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/data_preprocess"
    handler = DistanceToWaterHandler()
    print(handler.confirm_existence(root_path))
    handler.preprocess(root_path)
