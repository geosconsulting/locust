import requests
from configparser import ConfigParser
import os


class Config:

    @staticmethod
    def connections_details(service, file_name='credentials.ini'):

        # file_path = os.path.join(os.pardir, file_name)

        credentials = {}
        if os.path.isfile(file_name):
            # create a parser
            parser = ConfigParser()
            # read config file
            parser.read(file_name)

            if parser.has_section(service):
                params = parser.items(service)
                for param in params:
                    credentials[param[0]] = param[1]
                return credentials
            else:
                raise Exception('Section {0} not found in the {1} file'.format(service, file_name))
        else:
            print("File does not exist")

    @staticmethod
    def gfs_noaa():
        r1 = requests.get(
            "https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets",
            headers={"token": "yIgJOqrVfoTJMqReuaWxTWRuOtDBPZpJ",
                     "Content-type": "application/json",
                     "Accept": "application/json"}
        )

        print(r1.text)
        return r1.text
