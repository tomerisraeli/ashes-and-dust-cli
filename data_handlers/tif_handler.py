import os.path
from typing import Tuple

from data_handlers.handler import LocalHandler
from utils import preprocess_utils


class TifHandler(LocalHandler):
    """
    a general tif handler implementation

    clip and reproject to input file (TIF_PATH) to each tile in the handler, also holds basic implementation to all
    Handler functions
    """

    TIF_PATH: str  # the path from the root dir to tif file

    def confirm_existence(self, path: str):
        file_path, _ = self.__get_paths(path)
        return [] if os.path.isfile(file_path) else [file_path]

    def preprocess(self, path):
        tif_path, sub_dir = self.__get_paths(path)

        preprocess_utils.clip_and_reproject_one_file(
            src_path=tif_path,
            dir_path=sub_dir,
            result_file_name=self.NAME
        )

    def __get_paths(self, path: str) -> Tuple[str, str]:
        """
        get the full path for the tif file and the directory of the data
        :param path: the path of the root directory
        :return: tuple of (tif path, data's dir path)
        """
        tif_path = os.path.join(path, self.TIF_PATH)
        sub_dir_path = os.path.dirname(tif_path)
        return tif_path, sub_dir_path

    def get_required_files_list(self, root_dir):
        return [os.path.join(root_dir, self.TIF_PATH)]
