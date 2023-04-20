from rich.console import Console


class AshesAndDust(Console):

    def __init__(self):
        super().__init__()

        # list of all the spatial data handlers
        self.spatial_data_handlers = []
        # list of all the timed data handlers
        self.timed_data_handlers = []

    def start_cli(self):
        """
        start the cli of the project
        :return: None
        """

        self.print("Welcome to Ashes And Dust!", style="bold")

    def print_data_handlers(self):
        pass


if __name__ == '__main__':
    app = AshesAndDust()
    app.start_cli()
