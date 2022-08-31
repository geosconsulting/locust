import ee
from ee.batch import Export
# import eeconvert
import datetime
import pandas as pd
from geoalchemy2 import Geometry , WKTElement


from .CommonGEE import GEEDefaults


class GEEPrecipitation(GEEDefaults):

    def __init__(self):
        super(GEEPrecipitation , self).__init__()

        self.__chirps_collection_daily = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
        self.__chirps_collection_pentad = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')

    def get_raster_stored_in_gee(self):

        # Get the date range of images in the collection.
        rango = self.__chirps_collection_daily.reduceColumns(ee.Reducer.minMax(), ["system:time_start"])

        # Passing numeric date to standard
        init_date = ee.Date(rango.get('min')).getInfo()['value'] / 1000.
        init_date_f = datetime.datetime.utcfromtimestamp(init_date).strftime('%Y-%m-%d %H:%M:%S')

        last_date = ee.Date(rango.get('max')).getInfo()['value'] / 1000.
        last_date_f = datetime.datetime.utcfromtimestamp(last_date).strftime('%Y-%m-%d %H:%M:%S')

        date_for_table = last_date_f.split(" ")[0]

        return init_date_f, last_date_f, date_for_table

    @staticmethod
    def clean_submission_data(df_points):
        """
        Remove null data and data with wrong attributes
        :param df_points: dataframe containing scouting
        :return:
        """
        df_columns_keep = [u'REPORTID' , u'STARTDATE' , u'COUNTRYID', u'LOCNAME', u'SHAPE']
        df_swarm_gee_calculations = df_points[df_columns_keep]
        df_swarm_gee_no_duplicates = df_swarm_gee_calculations.drop_duplicates(subset=df_columns_keep , keep='last')
        list_of_dates = pd.Series(df_swarm_gee_no_duplicates.STARTDATE.unique())
        list_of_dates.dropna(inplace=True)
        min_date = list_of_dates.min()
        max_date = list_of_dates.max()

        return df_swarm_gee_no_duplicates , list_of_dates , min_date , max_date

    def gee_chirps_filtering_by_date(self , analysis_initial_datetime , analysis_final_datetime):
        """
        Sub-select CHIRPS using the min and max date of the points collected with FAMEWS
        :param analysis_initial_datetime:
        :param analysis_final_datetime:
        :return:
        """
        chirps_filtered = self.__chirps_collection_daily.filterDate(analysis_initial_datetime ,
                                                                    analysis_final_datetime).select('precipitation')

        num_chirps = chirps_filtered.size().getInfo()

        return chirps_filtered , num_chirps

    def export_precipitation_to_postgis(self , country , gdf_looping, metereological_param):  # date_for_table,

        table_name_looping = metereological_param + "_" + country.lower() + "_" + super()._TIMESTAMP_SUFFIX
        gdf_looping.to_sql(table_name_looping ,
                           super()._PG_ENGINE ,
                           if_exists='append' ,
                           index=False ,
                           dtype={'geom': Geometry('POINT' , srid='4326')})

        return table_name_looping

    @staticmethod
    def data_export_gdrive(feature_collection_with_precipitation):
        # Export
        export_task = Export.table.toDrive(
                collection=feature_collection_with_precipitation ,
                folder="testExtract" ,
                fileFormat='csv' ,
                description="testExtract")

        export_task.start()
        state = export_task.status()['state']

        while state in ['READY' , 'RUNNING']:
            print(state + '...')
            state = export_task.status()['state']

        print('Done.' , export_task.status())

    def get_point_value(self, i_date, f_date, lat, lon):

        filtered_chirps_daily = self.__chirps_collection_daily.select('precipitation').filterDate(i_date , f_date)
        ee_point = ee.Geometry.Point(lon , lat)

        scale = 1000  # scale in meters

        prec_point = self.__chirps_collection_daily.mean().sample(ee_point , scale).first().get('precipitation').getInfo()

        prec_point_ts = filtered_chirps_daily.getRegion(ee_point , scale).getInfo()

        return prec_point , prec_point_ts






