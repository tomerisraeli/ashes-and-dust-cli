class Handler:
    def __init__(self, path: str, start_date, end_date, overwrite: bool):
        self.path = path
        self.start_date = start_date
        self.end_date = end_date
        self.overwrite = overwrite

class LocalHandler(Handler):
    ...


class DownloadHandler(Handler):
    ...
