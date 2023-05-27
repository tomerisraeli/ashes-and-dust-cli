from data_handlers.handlers_api.handler import Handler


class LocalHandler(Handler):
    """
    handler for data which isn't available online and should be available locally.
    instead of downloading the data, it will confirm the existence of it at the given path
    """

    def confirm_existence(self, path: str) -> [str]:
        """
        confirm that all the needed files for this handler exits, with the right names and paths
        :param path:    the path to the root dir holding all data of the project
        :return:        an array of missing files
        """
        ...
