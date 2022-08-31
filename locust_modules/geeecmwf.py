import ee
from ee.batch import Export
import datetime
import pandas as pd
from geoalchemy2 import Geometry

from .CommonGEE import GEEDefaults


class GEEECMWF(GEEDefaults):

    def __init__(self):
        super(GEEECMWF, self).__init__()

        self._ecmwf_era5_land_hourly = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')

    def get_raster_stored_in_gee(self):
        """
        Get the ECMWF Land stored in GEE
        Returns:

            init_date_f: date for first dataset available
            last_date_f: date for last dataset available
            date_for_table: date for last dataset available converted to string

        """

        # Get the date range of images in the collection.
        rango = self._ecmwf_era5_land_hourly.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])

        # Passing numeric date to standard
        init_date = ee.Date(rango.get('min')).getInfo()['value'] / 1000.
        init_date_f = datetime.datetime.utcfromtimestamp(init_date).strftime('%Y-%m-%d %H:%M:%S')

        last_date = ee.Date(rango.get('max')).getInfo()['value'] / 1000.
        last_date_f = datetime.datetime.utcfromtimestamp(last_date).strftime('%Y-%m-%d %H:%M:%S')

        return init_date_f, last_date_f

    def get_point_value(self, i_date, f_date, lat, lon):
        filtered_chirps_daily = self._ecmwf_era5_land_hourly.select('precipitation').filterDate(i_date, f_date)
        ee_point = ee.Geometry.Point(lon, lat)

        scale = 1000  # scale in meters

        prec_point = self._ecmwf_era5_land_hourly.mean().sample(ee_point, scale).first().get('precipitation').getInfo()

        prec_point_ts = filtered_chirps_daily.getRegion(ee_point, scale).getInfo()

        return prec_point, prec_point_ts
