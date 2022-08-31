import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
import pandas as pd
import glob
import os
from google.cloud import storage
from datetime import date , datetime , timedelta
from pathlib import Path


class MeteorologyBio:
    # LOBELIA
    url = "https://api-sm.lobelia.earth/sm"
    url_ts = 'https://api-sm.lobelia.earth/sm-time-series'
    url_region = 'https://api-sm.lobelia.earth/regions'

    # ECMWF
    url_fao_gcp = 'https://console.cloud.google.com/storage/browser/fao-ecmwf-data'

    def __init__(self , analysis_date_ecmwf , nopack='true'):

        self.headers = {
            'Authorization': 'Basic ZmFvOjBuZUttU29pbE1vMXN0dXJl'
        }
        self.nopack = nopack

        # self.__client = storage.Client(client_endpoint)
        # self.__bucket = self.__client.get_bucket(bucket_ecmwf)

        self.__date_ecmwf = analysis_date_ecmwf

        # AVAILABLE FILES AREA LAGGING ONE DAY
        self._string_search = self.__date_ecmwf.strftime("%m%d")
        self._string_search_anomalies = self.__date_ecmwf.strftime("%m")

        self._string_search_midnight_batch = None
        self._string_search_midday_batch = None

        # Precipitation Anomalies
        self._string_search_anomalies_batch = None

        # Storms
        self._string_search_storm_batch = None

        self.__blobs_by_category = {}
        self.__working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__) , os.pardir))
        self.__dirs = ["meteo" , "anomalies" , "storms"]

        self.__download_root_dir = datetime.strptime(self._string_search + "2021" , "%m%d%Y").strftime("%B_%d_%Y")
        self.__download_dirs = []

    @property
    def working_dir(self):
        return self.__working_dir

    @property
    def analysis_date_ecmwf(self):
        return self.__date_ecmwf

    @property
    def search_strings(self):
        return self._string_search

    @property
    def blobs_by_category(self):
        return self.__blobs_by_category

    @property
    def download_dirs_postfix(self):
        return self.__dirs

    @property
    def download_dirs(self):
        return self.__download_dirs

    # Lobelia parts
    def soil_map_country(self , decade , region):
        params = {
            'decade': decade ,
            'region': region ,
            'noPack': self.nopack}

        response = requests.get(self.url , params=params , headers=self.headers)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
        else:
            response.text

        return image

    def soil_map_province(self , decade , region):
        params = {
            'decade': decade ,
            'region': region ,
            'noPack': self.nopack}

        response = requests.get(self.url , params=params , headers=self.headers)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
        else:
            response.text

        return image

    def time_series(self , decade , lat , lon):
        params_ts = {
            'decade': decade ,
            'noPack': self.nopack ,
            'lat'   : lat ,
            'lon'   : lon}

        response_ts = requests.get(self.url_ts , params=params_ts , headers=self.headers)
        response_json = response_ts.json()

        return response_json

    @staticmethod
    def plot_time_series(response_json):

        df = pd.DataFrame(response_json)
        sns.set_theme(style="whitegrid")
        sns.set(context="paper" , font="monospace")

        sns.lineplot(x=df.decade , y=df.value , data=df , palette="tab10" , linewidth=2.5)
        plt.xticks(rotation=45)
        plt.show()

    def get_provinces(self , country):

        response_region = requests.get(self.url_region , headers=self.headers)
        response_region_json = response_region.json()

        df_region = pd.json_normalize(response_region_json ,
                                      meta=['name'] ,
                                      record_path='regions' ,
                                      record_prefix='reg_')

        df_provinces_country = df_region[df_region['name'] == country]

        return df_provinces_country

    # ECMWF Parts
    def generate_search_strings(self):

        # AVAILABLE FILES AREA LAGGING ONE DAY
        self._string_search_midnight_batch = 'A1D' + self._string_search + "00"
        self._string_search_midday_batch = 'A1D' + self._string_search + "12"

        # Precipitation Anomalies
        self._string_search_anomalies_batch = 'A1F' + self._string_search_anomalies

        # Storms
        self._string_search_storm_batch = 'A1T' + self._string_search

    def search_blobs(self):

        blobs_meteo = list(self.__client.list_blobs(self.__bucket , prefix=self._string_search_midday_batch))
        self.__blobs_by_category['meteo'] = blobs_meteo

        blobs_anomalies = list(self.__client.list_blobs(self.__bucket , prefix=self._string_search_anomalies_batch))
        self.__blobs_by_category['anomalies'] = blobs_anomalies

        blobs_storms = list(self.__client.list_blobs(self.__bucket , prefix=self._string_search_storm_batch))
        self.__blobs_by_category['storms'] = blobs_storms

    def create_download_directory(self):

        for blob_dir in self.__dirs:
            dir_name = "/".join([self.__working_dir , 'data' , 'ecmwf' , self.__download_root_dir + '_' + blob_dir])
            self.__download_dirs.append(dir_name)
            try:
                os.mkdir(dir_name)
            except FileExistsError:
                pass

    def download_blobs(self , category):

        index_dir = list(self.blobs_by_category.keys()).index(category)
        file_list = [file.name for file in self.blobs_by_category[category]]
        num_interaction = 0

        for curr_grib in file_list:
            num_interaction += 1
            blob = self.__bucket.get_blob(curr_grib)
            destination_grib_file = "{}/{}".format(self.__download_dirs[index_dir] , curr_grib + ".grib")
            if Path(destination_grib_file).is_file():
                print("Blob {} has been downloaded already".format(curr_grib))
            else:
                blob.download_to_filename(destination_grib_file)
                print("Blob {} downloaded to {}".format(curr_grib , destination_grib_file))

        return num_interaction

    def get_filenames_category_blobs_collection(self , category):

        index_dir = list(self.blobs_by_category.keys()).index(category)
        collection_directory = self.download_dirs[index_dir]
        category_files = [f for f in os.listdir(collection_directory) if
                          os.path.isfile(os.path.join(collection_directory , f))]

        return category_files

    def generate_list_dates_grib_files(self):

        grib_file = self.blobs_by_category['meteo'][53].name
        grib_type = grib_file[:3]
        starting_date = grib_file[3:7]
        time_batch = grib_file[7:11]
        step_date = grib_file[11:15]
        time_step = grib_file[15:19]
        grib_year = grib_file[-1]

        return starting_date

    @staticmethod
    def return_grib_variables(grib_file):
        variables = []
        for temp in grib_file:
            variables.append(temp)
        return variables

    @staticmethod
    def merge_downloaded_gribs(collection_dir, category, hpa):

        file_out_name = collection_dir.split("/")[-2] + '.nc'
        file_out_dir = collection_dir.replace('\\' , '/')
        list_grib_files = glob.glob(os.path.join(collection_dir , '*.grib'))

        if Path(file_out_dir + file_out_name).exists():
            print("File exists {} ".format(file_out_dir + file_out_name))
            nc_file = xr.open_dataset(file_out_dir + file_out_name)
            return nc_file
        else:
            print("File does not exists {} ".format(file_out_dir + file_out_name))
            grib_file = list_grib_files[0].replace('\\' , '/')
            ds_tot = xr.open_dataset(grib_file ,
                                     engine='cfgrib' ,
                                     backend_kwargs={'filter_by_keys': {'edition': 1}}).sel(isobaricInhPa=hpa)
            if category == 'meteo':

                ds_tot['celsius'] = ds_tot.t2m - 273.15
                ds_tot['celsius'].attrs['long_name'] = "t2m in degree celsius"
                ds_tot['celsius'].attrs['units'] = "degrees"

                ds_tot['tp_mm'] = ds_tot.tp * 1000
                ds_tot['tp_mm'].attrs['long_name'] = "total precipitation in mm"
                ds_tot['tp_mm'].attrs['units'] = "millimiters"

            for curr_grib_file in enumerate(list_grib_files):
                grib_index = curr_grib_file[0]
                if grib_index == 0:
                    print("Step {} Month {} Day {} Time {}".format(grib_index ,
                                                                   ds_tot.valid_time.dt.month.values ,
                                                                   ds_tot.valid_time.dt.day.values ,
                                                                   ds_tot.valid_time.dt.time.values))
                elif grib_index >= 1:
                    ds = xr.open_dataset(curr_grib_file[1].replace('\\' , '/') ,
                                         engine='cfgrib' ,
                                         backend_kwargs={'filter_by_keys': {'edition': 1}}).sel(isobaricInhPa=1000)

                    if category == 'meteo':

                        ds['celsius'] = ds.t2m - 273.15
                        ds['celsius'].attrs['long_name'] = "celsius"
                        ds['celsius'].attrs['units'] = "degrees"

                        ds['tp_mm'] = ds.tp * 1000
                        ds['tp_mm'].attrs['long_name'] = "total_precipitation_mm"
                        ds['tp_mm'].attrs['units'] = "millimiters"

                    print("Step {} Month {} Day {} Time {}".format(grib_index ,
                                                                   ds.valid_time.dt.month.values ,
                                                                   ds.valid_time.dt.day.values ,
                                                                   ds.valid_time.dt.time.values))
                    ds_tot = xr.concat([ds_tot , ds] , 'valid_time')

        # if category == 'meteo':
        #     ds_tot['celsius'] = ds.t2m - 273.15
        #     ds_tot['celsius'].attrs['long_name'] = "celsius"

        ds_tot.to_netcdf(file_out_dir + file_out_name)

        nc_file = xr.open_dataset(file_out_dir + file_out_name)

        return nc_file

    def remove_downloaded_gribs(self) :

        import shutil
        for cur_dir in list(self.download_dirs):
            try:
                shutil.rmtree(cur_dir)
            except OSError as e:
                print("Error: %s : %s" % (cur_dir , e.strerror))




