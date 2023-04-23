from utils import constants

import os
import sys

from handlers.handler import LocalHandler
from handlers.tif_handler import TifHandler

sys.path.append(os.path.dirname(os.getcwd()))


class DistanceFromWaterHandler(LocalHandler, TifHandler):
    def __init__(self, path, start_date, end_date, overwrite):
        super().__init__(path, start_date, end_date, overwrite)
        self.name = "dist_from_water"
        self.source = "source"

    def confirm_existence(self):
        required_files = set(constants.REQUIRED_FILE)
        existing_files = set(os.listdir(self.path))
        return len(required_files & existing_files) == len(required_files)

    def preprocess(self):
        geotif_land_use = [f"{self.path}/dist_massive_water.tif"
            , f"{self.path}/dist_to_water.tif"]
        for tif in geotif_land_use:
            self.run_tif(self.name, tif, self.path)


def generate_classes(path, start_date, end_date, overwrite):
    for name in constants.HANDLERS:
        class_obj = globals().get(name)
        instance_obj = class_obj(path, start_date, end_date, overwrite)
        instance_obj.preprocess()
