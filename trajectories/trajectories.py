import requests
import json
import urllib.request
import zipfile
from datetime import datetime
from configparser import ConfigParser

import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

from arcgis.gis import GIS
from geopy.geocoders import Nominatim
from geoalchemy2 import Geometry , WKTElement
from sqlalchemy import *
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs  # import projections
import cartopy.feature as cf  # import features

from MultiChoice import MultiChoice

import click

URL_POST = "https://locusts.arl.noaa.gov/rest/v1/batch"
URL = "https://locusts.arl.noaa.gov/rest/v1/batch/"
OUTPUT_URL = "https://locusts.arl.noaa.gov/pub/"


def config(filename='../credentials.ini'):
    # create a parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)
    #
    # if parser.has_section('agis'):
    #     params_agis = parser.items('agis')
    #     LOCUST_HUB = GIS(params_agis[0][1] , params_agis[1][1] , params_agis[2][1])
    # else:
    #     raise Exception('Section {0} not found in the {1} file'.format('agis' , filename))

    if parser.has_section('locust_api_noaa'):
        params = parser.items('locust_api_noaa')
        for param in params:
            API_KEY = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format('locust_api_noaa' , filename))

    return API_KEY #, LOCUST_HUB


@click.group(chain=True)
@click.option('-l' , '--location' , help='Starting Point' , type=str)
@click.option('-b' , '--batch_id' , help='Previous Run' , type=int)
@click.option('-sd' , '--start_date' , help='Start Day' , type=str)
@click.pass_context
def cli(ctx , location , batch_id , start_date):

    ctx.ensure_object(dict)

    ctx.obj['location'] = location
    ctx.obj['batch_id'] = batch_id

    if start_date is None:
        now = datetime.now()
        start_date = now.strftime("%Y-%m-%d")
    ctx.obj['start_date'] = start_date


@cli.command('lat-lon')
@click.pass_context
def lat_lon(ctx):

    geo_locator = Nominatim(user_agent="point_locust_modelling")
    geocoded_location = geo_locator.geocode(ctx.obj['location'])

    if geocoded_location is not None:
        ctx.obj['lat'] = geocoded_location.latitude
        ctx.obj['lon'] = geocoded_location.longitude
        click.echo(f"Geocoded {geocoded_location} , lat: {ctx.obj['lat']} , lon: {ctx.obj['lon']}")
    else:
        click.secho('Location not found' , fg='red')


@cli.command('check-batch')
@click.pass_context
def check_batch(ctx):
    click.echo(f"Verifying {URL + str(ctx.obj['batch_id'])}")

    try:
        r = requests.get(
                URL + str(ctx.obj['batch_id']) ,
                headers={"Locusts-API-Key": config() ,
                         "Content-type"   : "application/json" ,
                         "Accept"         : "application/json"}
        )

        click.secho(f"Batch num {ctx.obj['batch_id']} is {r.json()['status']}" , fg="green")
        print(r.json())

        if r.json()['status'] == 'COMPLETED':
            print('Download the data? (y or n):')
            resp_user = input()
            if resp_user == 'y':
                ctx.obj['out_id'] = r.json()['runs'][0]['id']
                ctx.obj['name'] = r.json()['runs'][0]['name']
                print(f'Downloading..')
                get_output(ctx.obj['batch_id'] , ctx.obj['out_id'] , ctx.obj['name'])
            else:
                print('Abort')
    except:
        click.secho(f"Batch num {ctx.obj['batch_id']} not found" , fg="red")


@click.command('run')
@click.pass_context
def run_trajectory(ctx):

    click.secho(f"Start Date: {ctx.obj['start_date']}  Lat {ctx.obj['lat']} Lon {ctx.obj['lon']}" , fg="yellow")

    data = [{"name"                       : ctx.obj['location'].replace(" " , "_") ,
             "latitude"                   : ctx.obj['lat'] ,  # 4.0,
             "longitude"                  : ctx.obj['lon'] ,  # 36.0,
             "height"                     : 500.0 ,
             "height2"                    : 1000.0 ,
             "meteorologicalData"         : "GFS" ,
             "startDate"                  : ctx.obj['start_date'] ,
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

    headers = {"Locusts-API-Key": config() ,
               "Content-type"   : "application/json" ,
               "Accept"         : "application/json"}

    r = requests.post(
            URL_POST ,
            headers=headers ,
            data=json.dumps(data)
    )

    # if r.status_code == 200:
    #     print(r.text)

    print(r.json())


cli.add_command(run_trajectory)


def get_output(bid , out_id , run_name):

    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trj_001.png
    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trajplot.ps
    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_trajplot.pdf
    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_HYSPLITtraj.kmz
    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257_gis.zip
    # https: // locusts.arl.noaa.gov / pub / swarm_7257 / swarm_7257.zip

    question = MultiChoice(
            "Download in which format?\n"
            "You must choose one of the following:" ,
            options=("Bitmap" , "PostScript" , "Pdf" , "Google KMZ" , "Shapefile" , "All") ,
    )
    answer = question()

    click.secho(f"Requested output {answer} for batch {bid} run id {out_id}" , fg='blue')

    if answer == 'Bitmap':
        end_point = (OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trj_001.png")
    elif answer == 'PostScript':
        end_point = (OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trajplot.ps")
    elif answer == 'Pdf':
        end_point = (OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_trajplot.pdf")
    elif answer == 'Google KMZ':
        end_point = (
                    OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_HYSPLITtraj.kmz")
    elif answer == 'Shapefile':
        end_point = (OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + "_gis.zip")
    else:
        end_point = (OUTPUT_URL + run_name + "_" + str(out_id) + "/" + run_name + "_" + str(out_id) + ".zip")

    response = requests.get(
            end_point ,
            headers={"Locusts-API-Key": config()[0],
                     "Content-type"   : "application/json" ,
                     "Accept"         : "application/json"}
    )

    if response.status_code == 200:
        if answer == 'Bitmap':
            image = Image.open(BytesIO(response.content))
            plt.imshow(image)
            plt.show()
        elif answer == 'Shapefile':
            # open method to open a file on your system and write the contents
            with open(f"swarm_{out_id}_gis.zip" , "wb") as code:
                code.write(response.content)
        elif answer == 'All':
            # Copy a network object to a local file
            urllib.request.urlretrieve(end_point , f"swarm_{out_id}.zip")


@cli.command('shp2pg')
@click.argument('zip_file')
@click.pass_context
def shp_2_pg(ctx , zip_file):
    print(ctx.obj)

    engine = create_engine('postgresql://postgres:antarone@localhost:5432/locust')

    root_dir = zip_file.split('.')[0] + "/"

    list_shp = []

    with zipfile.ZipFile(zip_file , 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.split(".")[1] == 'shp':
                list_shp.append(file.split(".")[0])

        zip_ref.extractall(zip_file.split('.')[0])

    # print(list_shp)

    count_underscore = list_shp[0].count('_')
    elements = list_shp[0].split('_')[:count_underscore]

    table_name_root = ['_'.join(elements)][0]
    table_name_taking_off = table_name_root + '_takeoff_pts'
    table_name_landing = table_name_root + '_landing_pts'
    table_name_trajectories = table_name_root + '_all_trajs'

    taking_off_points = gpd.read_file(root_dir + table_name_root + '_takeoff_pts.shp')
    landing_points = gpd.read_file(root_dir + table_name_root + '_landing_pts.shp')
    trajectories = gpd.read_file(root_dir + table_name_root + '_all_trajs.shp')

    # taking_off_points_4326 = taking_off_points.to_crs("EPSG:4326")
    # print(taking_off_points_4326)
    # landing_points_4326 = landing_points.to_crs("EPSG:4326")
    # trajectories_4326 = trajectories.to_crs("EPSG:4326")

    # taking_off_points_web_mercator = taking_off_points.to_crs("EPSG:3857")
    # print(taking_off_points_web_mercator)

    # rivers_50m = cf.NaturalEarthFeature('physical' , 'rivers_lake_centerlines' , '10m')
    # print(rivers_50m.crs)
    #
    # crs = ccrs.PlateCarree()
    # ax = plt.axes(projection=crs)  # create a set of axes with Mercator projection
    # ax.add_feature(cf.COASTLINE)  # plot some data on them
    # ax.set_title("Model Plot")  # label it
    # ax.add_feature(cf.OCEAN)
    # ax.add_feature(cf.LAND , edgecolor='black')
    # ax.add_feature(cf.LAKES , edgecolor='black')
    # # ax.add_feature(rivers_50m , facecolor='None' , edgecolor='b')
    # ax.add_geometries(taking_off_points.geometry , crs=ccrs.PlateCarree() , color='red')
    # ax.gridlines()
    # plt.show()

    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))

    fig , ax = plt.subplots(figsize=(12 , 8))
    taking_off_points.plot(ax=ax, c='green')
    landing_points.plot(ax=ax , c='red')
    trajectories.plot(ax=ax , cmap='Reds' , alpha=0.5)
    world.plot(ax=ax)
    # cities.plot(ax=ax, c='yellow')
    plt.show()

    # taking_off_points.to_postgis(table_name_taking_off , engine , if_exists='replace',
    #                              schema='trajectories', index=True , index_label='Index')
    # landing_points.to_postgis(table_name_landing , engine , if_exists='replace',
    #                                schema='trajectories' , index=True , index_label='Index')
    # trajectories.to_postgis(table_name_trajectories , engine , if_exists='replace',
    #                              schema='trajectories', index=True , index_label='Index')


@cli.command('all-batches')
@click.option('--lower_batch' , '-lb' , default=7240 , type=int)
@click.option('--upper_batch' , '-ub' , default=7290 , type=int)
def check_batches(lower_batch , upper_batch):
    list_batches = []

    for num_batch in range(lower_batch , upper_batch):
        r = requests.get(URL + str(num_batch) ,
                         headers={"Locusts-API-Key": "21c0d4e0-2467-44b5-8407-6575c41909a2" ,
                                  "Content-type"   : "application/json" ,
                                  "Accept"         : "application/json"}
                         )

        try:
            print(f"Found batch {r.json()['batchId']}")
            list_batches.append(r.json()['batchId'])
        except:
            print(f"Batch {num_batch} not found")

    with open('list_batches.txt' , 'w') as file_handle:
        for list_item in list_batches:
            file_handle.write('%s\n' % list_item)


def locust_hub():
    pass


@click.command()
def gfs_noaa():
    r1 = requests.get(
            "https://www.ncdc.noaa.gov/cdo-web/api/v2/datasets" ,
            headers={"token"       : "yIgJOqrVfoTJMqReuaWxTWRuOtDBPZpJ" ,
                     "Content-type": "application/json" ,
                     "Accept"      : "application/json"}
    )

    print(r1.text)

    return r1.text


cli.add_command(gfs_noaa)

if __name__ == '__main__':
    cli(obj={})
