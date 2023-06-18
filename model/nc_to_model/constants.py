# Important names for the project, so we won't need to change a lot of names while working on the project

# PATHS FOR THE NETCDF FILES:
# Temporal and spatial
PM10path_nc = 'nc\\h20v05pm10_1_YEAR.nc'
AODpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\h20v05_AOT_one_year.nc'
RHpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\h20v05RelativeHumidity_YEAR.nc'
PBLpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\h20v05pm25_YEAR_2010pbl.nc'
WSpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\h20v05WindSpeed_YEAR.nc'

# Spatial only
ELpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\elevation_h20v05.nc'
HDpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\distance_form_highways_h20v05.nc'
WBDpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\distance_to_water_h20v05.nc'
LUpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\land_use_classification_h20v05.nc'
PDpath_nc = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\nc\\Population Density 2011_h20v05 (1).nc'

# Dictionaries for use in the files - much of the process is common for more than one data type
PMdict = {'path': PM10path_nc, 'var': 'pm10', 'name': 'PM'}
AODdict = {'path': AODpath_nc, 'var': 'AOT', 'name': 'AOD'}
RHdict = {'path': RHpath_nc, 'var': 'RH', 'name': 'RH'}
WSdict = {'path': WSpath_nc, 'var': 'Ws', 'name': 'WS'}
PBLdict = {'path': PBLpath_nc, 'var': 'blh', 'name': 'PBL'}

TEMPORAL_VARS_ARRAY = [PMdict, AODdict, RHdict, WSdict]  # All temporal dictionaries which are not PM or AOD (AOD is too big and needs a different approach

ELdict = {'path': ELpath_nc, 'var': '__xarray_dataarray_variable__', 'name': 'EL'}  # Elevation
HDdict = {'path': HDpath_nc, 'var': '__xarray_dataarray_variable__', 'name': 'HD'}
WBDdict = {'path': WBDpath_nc, 'var': '__xarray_dataarray_variable__', 'name': 'WBD'}
LUdict = {'path': LUpath_nc, 'var': '__xarray_dataarray_variable__', 'name': 'LU'}
PDdict = {'path': PDpath_nc, 'var': '__xarray_dataarray_variable__', 'name': 'PD'}
SPATIAL_VARS_ARRAY = [ELdict, HDdict, WBDdict, LUdict, PDdict]

WINDOW_SIZE = 720  # Window size for averaging over time in minutes
CHUNK_SIZE = 1000000  # number of lines in each AOD csv file

DATApath = 'C:\\Users\\DellTest\\PycharmProjects\\testing\\csv' + str(int(WINDOW_SIZE / 60)) + 'hours\\merged' + str(int(WINDOW_SIZE / 60)) + 'hours.csv'
