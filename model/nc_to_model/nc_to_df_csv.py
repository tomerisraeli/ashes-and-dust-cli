import netCDF4 as nc
import numpy.ma
import pandas as pd
from constants import *
from tqdm import tqdm
import xarray as xr
import os

# Converting TMPORAL netcdf file to pandas dataframe and saves it as a csv

if not os.path.isdir('csv' + str(int(WINDOW_SIZE / 60)) + 'hours'):
    os.mkdir('csv' + str(int(WINDOW_SIZE / 60)) + 'hours')

for var in TEMPORAL_VARS_ARRAY:
    # Open the netCDF file and get the variables from the netCDF file
    netcdf_file = nc.Dataset(var['path'])
    x = netcdf_file.variables['x'][:]
    y = netcdf_file.variables['y'][:]
    time = netcdf_file.variables['time'][:]
    data = netcdf_file.variables[var['var']][:]

    # Create time windows for averaging
    time_window = []
    zero_flag = True
    for w in range(0, time[-1], WINDOW_SIZE):
        flag_start = False
        start = 0
        for i in range(len(time)):
            if time[i] < w:
                continue
            elif (time[i] >= w + WINDOW_SIZE) and (start != 0 or zero_flag):
                time_window.append([start, i])
                start = i
                zero_flag = False
                break
            elif (time[i] >= w + WINDOW_SIZE) and (start == 0):
                continue
            elif not flag_start:
                start = i
                flag_start = True

    cells = []
    # Iterate over the indices of the variables with tqdm
    for i in tqdm(range(len(x)), desc='Processing'):
        for j in range(len(y)):
            for w in time_window:
                count = 0
                pm10_value = 0
                x_value = x[i]
                y_value = y[j]
                time_value = (time[w[0]] // WINDOW_SIZE) * WINDOW_SIZE
                for k in range(w[0], w[1]):
                    # Get the values of x, y, time, and pm10 at the current indices
                    curr = data[k, j, i]
                    if numpy.ma.is_masked(curr):
                        continue
                    pm10_value += curr

                    count += 1
                # Append the cell as a dictionary to the list
                if count == 0:
                    continue
                cell = {'x': x_value, 'y': y_value, 'time': time_value, var['name']: pm10_value / count}  # averaging over
                # all measurments in the current time window

                cells.append(cell)

    # Create a pandas DataFrame from the list of cells
    df = pd.DataFrame(cells)

    if var['name'] == 'AOD':
        num_chunks = len(df) // CHUNK_SIZE + 1
        os.mkdir('AOD' + str(int(WINDOW_SIZE / 60)) + 'hours')
        for i in range(15):
            start = i * CHUNK_SIZE
            end = (i + 1) * CHUNK_SIZE
            chunk_df = df.iloc[start:end]
            chunk_df.to_csv(f'csv' + str(int(WINDOW_SIZE / 60)) + '\\AOD' + str(int(WINDOW_SIZE / 60)) + 'hours\\AOD' + str(WINDOW_SIZE / 60) + f'hours{i}.csv', index=False)
    else:
        df.to_csv(f'csv' + str(int(WINDOW_SIZE / 60)) + 'hours\\' + var['name'] + str(int(WINDOW_SIZE / 60)) + 'hours.csv', index=False)

    netcdf_file.close()

os.mkdir('csv_spatial')

for var in SPATIAL_VARS_ARRAY:
    ds = xr.open_dataset(var['path'])
    df1d = ds.to_dataframe()

    df1d = df1d.reset_index()
    df1d.drop(['band', 'spatial_ref'], axis=1, inplace=True)  # Remove not needed columns
    df1d.rename(columns={var['var']: var['name']}, inplace=True)
    df1d = df1d.dropna(subset=var['name'])  # Remove empty rows
    df1d.to_csv(f'csv_spatial\\' + var['name'] + 'df.csv', index=True)

    ds.close()
