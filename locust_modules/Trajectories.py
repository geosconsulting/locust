import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import zipfile
import os.path
import urllib.request


class Trajectory:

    URL_POST = "https://locusts.arl.noaa.gov/rest/v1/batch/"
    OUTPUT_URL = "https://locusts.arl.noaa.gov/pub/"

    def __init__(self):

        self._api_key = None
        self._api_key_gfs = None
        self._start_date = datetime.now().strftime("%Y-%m-%d")
        self._trajectory_id = None
        self._trajectory_name = None

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self , start_date):
        self._start_date = start_date

    @property
    def api_key_manager(self):
        return self._api_key

    @api_key_manager.setter
    def api_key_manager(self , key):
        self._api_key = key

    @property
    def trajectory_id_manager(self):
        return self._trajectory_id

    @trajectory_id_manager.setter
    def trajectory_id_manager(self , trajectory_id):
        self._trajectory_id = trajectory_id

    @property
    def trajectory_name(self):
        return self._trajectory_name

    def check_batch(self):

        try:
            r = requests.get(
                    self.URL_POST + str(self.trajectory_id_manager) ,
                    headers={"Locusts-API-Key": self.api_key_manager ,
                             "Content-type"   : "application/json" ,
                             "Accept"         : "application/json"}
            )

            if r.json()['status'] == 'COMPLETED':
                self._trajectory_id = r.json()['batchId']
                # status = r.json()['status']
                # run_id = r.json()['runs'][0]['id']
                self._trajectory_name = r.json()['runs'][0]['name']
                # run_status = r.json()['runs'][0]['status']
                return r.json()
        except requests.RequestException:
            print(f"Batch num {self.trajectory_id_manager} not found")

    def run_trajectory(self , location , lat , lon):

        data = [{"name"                       : location.replace(" " , "_") ,
                 "latitude"                   : lat ,  # 4.0,
                 "longitude"                  : lon ,  # 36.0,
                 "height"                     : 500.0 ,
                 "height2"                    : 1000.0 ,
                 "meteorologicalData"         : "GFS" ,
                 "startDate"                  : self.start_date ,
                 "firstDayStartHour"          : None ,
                 "firstDayStartMinute"        : None ,
                 "firstDayEndingHour"         : None ,
                 "firstDayEndingMinute"       : None ,
                 "durationOfSimulation"       : 3 ,
                 "simulationDirection"        : 0 ,
                 "nonstopFlight"              : False ,
                 "takeoffTimeAfterSunrise"    : 2.0 ,
                 "landingTimeBeforeSunset"    : 1.0 ,
                 "mapBackground"              : "terrain" ,
                 "spatialPlotRadius"          : 500.0 ,
                 "verticalMotion"             : 4 ,
                 "gisFileByDay"               : True ,
                 "gisFileByHeight"            : False ,
                 "gisFileByDayHeight"         : False ,
                 "gisFileAllTrajectoriesInOne": True ,
                 "useLineShapefile"           : True ,
                 "colorOpacity"               : 100 ,
                 "includeHysplitFile"         : True ,
                 "includeImage"               : True ,
                 "includePostscript"          : False ,
                 "includePDF"                 : True ,
                 "includeShapefile"           : True ,
                 "includeKMZ"                 : True}]

        headers = {"Locusts-API-Key": self.api_key_manager ,
                   "Content-type"   : "application/json" ,
                   "Accept"         : "application/json"}

        r = requests.post(
                self.URL_POST ,
                headers=headers ,
                data=json.dumps(data)
        )

        if r.status_code == 200:
            return r.json()
        else:
            return r.json()

    def check_batches(self , lower_batch , upper_batch):
        list_batches = []

        for num_batch in range(lower_batch , upper_batch):
            r = requests.get(self.URL_POST + str(num_batch) ,
                             headers={"Locusts-API-Key": self.api_key_manager ,
                                      "Content-type"   : "application/json" ,
                                      "Accept"         : "application/json"}
                             )

            try:
                print(f"Found batch {r.json()['batchId']}")
                list_batches.append(r.json()['batchId'])
            except requests.RequestException:
                print(f"Batch {num_batch} not found")

        with open('list_batches.txt' , 'w') as file_handle:
            for list_item in list_batches:
                file_handle.write('%s\n' % list_item)

    def get_output(self , out_type, out_id, run_name):

        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trj_001.png
        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trajplot.ps
        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trajplot.pdf
        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_HYSPLITtraj.kmz
        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_gis.zip
        # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257.zip

        if out_type == 'Bitmap':
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trj_001.png")
        elif out_type == 'PostScript':
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trajplot.ps")
        elif out_type == 'Pdf':
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trajplot.pdf")
        elif out_type == 'Google KMZ':
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_HYSPLITtraj.kmz")
        elif out_type == 'Shapefile':
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_gis.zip")
        else:
            end_point = (self.OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + ".zip")

        response = requests.get(
                end_point ,
                headers={"Locusts-API-Key": self.api_key_manager ,
                         "Content-type"   : "application/json" ,
                         "Accept"         : "application/json"}
        )

        if response.status_code == 200:
            if out_type == 'Bitmap':
                image = Image.open(BytesIO(response.content))
                plt.imshow(image)
                plt.show()
            elif out_type == 'Shapefile':
                # open method to open a file on your system and write the contents
                zip_shp = f"trajectories/swarm_{out_id}_gis.zip"
                with open(zip_shp , "wb") as code:
                    code.write(response.content)
                return zip_shp
            elif out_type == 'All':
                # Copy a network object to a local file
                zip_all = f"trajectories/swarm_{out_id}.zip"
                urllib.request.urlretrieve(end_point , zip_all)
                return zip_all

    @staticmethod
    def shapefile_explode(zip_file):

        target_location = zip_file.split('.')[0] + "/"

        list_shp = []
        with zipfile.ZipFile(zip_file , 'r') as zip_ref:
            print(zip_ref.namelist())
            for member in zip_ref.namelist():
                if os.path.exists(target_location + r'/' + member) or os.path.isfile(target_location + r'/' + member):
                    print('Error: ' , member , ' exists.')
                else:
                    zip_ref.extract(member , target_location)
                    list_shp.append(member.split(".")[0])
            # zip_ref.extractall(zip_file.split('.')[0])

        # count_underscore = list_shp[0].count('_')
        # elements = list_shp[0].split('_')[:count_underscore]
        # table_name_root = ['_'.join(elements)][0]
        #
        # taking_off_points = target_location + table_name_root + '_takeoff_pts.shp'
        # landing_points = target_location + table_name_root + '_landing_pts.shp'
        # trajectories = target_location + table_name_root + '_all_trajs.shp'
        #
        # return taking_off_points , landing_points , trajectories

    @staticmethod
    def gfs_noaa():
        r1 = requests.get(
                "https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets" ,
                headers={"token"       : "yIgJOqrVfoTJMqReuaWxTWRuOtDBPZpJ" ,
                         "Content-type": "application/json" ,
                         "Accept"      : "application/json"}
        )

        return r1.text

