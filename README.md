# ashes-and-dust-cli

## general
### dependencies
before using or working on this project you have to install some libraries
1. [rich](https://pypi.org/project/rich/) - pip install rich
2. [typer](https://pypi.org/project/typer/) - pip install typer
3. [geopandas]()
4. rioxarray
5. scipy

## project structures

### app configuration
some parts of the app require some configuration files, use the ```ConfigurationValues``` [implemented on utils/configuration_values.py](utils/configuration_values.py) to add more values, you may access the config file from the [constants file](utils/constants.py)
### data download and preprocess
each data type has its own data_handler(see data_handlers/handler.py) that implements the basic functions of the data.

the data was divided to 2 groups:
- Local Data: data that the program expects to find locally and cant download from an online source
- Remote Data: data that is available online and the program will download when needed

for each of those groups, there is a designated handler class - ```LocalHandler``` for Local Data and ```DownloadHandler``` for Remote Data. 

as many data types are similar to each other (especially Local Data), there are some subclasses of ```LocalHandler```
- ```TifHandler``` - [implemented on data_handlers/tif_handler.py](data_handlers/tif_handler.py) for preprocessing a tif file available locally
- ```Convert Handler``` - [implemented on data_handlers/convert_handler.py](data_handlers/convert_handler.py) - for data types that require some calculations and conversions

#### adding new data type
before adding a new data type to the project, there a several things to consider
1. the data_handler api its handler should implement - is it local or is it remote? 
2. is it similar to other data types or should I write the code myself?
3. after the handler is implemented add it to list of handlers on the [constants file](utils/constants.py)
make sure the look at the [utils](utils) that already exists, you save yourself some time using functions that are already implemented