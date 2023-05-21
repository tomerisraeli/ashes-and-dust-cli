# ashes-and-dust-cli

## general
### dependencies and versions
the project was developed using python 3.9.6 and requires the libraries specified at 
[requirements.txt](requirements.txt)
```bash
pip install -r requirements.txt
``` 
to install them all

### project CLI
after installing all the requirements, you can run 
```bash
python aad.py --help
```
to see all CLI commands. to see further information on each cmd you can use
```bash
python aad.py download --help
```
for example
#### CLI input
when running different CLI functions you might be asked to enter a path to the root directory of the data. 
what is this directory?

root directory - the path to the directory holding all project data, when running the download function of CLI, 
the existence of local data will be checked, and the missing files will be presented to the user, make sure all files 
exists before running other functions. 

## project structure
the main file of the project is [aad.py](aad.py) (aad - ashes and dust), running this file will start the CLI. 
other than the main file, the basic implementations of ashes and dust functions are on the 
[ashes_and_dust dir](ashes_and_dust) and they are imported to the main file

### data download and preprocess
#### the general idea
before running any data analysis, we have to do 2 things
1. making sure the data is available locally
2. preprocess the data - preprocessing of data is split to 2 parts
   - make sure all the data is saved on the same format(netcdf, nc for short) 
   - make sure the data describes the same locations. read more at [tiles](#tiles) under [project support](#project-support)

#### Implementation
each data type has its own data_handler(see data_handlers/handler.py) that implements the basic functions of the data type, those discussed on the last section

the data was divided to 2 groups:
- Local Data: data that the program expects to find locally and cant download from an online source
- Remote Data: data that is available online and the program will download when needed

for each of those groups, there is a designated handler class - ```LocalHandler``` for Local Data and ```DownloadHandler``` for Remote Data. 

as many data types are similar to each other (especially Local Data), there are some subclasses of ```LocalHandler```
- ```TifHandler``` - [implemented on data_handlers/tif_handler.py](data_handlers/tif_handler.py) for preprocessing a tif file available locally
- ```Convert Handler``` - [implemented on data_handlers/convert_handler.py](data_handlers/convert_handler.py) - for data types that require some calculations and conversions

#### adding a new data type
before adding a new data type to the project, there a several things to consider
1. the data_handler api its handler should implement - is it local or is it remote? 
2. is it similar to other data types or should I write the code myself?
3. after the handler is implemented add it to list of handlers on the [constants file](utils/constants.py)
make sure the look at the [utils](utils) that already exists, you may save yourself some time using functions that are already implemented

## project support
### app configuration
some parts of the app require some configuration files, use the ```ConfigurationValues``` [implemented on utils/configuration_values.py](utils/configuration_values.py) to add more values, you may access the config file from the [constants file](utils/constants.py)

### tiles
the area of Israel intersects 3 different [modis tiles](https://modis-land.gsfc.nasa.gov/MODLAND_grid.html). 
to make our life easier, we decided to save the data at 3 different nc files - a file for each tile.

we also made sure that the data saved on each file describes the same locations - the program projects the data to the tle grid

#### tiles resources
all tile resources are available at [data_handlers/tiles](data_handlers/tiles) 
- shp file that holds the tile intersection with Israel, use those to clip the data
- tif file that describes the tile grid