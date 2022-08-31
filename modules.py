import datetime
import glob
import xarray as xr
import re
import os
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image
from io import BytesIO
from IPython.display import Image as showim
import IPython.display as Disp
import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeat
# import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cmocean
import folium
from folium.plugins import Draw
import branca
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling
import holoviews as hv
from holoviews import opts, dim
import hvplot
import hvplot.pandas  # noqa
import hvplot.xarray  # noqa
import panel as pn
import panel.widgets as pnw
import geoviews as gv
import geoviews.feature as gf

gv.extension('bokeh', 'matplotlib')

import ipywidgets as widgets
from ipyfilechooser import FileChooser
from ipyleaflet import Map, GeoData, WMSLayer, basemaps, FullScreenControl, Marker
from ipyleaflet import DrawControl, LayersControl, GeoJSON, basemaps, WidgetControl
from ipyleaflet.velocity import Velocity
from importlib import reload
from tqdm.notebook import tqdm
import qgrid
from datetime import datetime, timedelta
import shapefile as shp  # Requires the pyshp package
import geoplot as gplt
import geoplot.crs as gcrs
from owslib.wms import WebMapService


# import zarr
# import boto3
# import botocore

import warnings
from IPython.display import display, HTML

warnings.filterwarnings('ignore')
display(HTML("<style>.container { width:90% !important; }</style>"))

