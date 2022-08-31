import os
import logging
from datetime import datetime
import click
from sqlalchemy import create_engine

# import matplotlib.pyplot as plt
# import geopandas as gpd
# import geoplot as gplt


@click.command()
@click.option('-y', '--years', default=1, help='Before or after 2020', prompt="Before 2020(1) or after (2)")
@click.option('-s', '--single', default='all', help='One year', type=click.Choice(['all', 'one'], case_sensitive=False),
              prompt="All years or a single year")
def file_check(years, single):

    if years == 1:
        chosen_path = '../data/extract/1985_2019'
    else:
        chosen_path = '../data/extract/2020 in progress'

    if single == 'one':
        print('Enter year:')
        x = input()
        if years == 1:
            chosen_path = chosen_path + '/' + x + 'yearly'

    click.echo("Working with following path {}".format(chosen_path))

    for main_dir, sub_dirs, files_in_subdir in os.walk(chosen_path):
        # logger.debug("main_dir {} sub_dirs {} files_in_subdir {}".format(main_dir, sub_dirs, files_in_subdir))
        if len(sub_dirs) == 0:
            if 'monthly' not in main_dir:
                shp_counter = [fi for fi in files_in_subdir if fi.endswith(".shp")]
                active_year = main_dir.split("\\")[1].replace('yearly', "")
                logger.info("Directory: {} - Year: {} - Number of Shp: {}".format(main_dir, active_year, len(shp_counter)))
                logger.debug("Year {}".format(active_year))
                for filename in files_in_subdir:
                    filepath = main_dir + os.sep + filename
                    if filepath.endswith(".shp"):
                        print(filename)
            else:
                for main_dir_monthly , sub_dirs_monthly , files_in_subdir_monthly in os.walk(main_dir):
                    shp_counter = [fi for fi in files_in_subdir_monthly if fi.endswith(".shp")]
                    year_month = main_dir_monthly.split("\\")
                    active_year = year_month[1].replace('monthly', "")
                    datetime_object = datetime.strptime(year_month[-1] , "%m")
                    month_name = datetime_object.strftime("%B")
                    logger.info("Directory: {} - Year: {} - Month:{} - Number of Shp: {}".format(main_dir_monthly ,
                                                                                                 active_year ,
                                                                                                 month_name,
                                                                                                 len(shp_counter)))
                    logger.debug("Year {} Month {}".format(active_year, month_name))
                    for filename_monthly in files_in_subdir_monthly:
                        filepath_monthly = main_dir_monthly + os.sep + filename_monthly
                        if filepath_monthly.endswith(".shp"):
                            print(filename_monthly)


def write_2_pg(table_locust):
    """Create Postgresql table from shapefiles

                Args:
                    table_locust: name of table to be created

                Returns:
                    None

                """

    # db_connection_url = "postgres://postgres:antarone@172.30.88.60:5432/locust"
    db_connection_url = "postgres://postgres:antarone@localhost:5432/locust"

    engine = create_engine(db_connection_url)
    table_locust.to_postgis(name="swarm", con=engine)


if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(filename)s  %(lineno)d %(funcName)s() %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("../app.log" , mode='w')
    file_format = logging.Formatter("%(message)s")
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    file_handler.setLevel(logging.INFO)
    file_check()
