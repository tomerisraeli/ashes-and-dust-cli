import pandas as pd
from constants import *

# This file merges the csv's of the different spatial and temporal data to one df which can be fed to the model.
# Keep in mind that first the netcdf's should be converted to csv using nc_to_df_csv.py

pmdf = pd.read_csv('PM' + str(int(WINDOW_SIZE / 60)) + 'hours.csv')
pmdf = pmdf.round()

base_df = pd.DataFrame()  # We will save this at the end

# Because the AOD spans across multiple files we need to merge it first with the PM
for i in range(15):
    chunk_df = pd.read_csv(f'AOD' + str(int(WINDOW_SIZE / 60)) + 'hours\AOD' + str(int(WINDOW_SIZE / 60)) + f'hours{i}.csv')
    chunk_df = chunk_df.round()
    df_merged = pd.merge(pmdf, chunk_df, on=['x', 'y', 'time'], how='inner')  # Inner because we want to save only the intersections
    base_df = pd.concat([base_df, df_merged], ignore_index=True)

for var in TEMPORAL_VARS_ARRAY.remove(AODdict).remove(PMdict):
    df = pd.read_csv(var['name'] + str(int(WINDOW_SIZE / 60)) + 'hours.csv')
    df = df.round()  # Rounding the numbers is important because there might be slight differentiations between the
    # files which makes the mergeing a real pain in the ass.
    base_df = pd.merge(base_df, df)

for var in SPATIAL_VARS_ARRAY:
    df = pd.read_csv(f'csv_spatial\\' + var['name'] + 'df.csv')
    df = df.round()
    df = df.dropna(subset=var['name'])
    base_df = pd.merge(base_df, df, on=['x', 'y'])
    if 'Unnamed: 0' in df.columns:
        base_df.drop(['Unnamed: 0'], axis=1, inplace=True)


base_df.to_csv(f'csv' + str(int(WINDOW_SIZE / 60)) + 'hours\\merged' + str(int(WINDOW_SIZE / 60)) + 'hours.csv', index=True)
