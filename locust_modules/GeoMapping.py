import matplotlib.pyplot as plt
import pandas as pd
from geopy.geocoders import Nominatim
import geopandas as gpd
from arcgis.gis import GIS
from sqlalchemy import *


class Mapping:

    def __init__(self):

        self._locust_hub = None
        self._locust_layer = None

        self._location = None
        self._lat = None
        self._lon = None

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = location

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        self._lat = lat

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, lon):
        self._lon = lon

    @property
    def locust_hub(self):
        return self._locust_hub

    @locust_hub.setter
    def locust_hub(self, locust_hub):
        self._locust_hub = locust_hub

    @property
    def locust_layer(self):
        return self._locust_layer

    @locust_layer.setter
    def locust_layer(self, locust_layer):
        self._locust_layer = locust_layer

    def get_clean_lat_lon(self, coordinates):

        changed_text = coordinates.replace('[', "").replace(']', "").replace("\n", "")
        lat = changed_text.split(",")[0]
        lon = changed_text.split(",")[1]

        self.lat = lat
        self.lon = lon

    def lat_lon(self, location):

        geo_locator = Nominatim(user_agent="point_locust_modelling")
        geocoded_location = geo_locator.geocode(location)

        if geocoded_location is not None:
            self.lat = geocoded_location.latitude
            self.lon = geocoded_location.longitude
        else:
            print('Location not found')

    def get_nearest_village(self, coordinates):

        geo_locator = Nominatim(user_agent="point_locust_modelling")

        changed_text = coordinates.replace('[', "").replace(']', "").replace("\n", "")
        geocoded_location = str(geo_locator.geocode(changed_text)).split(",")

        if geocoded_location is not None:
            self.location = geocoded_location
        else:
            print('Location not found')

    def arcgis_online_locust_hub(self, config):

        """

        Args:
            config: file containing passwords

        Returns:
            Connection to ArcGIS Online - Locust HUB

        """

        locust_hub_gis = GIS(config['host'], config['user'], config['password'])
        self.locust_hub = locust_hub_gis

    def get_locust_layers(self, max_items=10, search_term="Locust"):
        """

        Args:
            max_items: max num records to fetch
            search_term: Term chose to select a specific set of layers

        Returns:
            List of layers
        """
        layers_found_4_term = self.locust_hub.content.search(search_term, max_items=max_items)

        return layers_found_4_term

    def get_locust_layer(self, max_items=10, search_term="Locust", item_term='Ramses Observations'):
        """

        Args:
            max_items: max num records to fetch
            search_term: Term chose to select a specific set of layers
            item_term: name of the layer

        Returns:
            Layer on AGIS Online containing the records from the field

        """

        locust_items = self.locust_hub.content.search(search_term, item_type="Feature Layer Collection",
                                                      max_items=max_items)

        for item in locust_items:
            name_item = item.name
            id_item = item.id
            if name_item == item_term:
                locust_item = self.locust_hub.content.get(id_item)

        locust_layer = locust_item.layers[0]

        self.locust_layer = locust_layer

    def get_fields_locust_layer(self):
        """

        Args:

        Returns:
            Fields of the layer containing RAMSES Observation

        """

        layer_fields = self.locust_layer.properties.fields

        return layer_fields

    def get_dataframe_locust_layer(self, filter_field='STARTDATE', filter_date=None):
        """
        Args:
            filter_date: data after which data will be selected
            filter_field: field to use for filtering
        Returns:
            geo-dataframe containing the selected records

        """
        query_literal = f"{filter_field} > '{filter_date}'"
        locust_filtered = self.locust_layer.query(where=query_literal)
        sdf_locust_filtered = locust_filtered.sdf

        df = pd.concat(
            [sdf_locust_filtered.drop(['SHAPE'], axis=1), sdf_locust_filtered['SHAPE'].apply(pd.Series)], axis=1)

        # df['STARTDATE'] = df['STARTDATE'].astype(str)
        # df['FINISHDATE'] = df['FINISHDATE'].astype(str)

        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
        # [['OBJECTID', 'STARTDATE', 'FINISHDATE', 'LOCNAME', 'CAT', 'COUNTRYID', 'x', 'y', 'geometry']]

        return gdf

        # return query_literal

    @staticmethod
    def plot_trajectories(landing_points, taking_off_points, trajectories):

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

        taking_off_points_gdf = gpd.read_file(landing_points)
        landing_points_gdf = gpd.read_file(taking_off_points)
        trajectories_gdf = gpd.read_file(trajectories)

        fig, ax = plt.subplots(figsize=(12, 8))
        taking_off_points_gdf.plot(ax=ax, c='green')
        landing_points_gdf.plot(ax=ax, c='red')
        trajectories_gdf.plot(ax=ax, cmap='Reds', alpha=0.5, linewidth=12)
        world.plot(ax=ax)

        plt.show()

    @staticmethod
    def shp_2_pg(root_table, taking_off_points, landing_points, trajectories):

        engine = create_engine('postgresql://postgres:antarone@localhost:5432/locust')

        taking_off_points_gdf = gpd.read_file(taking_off_points)
        landing_points_gdf = gpd.read_file(landing_points)
        trajectories_gdf = gpd.read_file(trajectories)

        taking_off_points_gdf.to_postgis('take_off', engine, if_exists='replace',
                                         schema='trajectories', index=True, index_label='Index')

        landing_points_gdf.to_postgis('landing', engine, if_exists='replace',
                                      schema='trajectories', index=True, index_label='Index')

        trajectories_gdf.to_postgis('trajectories', engine, if_exists='replace', schema='trajectories',
                                    index=True, index_label='Index')
