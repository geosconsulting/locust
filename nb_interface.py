import modules as md

# Loading coastlines from Cartopy
coastline = md.gf.coastline(line_width=2 , line_color='k').opts(projection=md.ccrs.PlateCarree() , scale='10m')

date_analysis = md.widgets.DatePicker(
        description='Pick a Date' ,
        disabled=False ,
)

altitude_analysis = md.widgets.Dropdown(
        description='Model elevation' ,
        disabled=False ,
)

cumulation_period = md.widgets.Dropdown(
        description='Cumulation Period' ,
        options=['precip_1d' , 'precip_3d' , 'precip_7d'] ,
        value='precip_3d' ,
        disabled=False ,
)

mapping_colors = md.widgets.Dropdown(
        description='Palette' ,
        options=['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
                 'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'] ,
        value='RdBu' ,
        disabled=False ,
)

wms_layers = md.WebMapService('https://geospatial.jrc.ec.europa.eu/geoserver/copernicus/wms', version='1.1.1')
wms_layers_chooser = md.widgets.Dropdown(
        description='Layers' ,
        options=list(wms_layers.contents) ,
        value=list(wms_layers.contents)[0] ,
        disabled=False ,
)


def select_variables(ds):
    list_variables = []

    for temp in ds:
        list_variables.append(temp)

    variables = md.widgets.Dropdown(
            options=list_variables ,
            description='Variable:' ,
            disabled=False ,
    )

    return variables


def select_dates(ds):
    date_list = []
    for i in range(len(ds.valid_time)):
        date_list.append(ds.coords['valid_time'][i].values)

    dates_available = md.widgets.Dropdown(
            options=date_list ,
            description='Dates:' ,
            disabled=False ,
    )
    return dates_available


def filter_values(ds , chosen_val):
    min_val = ds[chosen_val].min()
    max_val = ds[chosen_val].max()

    sel_min = min_val + 20
    sel_max = max_val - 20

    sub_sel = md.widgets.IntRangeSlider(
            value=[sel_min , sel_max] ,
            min=min_val ,
            max=max_val ,
            step=10 ,
            description='Test:' ,
            disabled=False ,
            continuous_update=False ,
            orientation='horizontal' ,
            readout=True
    )
    return sub_sel


def clip_cube(ds_tot):
    min_lon = 25.0  # lower left longitude
    min_lat = 20.50  # lower left latitude
    max_lon = 60.10  # upper right longitude
    max_lat = -10.0  # upper right latitude

    # Defining the boundaries
    lon_bnds = [min_lon , max_lon]
    lat_bnds = [min_lat , max_lat]

    # Performing the reduction
    ds_tot_clip = ds_tot.sel(latitude=slice(*lat_bnds) , longitude=slice(*lon_bnds))

    # Resampling using the slice method
    resample_1 = ds_tot_clip.isel(longitude=slice(None , None , 7) , latitude=slice(None , None , 7))

    # Convert current u and v to magnitude and angle
    mag = md.np.sqrt(resample_1.u10 ** 2 + resample_1.v10 ** 2)
    angle = (md.np.pi / 2.) - md.np.arctan2(resample_1.u10 / mag , resample_1.v10 / mag)

    resample_1["mag"] = (['valid_time' , 'latitude' , 'longitude'] , mag)
    resample_1["angle"] = (['valid_time' , 'latitude' , 'longitude'] , angle)

    # Convert current u and v to magnitude and angle
    mag_100 = md.np.sqrt(resample_1.u100 ** 2 + resample_1.v100 ** 2)
    angle_100 = (md.np.pi / 2.) - md.np.arctan2(resample_1.u100 / mag , resample_1.v100 / mag)

    resample_1["mag_100"] = (['valid_time' , 'latitude' , 'longitude'] , mag_100)
    resample_1["angle_100"] = (['valid_time' , 'latitude' , 'longitude'] , angle_100)

    # Specify the dataset, its coordinates and requested variable
    dataset = md.gv.Dataset(resample_1 , ['longitude' , 'latitude' , 'valid_time'] , 'mag' , crs=md.ccrs.PlateCarree())
    images = dataset.to(md.gv.Image , dynamic=True)

    # Specify the dataset, its coordinates and requested variable
    dataset_100 = md.gv.Dataset(resample_1 , ['longitude' , 'latitude' , 'valid_time'] , 'mag_100' ,
                                crs=md.ccrs.PlateCarree())
    images_100 = dataset_100.to(md.gv.Image , dynamic=True)

    # x and y 1d coordinates
    lat_m = resample_1.latitude
    lon_m = resample_1.longitude

    # Number of time step (4 based on the groupby approach 2W)
    nb = resample_1.angle.shape[0]
    nb_100 = resample_1.angle_100.shape[0]

    # We will normalise the arrow to avoid changes in scale as the
    # time evolve...
    max_mag = resample_1.mag.max()
    max_mag_100 = resample_1.mag_100.max()

    # Create a disctionary of VectorField values at each time interval
    a_var = resample_1.valid_time.values
    y_list = []
    for i in range(nb):
        y_list.append(md.gv.VectorField((lon_m ,
                                         lat_m ,
                                         resample_1.angle[i , : , :] ,
                                         resample_1.mag[i , : , :] / max_mag) ,
                                        crs=md.ccrs.PlateCarree()))
    dict_y = {a_var[i]: y_list[i] for i in range(nb)}

    # Create a disctionary of VectorField values at each time interval
    y_list_100 = []
    for i in range(nb):
        y_list_100.append(md.gv.VectorField((lon_m ,
                                             lat_m ,
                                             resample_1.angle_100[i , : , :] ,
                                             resample_1.mag_100[i , : , :] / max_mag_100) ,
                                            crs=md.ccrs.PlateCarree()))
    dict_y_100 = {a_var[i]: y_list_100[i] for i in range(nb_100)}

    diff_tp = resample_1['tp_mm'].interactive.sel(valid_time=md.pnw.DiscreteSlider)
    interactive_tp = diff_tp.hvplot(cmap='Blues' ,
                                    clim=(resample_1['tp_mm'].min() , resample_1['tp_mm'].max()) ,
                                    coastline=True ,
                                    width=640 ,
                                    height=480)

    diff_t2m = resample_1['t2m'].interactive.sel(valid_time=md.pnw.DiscreteSlider)
    interactive_t2m = diff_t2m.hvplot(cmap='Reds' ,
                                      clim=(resample_1['t2m'].min() , resample_1['t2m'].max()) ,
                                      coastline=True ,
                                      width=640 ,
                                      height=480)

    hmap = md.hv.HoloMap(dict_y , kdims="valid_time").opts(md.opts.VectorField(magnitude=md.dim('Magnitude') * 4.5 ,
                                                                               color='b' ,
                                                                               pivot='tip' ,
                                                                               line_width=0.75 ,
                                                                               rescale_lengths=True ,
                                                                               projection=md.ccrs.PlateCarree()
                                                                               )
                                                           )

    hmap_100 = md.hv.HoloMap(dict_y_100 , kdims="valid_time").opts(
        md.opts.VectorField(magnitude=md.dim('Magnitude') * 4.5 ,
                            color='b' ,
                            pivot='tip' ,
                            line_width=0.75 ,
                            rescale_lengths=True ,
                            projection=md.ccrs.PlateCarree()
                            )
        )

    return coastline , images , images_100 , hmap , hmap_100 , interactive_tp , interactive_t2m


def generate_dashboard(ds_tot , coastline , images , images_100 , hmap , hmap_100 , interactive_tp , interactive_t2m):
    dashboard = md.pn.Column(
            md.pn.panel("# ECMWF Forecasts" , width=800 , height=40) ,
            md.pn.Row(
                    md.pn.Column(
                            md.pn.panel("### Parameter : {}".format(ds_tot['tp'].attrs['long_name'])) ,
                            interactive_tp.widgets() ,
                            interactive_tp.panel() ,
                    ) ,
                    md.pn.Column(
                            md.pn.panel("### Parameter : {}".format('Wind magnitude + Wind direction at 10 metres')) ,
                            images.opts(active_tools=['wheel_zoom' , 'pan'] , cmap=md.plt.cm.Reds , colorbar=True ,
                                        width=800 , height=600) * coastline * hmap
                    )
            ) ,
            md.pn.Row(
                    md.pn.Column(
                            md.pn.panel("### Parameter : {}".format(ds_tot['t2m'].attrs['long_name'])) ,
                            interactive_t2m.widgets() ,
                            interactive_t2m.panel() ,
                    ) ,
                    md.pn.Column(
                            md.pn.panel("### Parameter : {}".format('Wind magnitude + Wind direction at 100 metres')) ,
                            images_100.opts(active_tools=['wheel_zoom' , 'pan'] , cmap=md.plt.cm.Reds , colorbar=True ,
                                            width=800 , height=600) * coastline * hmap_100
                    )
            ) ,
    ).servable()

    return dashboard


def get_servir_precipitation(date_str , cumulation_period):

    date_analysis_from_interface = md.datetime.strptime(date_str , '%Y-%m-%d')

    start_date = (date_analysis_from_interface - md.timedelta(days=8)).strftime("%Y/%m/%d")
    end_date = (date_analysis_from_interface + md.timedelta(days=5)).strftime("%Y/%m/%d")

    url_gpm = "https://pmmpublisher.pps.eosdis.nasa.gov/opensearch?" \
              "q=" + cumulation_period + "&lat=0&lon=5&limit=10" \
                                         "&startTime=" + start_date + "&endTime=" + end_date

    response_gpm = md.requests.request("GET" , url_gpm)

    df = md.pd.DataFrame.from_records(response_gpm.json()['items'])

    return df , start_date , end_date , response_gpm


def plot_servir_precipitation(response_gpm , index_servir , lat, lon, start_date):
    # response_gpm.json()['items'][0]['@id']

    url_tiff = response_gpm.json()['items'][index_servir]['action'][1]['using'][1]['url']
    url_geojson = response_gpm.json()['items'][index_servir]['action'][5]['using'][0]['url']
    styles = md.requests.get(response_gpm.json()['items'][index_servir]['action'][2]['using'][1]['url']).json()

    def style_function(feature):
        prec_level = feature['properties']['precip']
        string_search = '{{{base}}}=={level}'.format(base='precip' , level=prec_level)
        #     print(styles.get(string_search))
        return {
            "fillOpacity": styles.get(string_search)['fillOpacity'] ,
            "weight"     : styles.get(string_search)['weight'] ,
            "fillColor"  : "#white" if prec_level is None else styles.get(string_search)['color']
            # colorscale(prec_level),
        }

    m = md.folium.Map(
            location=[10 , 10] ,
            tiles="cartodbpositron" ,
            zoom_start=5 ,
    )

    md.folium.GeoJson(url_geojson ,
                      name="IMERG cumulated precipitation" ,
                      style_function=style_function ,
                      popup=md.folium.GeoJsonPopup(fields=['precip'])
                      ).add_to(m)

    md.folium.LayerControl().add_to(m)

    md.folium.Marker([lon, lat] , popup=start_date).add_to(m)

    lat_interval = 10
    lon_interval = 10

    for lat in range(-90 , 91 , lat_interval):
        md.folium.PolyLine([[lat , -180] , [lat , 180]] , weight=0.5).add_to(m)

    for lon in range(-180 , 181 , lon_interval):
        md.folium.PolyLine([[-90 , lon] , [90 , lon]] , weight=0.5).add_to(m)

    return m


def processing_wind(ds_tot):

    min_lon = 25.0  # lower left longitude
    min_lat = 20.50  # lower left latitude
    max_lon = 60.10  # upper right longitude
    max_lat = -10.0  # upper right latitude

    # Defining the boundaries
    lon_bnds = [min_lon , max_lon]
    lat_bnds = [min_lat , max_lat]

    # Performing the reduction
    ds_tot_clip = ds_tot.sel(latitude=slice(*lat_bnds) , longitude=slice(*lon_bnds))

    # Resampling using the slice method
    resample_1 = ds_tot_clip.isel(longitude=slice(None , None , 7) , latitude=slice(None , None , 7))

    # Convert current u and v to magnitude and angle
    mag = md.np.sqrt(resample_1.u10 ** 2 + resample_1.v10 ** 2)
    angle = (md.np.pi / 2.) - md.np.arctan2(resample_1.u10 / mag , resample_1.v10 / mag)

    resample_1["mag"] = (['valid_time' , 'latitude' , 'longitude'] , mag)
    resample_1["angle"] = (['valid_time' , 'latitude' , 'longitude'] , angle)

    # Convert current u and v to magnitude and angle
    mag_100 = md.np.sqrt(resample_1.u100 ** 2 + resample_1.v100 ** 2)
    angle_100 = (md.np.pi / 2.) - md.np.arctan2(resample_1.u100 / mag , resample_1.v100 / mag)

    resample_1["mag_100"] = (['valid_time' , 'latitude' , 'longitude'] , mag_100)
    resample_1["angle_100"] = (['valid_time' , 'latitude' , 'longitude'] , angle_100)

    # Specify the dataset, its coordinates and requested variable
    dataset = md.gv.Dataset(resample_1 , ['longitude' , 'latitude' , 'valid_time'] , 'mag' , crs=md.ccrs.PlateCarree())
    images = dataset.to(md.gv.Image , dynamic=True)

    # Specify the dataset, its coordinates and requested variable
    dataset_100 = md.gv.Dataset(resample_1 , ['longitude' , 'latitude' , 'valid_time'] , 'mag_100' ,
                                crs=md.ccrs.PlateCarree())
    images_100 = dataset_100.to(md.gv.Image , dynamic=True)

    # x and y 1d coordinates
    lat_m = resample_1.latitude
    lon_m = resample_1.longitude

    # Number of time step (4 based on the groupby approach 2W)
    nb = resample_1.angle.shape[0]
    nb_100 = resample_1.angle_100.shape[0]

    # We will normalise the arrow to avoid changes in scale as the
    # time evolve...
    max_mag = resample_1.mag.max()
    max_mag_100 = resample_1.mag_100.max()

    # Create a disctionary of VectorField values at each time interval
    a_var = resample_1.valid_time.values
    y_list = []
    for i in range(nb):
        y_list.append(md.gv.VectorField((lon_m ,
                                         lat_m ,
                                         resample_1.angle[i , : , :] ,
                                         resample_1.mag[i , : , :] / max_mag) ,
                                        crs=md.ccrs.PlateCarree()))
    dict_y = {a_var[i]: y_list[i] for i in range(nb)}

    # Create a dictionary of VectorField values at each time interval
    y_list_100 = []
    for i in range(nb):
        y_list_100.append(md.gv.VectorField((lon_m ,
                                             lat_m ,
                                             resample_1.angle_100[i , : , :] ,
                                             resample_1.mag_100[i , : , :] / max_mag_100) ,
                                            crs=md.ccrs.PlateCarree()))
    dict_y_100 = {a_var[i]: y_list_100[i] for i in range(nb_100)}

    hmap = md.hv.HoloMap(dict_y , kdims="valid_time").opts(md.opts.VectorField(magnitude=md.dim('Magnitude') * 4.5 ,
                                                                               color='b' ,
                                                                               pivot='tip' ,
                                                                               line_width=0.75 ,
                                                                               rescale_lengths=True ,
                                                                               projection=md.ccrs.PlateCarree() ,
                                                                               width=1500 , height=750
                                                                               )
                                                           )

    hmap_100 = md.hv.HoloMap(dict_y_100 , kdims="valid_time").opts(
        md.opts.VectorField(magnitude=md.dim('Magnitude') * 4.5 ,
                            color='b' ,
                            pivot='tip' ,
                            line_width=0.75 ,
                            rescale_lengths=True ,
                            projection=md.ccrs.PlateCarree()
                            )
        )

    return images , images_100 , hmap , hmap_100






