from datetime import datetime, timedelta

import os
import cdsapi
from tqdm import tqdm

##parameters
dir_to_download = '/Users/tomerisraeli/Documents/GitHub/ashes-and-dust-cli/handlers/download_handlers'
uid = "196384"
apikey = "fce99bdf-7a3d-4532-8386-191f924b7fa0"

# Subregion extraction
North = 34
South = 29
East = 36
West = 33


HOUR = "12:00"


def __get_dates(sdate: datetime, edate: datetime):
    """
    get a list of dates to download and the files names
    :param sdate: the first date to download data to
    :param edate: the last date to download data to (not included)
    :return: an iterator of file_names and the dates as datetime object
    """

    dates = [sdate + timedelta(days=x) for x in range((edate - sdate).days)]
    file_names = [f"{date.day}_{date.month}_{date.year}_{HOUR.replace(':', '_')}_pbl" for date in dates]
    return list(zip(file_names, dates))


def __filter_dates(dates):
    """

    :param dates:
    :return:
    """
    return dates


def __download_single_date(cdsapi_client, file_name, date):
    """
    download a single day from the api
    :param file_name: the file to download to
    :param date: the date of the data
    :return:
    """

    cdsapi_client.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': 'boundary_layer_height',
            'year': [f"{date.year}"],
            'month': [f"{date.month}"],
            'day': [f"{date.day}"],
            'time': [HOUR],
            'area': [North, West, South, East],
            'format': 'netcdf',
        },
        f"{file_name}.nc"
    )


def download(sdate, edate, overwrite):
    """

    :param sdate:
    :param edate:
    :param overwrite:
    :return:
    """


    os.chdir(dir_to_download)

    dates = __get_dates(sdate, edate)
    if overwrite:
        dates = __filter_dates(dates)

    if not dates:
        print("nothing to download")
        return

    print(f"downloading {len(dates)} files")
    cdsapi_client = cdsapi.Client(key=f"{uid}:{apikey}", url="https://cds.climate.copernicus.eu/api/v2")
    for file, date in tqdm(dates):
        try:
            __download_single_date(cdsapi_client, file, date)
        except Exception as e:
            print(f"file downloading {file}")

if __name__ == '__main__':
    sdate = datetime(day=12, month=5, year=2020)
    edate = datetime(day=15, month=5, year=2020)
    overwrite = True
    download(sdate, edate, overwrite)