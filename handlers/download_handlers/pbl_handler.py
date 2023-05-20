import os.path
from datetime import datetime, timedelta

import cdsapi
import shutil

from rich.progress import track

from utils import preprocess_utils
import rich
from tqdm import tqdm
import xarray as xr
from handlers.handler import DownloadHandler
from utils import constants


class PBLHandler(DownloadHandler):
    SOURCE = "https://cds.climate.copernicus.eu/api/v2"
    NAME = "PBL DATA"
    DESCRIPTION = "the PBL data from cds"

    __API_URL = "https://cds.climate.copernicus.eu/api/v2"
    __HOUR = "12:00"  # the hour to download data to
    __AREA = [34, 33, 29, 36]  # the bbox of the download [North, West, South, East]
    __RAW_DATA_CRS = "WGS84"

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

        for file, date in tqdm(dates):
            try:
                self.__download_single_date(cdsapi_client, file, date)
            except Exception as e:
                rich.print(f"       [red]failed downloading {file}")

    def preprocess(self, path):

        # the preprocessing of data is made in 2 steps:
        # 1. clip and reproject all the data files
        #    after this step, we will have all the processed files in one folder - processed_data_dir_path
        # 2. merging all files to one .nc file

        pbl_dir = self.__get_pbl_dir(path)  # path to dir of pbl
        processed_data_dir_path = os.path.join(pbl_dir, 'processed')  # path to dir of processed files
        raw_data_path = self.__generate_data_path(path)  # path to dir of pbl raw data

        if not os.path.isdir(processed_data_dir_path):
            os.mkdir(processed_data_dir_path)

        # list of pbl raw data files
        data_files = [file for file in os.listdir(raw_data_path) if file.endswith(".nc")]

        # step 1 - run over the files and process them, after clipping and re-projecting to tiles, add the generated
        # files to the matching value on the preprocessed_files_by_tile_name
        preprocessed_files_by_tile_name = {tile_name: [] for _, _, tile_name in self.CLIP_AND_REPROJECT_FILES}

        for file in track(data_files, description="preprocessing pbl raw data file"):
            generated_files = preprocess_utils.clip_and_reproject_one_file(
                src_path=os.path.join(raw_data_path, file),
                dir_path=processed_data_dir_path,
                result_file_name=file.split(".")[0],
                src_crs=PBLHandler.__RAW_DATA_CRS
            )

            for tile_name, file_path in generated_files:
                preprocessed_files_by_tile_name[tile_name].append(file_path)

        # step 2 - merge files to one netcdf
        rich.print("merging data to .nc file, this may take some time")
        for tile_name, tile_files in preprocessed_files_by_tile_name.items():
            modified_datasets = []
            for file in tile_files:
                data = xr.open_dataset(file)
                data['time'] = [self.__get_file_date(file)]
                modified_datasets.append(data)

            merged_data = xr.concat(modified_datasets, dim='time')
            merged_data.to_netcdf(os.path.join(pbl_dir, f"pbl_{tile_name}.nc"))
        rich.print("merged data, deleting temp files")
        # delete unnecessary folder
        shutil.rmtree(processed_data_dir_path)

    def __get_dates(self, sdate: datetime, edate: datetime):
        """
        get a list of dates to download and the files names
        :param sdate: the first date to download data to
        :param edate: the last date to download data to (not included)
        :return: an iterator of file_names and the dates as datetime object
        """

        dates = [sdate + timedelta(days=x) for x in range((edate - sdate).days)]
        file_names = [f"{date.day}_{date.month}_{date.year}_{PBLHandler.__HOUR.replace(':', '_')}_pbl.nc" for date in
                      dates]
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
        dir_path = os.path.join(self.__get_pbl_dir(path), "data")
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        return dir_path

    def __get_pbl_dir(self, path):
        return os.path.join(path, "pbl")

    def __get_file_date(self, file_path) -> datetime:
        file_name = os.path.basename(file_path)
        # file name should be something like this - 1_1_2010_12_00_pbl_h20v05.nc
        # hence the last 14 characters are not date data
        date_str = file_name[:-14]

        return datetime.strptime(date_str, '%d_%m_%Y_%H_%M')


if __name__ == '__main__':
    os.chdir("/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli")
    PBLHandler().preprocess(
        "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/data_preprocess")
