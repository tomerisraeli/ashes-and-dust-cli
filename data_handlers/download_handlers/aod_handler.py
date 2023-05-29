from data_handlers.download_handlers.modis_handler import ModisHandler


class AODHandler(ModisHandler):
    NAME = "AOD"
    DESCRIPTION = ""  # TODO: insert a short description about the data

    _MODIS_DATA_NAME = "aod.504"  # change this

    # all the implementation should be on the ModisHandler, we dont expect to have any functions over here,
    # only constants
