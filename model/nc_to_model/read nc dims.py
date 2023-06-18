# This file gets a variable dictionary, and prints it's dimensions and variables

import netCDF4 as nc
from constants import *

var = AODdict  # Put var dict here

ncfile = nc.Dataset(var['path'], 'r')
# Print the dimensions
print("Dimensions:")
for dimname, dimobj in ncfile.dimensions.items():
    print(dimname + ": " + str(len(dimobj)))

# Print the variables
print("\nVariables:")
for varname, varobj in ncfile.variables.items():
    print(varname + ": ")

    print("\tDimensions: " + ", ".join(varobj.dimensions))

    # Print the variable attributes
    for attrname in varobj.ncattrs():
        print("\t" + attrname + ": " + str(varobj.getncattr(attrname)))
