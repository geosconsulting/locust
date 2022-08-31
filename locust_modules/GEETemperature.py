import ee
import eeconvert
import datetime
import pandas as pd
from geoalchemy2 import Geometry , WKTElement

from .CommonGEE import GEEDefaults


class GEETemperature(GEEDefaults):

    def __init__(self):
        super(GEETemperature , self).__init__()
        self.__era5_collection = ee.ImageCollection('ECMWF/ERA5/DAILY')
        self.__era5_land_collection = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")

    def get_raster_stored_in_gee(self):

        # Get the date range of images in the collection.
        rango = self.__era5_land_collection.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])

        # Passing numeric date to standard
        init_date = ee.Date(rango.get('min')).getInfo()['value'] / 1000.
        init_date_f = datetime.datetime.utcfromtimestamp(init_date).strftime('%Y-%m-%d %H:%M:%S')

        last_date = ee.Date(rango.get('max')).getInfo()['value'] / 1000.
        last_date_f = datetime.datetime.utcfromtimestamp(last_date).strftime('%Y-%m-%d %H:%M:%S')

        date_for_table = last_date_f.split(" ")[0]

        return init_date_f, last_date_f, date_for_table