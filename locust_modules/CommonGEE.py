from datetime import datetime
import pycountry
import pandas as pd
import ee


class GEEDefaults:

    """
    General settings for data management of API
    """

    _TIMESTAMP_SUFFIX = datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self, ):
        """
        Set position of shapefiles in __shape_admin_0,__shape_admin_1,__shape_admin_2
        """
        ee.Initialize()
        self.__shape_admin_0 = None
        self.__shape_admin_1 = None
        self.__shape_admin_2 = None

        self.__working_dir = None
        self.__country_iso = None
        self.__country_name = None

    @property
    def working_dir(self):
        """
        Working directory of analysis
        :return: directory
        """
        return self.__working_dir

    @working_dir.setter
    def working_dir(self, working_dir):
        """
        set the working directory of the analysis
        :param working_dir:
        :return:
        """
        self.__working_dir = working_dir

    @property
    def country_name(self):
        """
        The country for which the data will be selected
        :return:
        """
        return self.__country_name

    @country_name.setter
    def country_name(self, country_iso):
        """
        Set the country for selecting the records for
        :param country_iso: ISO2 Code
        :return: Nothing
        """

        if country_iso == 'TL':
            self.__country_name = 'East Timor'
        else:
            for country in list(pycountry.countries):
                try:
                    if country_iso == country.alpha_2:
                        self.__country_name = country.name
                except NameError:
                    print(NameError)

    @property
    def country_iso(self):
        """
        The iso code of the country for which the data will be selected
        :return:
        """
        return self.__country_iso

    @country_iso.setter
    def country_iso(self, country_iso):
        """
        Set the country for selecting the records for
        :param country_iso: ISO2
        :return: Nothing
        """
        self.__country_iso = country_iso

    @property
    def adm0(self):
        """
        Get the country selected for analysis
        :return: shapefile of countries
        """
        return self.__shape_admin_0

    @adm0.setter
    def adm0(self , working_dir):
        """
        Set shapefile of countries
        :return: Path to Admin 0 shapefile
        """
        self.__shape_admin_0 = working_dir + '/geodata/GAUL/g2015_2014_0/g2015_2014_0.shp'

    @property
    def adm1(self):
        return self.__shape_admin_1

    @adm1.setter
    def adm1(self , working_dir):
        """
        Set shapefile of regions
        :return: Path to Admin 1 shapefile
        """
        self.__shape_admin_1 = working_dir + '/geodata/GAUL/g2015_2014_1/g2015_2014_1.shp'

    @property
    def adm2(self):
        return self.__shape_admin_2

    @adm2.setter
    def adm2(self , working_dir):
        """
        Set shapefile of povinces
        :return: Path to Admin 2 shapefile
        """
        self.__shape_admin_2 = working_dir + '/geodata/GAUL/g2015_2014_2/g2015_2014_2.shp'

    @staticmethod
    def ee_array_to_df(arr , list_of_bands):
        """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
        df = pd.DataFrame(arr)

        # Rearrange the header.
        headers = df.iloc[0]
        df = pd.DataFrame(df.values[1:] , columns=headers)

        # Remove rows without data inside.
        df = df[['longitude' , 'latitude' , 'time' , *list_of_bands]].dropna()

        # Convert the data to numeric values.
        for band in list_of_bands:
            df[band] = pd.to_numeric(df[band] , errors='coerce')

        # Convert the time field into a datetime.
        df['datetime'] = pd.to_datetime(df['time'] , unit='ms')

        # Keep the columns of interest.
        df = df[['time' , 'datetime' , *list_of_bands]]

        return df


