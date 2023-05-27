class Handler:
    """
    the general handler api of the program. provides the basic structure of a data-handler on the app.
    """

    SOURCE: str = ...  # the source of the data handled by the Handler
    NAME: str = ...  # a short name for data handled by the Handler
    DESCRIPTION: str = ""  # a short description of the data

    CLIP_AND_REPROJECT_FILES = [
        # (clip file - shp, reproject file - tif, tile name)
        ("data_handlers/tiles/h21v06_crs2039.shp", "data_handlers/tiles/h21v06.tif", "h21v06"),
        ("data_handlers/tiles/h21v05_crs2039.shp", "data_handlers/tiles/h21v05.tif", "h21v05"),
        ("data_handlers/tiles/h20v05_crs2039.shp", "data_handlers/tiles/h20v05.tif", "h20v05")
    ]

    def preprocess(self, path):
        """
        preprocess the raw data: clip, reproject and save as a new netcdf file for each tile
        :param path:    the path to the root dir holding all data of the project
        :return:        None
        """
        ...

    def get_required_files_list(self, root_dir):
        """
        get a list of all the required files for the handler functions
        :param root_dir:    the path to root dir, might not be a valid path
        :return:            a list of paths as str
        """
        ...

