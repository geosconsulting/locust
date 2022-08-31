import rasterio
import xarray as xr
# import rioxarray

# import os
#
# os.environ['ECCODES_DEFINITON_PATH'] = 'C:/Users/pc/anaconda3/envs/geospatial/Library/share/eccodes/definitions'


ds = xr.open_dataset('C:/Users/pc/PycharmProjects/locust/data/ecmwf/May_22_2021_meteo/A1D05221200052212011.grib',
                     engine='cfgrib',
                     backend_kwargs={'filter_by_keys': {'edition': 1}})

print(ds)

