import numpy as np
import rasterio
from rasterio.plot import show
from matplotlib import pyplot
from PIL import Image

class Data:

    def __init__(self, name, path_of_nc):
        self.name = name
        self.path = path_of_nc


if __name__ == '__main__':

    all_data = [
        Data("Distance From Water",
             "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/distance_to_water/distance_to_water_world.nc"),
        Data("Elevation",
             "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/elevation/elevation_world.nc"),
        Data("Land Use",
             "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/land_use/land_use_world.nc"),
        Data("Population Density",
             "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/population_density/population_density_world.nc"),
        # Data("Map",
        #      "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/israel_map.tif")

    ]

    fig, axes = pyplot.subplots(1, len(all_data))

    # clean axes
    for ax in axes:
        ax.xaxis.set_tick_params(labelbottom=False)
        ax.yaxis.set_tick_params(labelleft=False)
        ax.set_xticks([])
        ax.set_yticks([])

        # share zoom
        ax.sharex(axes[0])
        ax.sharey(axes[0])

    # img = imageio.imread(
    #     "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/israel_map.png"
    # )
    # img = Image.open(
    #     "/Users/tomerisraeli/Library/CloudStorage/GoogleDrive-tomer.israeli.43@gmail.com/My Drive/year_2/Magdad/preprocessed_data/showdown_data/israel_map.png"
    # ).convert("L")
    #
    # show(img, ax=axes[-1], title="tomer")

    for index, data in enumerate(all_data):
        with rasterio.open(data.path, "r") as ras:

            if index == 3:

                kwargs = {"vmin":0, "vmax": 1}

            kwargs = {}#{"cmap": "Greys"}
            # if index == 3:
            #     kwargs = {"vmin": 0, "vmax": 80, "cmap": 'Greys_r'}
            show(ras, ax=axes[index], title=data.name, **kwargs)




    pyplot.show()
