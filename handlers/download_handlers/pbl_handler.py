import logging
import os.path
from datetime import datetime, timedelta

import cdsapi
import rich
from tqdm import tqdm

from handlers.handler import DownloadHandler
from utils import constants


class PBLHandler(DownloadHandler):
    SOURCE = "https://cds.climate.copernicus.eu/api/v2"
    NAME = "PBL DATA"
    DESCRIPTION = "the PBL data from cds"

    __API_URL = "https://cds.climate.copernicus.eu/api/v2"
    __HOUR = "12:00"  # the hour to download data to
    __AREA = [34, 33, 29, 36]  # the bbox of the download [North, West, South, East]

    def download(self, path: str, start_date: datetime, end_date: datetime, overwrite: bool):
        """

        :param path:
        :param start_date:
        :param end_date:
        :param overwrite:
        :return:
        """
        pwd = self.__generate_data_path(path)
        os.chdir(pwd)

        dates = self.__get_dates(start_date, end_date)
        dates = self.__filter_dates(dates, overwrite)

        if not dates:
            rich.print("        [green]nothing to download")
            return

        rich.print(f"       downloading {len(dates)} files")
        cdsapi_client = cdsapi.Client(
            key=constants.CONFIG.get_key(constants.CONFIG.Keys.pbl_api_key),
            url=PBLHandler.__API_URL
        )
        cdsapi_client.logger.setLevel(level=logging.CRITICAL)

        for file, date in tqdm(dates):
            try:
                self.__download_single_date(cdsapi_client, file, date)
            except Exception as e:
                rich.print(f"       [red]failed downloading {file}")

    def preprocess(self, path):
        pass

    def __get_dates(self, sdate: datetime, edate: datetime):
        """
        get a list of dates to download and the files names


        :param sdate: the first date to download data to
        :param edate: the last date to download data to (not included)
        :return: an iterator of file_names and the dates as datetime object
        """

        dates = [sdate + timedelta(days=x) for x in range((edate - sdate).days)]
        file_names = [f"{date.day}_{date.month}_{date.year}_{PBLHandler.__HOUR.replace(':', '_')}_pbl.nc" for date in dates]
        return list(zip(file_names, dates))

    def __filter_dates(self, dates, overwrite):
        """
        remove all files that already exits in the directory
        :param dates:
        :return:
        """
        if overwrite:
            return dates
        return [(file_path, date) for file_path, date in dates if not os.path.isfile(file_path)]

    def __download_single_date(self, cdsapi_client, file_name, date):
        """
        download a single day from the api
        :param file_name: the file to download to
        :param date: the date of the data
        :return:
        """
        _ = cdsapi_client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': 'boundary_layer_height',
                'year': f"{date.year}",
                'month': f"{date.month}",
                'day': f"{date.day}",
                'time': PBLHandler.__HOUR,
                'area': PBLHandler.__AREA,
                'format': 'netcdf',
            },
            file_name
        )

    def __generate_data_path(self, path):
        dir_path =  os.path.join(path, "pbl", "data")
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path
