import os
import logging
# import matplotlib.pyplot as plt
# import geopandas as gpd
# import geoplot as gplt
# from sqlalchemy import create_engine

# from models import read_zip

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(filename)s  %(lineno)d %(funcName)s() %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

path = '../data/extract/'
path1 = 'data/extract/1985_2019/1985yearly'
path_1985_2019 = '../data/extract/1985_2019'

# list_files = read_zip
# print(list_files.list_files_shp)
# shp_files = glob.glob(path + "/**/*.shp", recursive=True)
# print(shp_files)

# for filename in os.listdir(path1):
#     if filename.endswith(".shp"):
#         print(os.path.join(path, filename))
#     else:
#         continue

for subdir, dirs, files in os.walk(path_1985_2019):
    if 'monthly' not in subdir:
        logger.debug("Yearly data in {}".format(subdir))
        for filename in files:
            filepath = subdir + os.sep + filename
            if filepath.endswith(".shp"):
                logger.info(filename)
                # logger.info(filepath)
                continue
    else:
        for subdir_monthly , dirs_monthly , files_monthly in os.walk(subdir):
            logger.info(subdir_monthly)
            for filename_monthly in files_monthly:
                filepath_monthly = subdir_monthly + os.sep + filename_monthly
                if filepath_monthly.endswith(".shp"):
                    logger.info(filename_monthly)
                    # print(filepath_monthly)


# swarm_1985 = gpd.read_file('data/extract/1985_2019/1985yearly/19850101_19860101_Swarm.shp')
# swarm_1986 = gpd.read_file('data/extract/1985_2019/1986yearly/19860101_19870101_Swarm.shp')
# joined = swarm_1985.append(swarm_1986)
# gplt.pointplot(swarm_1985, figsize=(8, 4))
# plt.show()

# db_connection_url = "postgres://postgres:antarone@172.30.88.60:5432/locust"
# db_connection_url = "postgres://postgres:antarone@localhost:5432/locust"

# engine = create_engine(db_connection_url)
# joined.to_postgis(name="swarm", con=engine)
