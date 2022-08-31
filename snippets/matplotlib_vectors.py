"""
DKRZ matplotlib script:  matplotlib_vectors.py

   - vectors on map plot
   - rectilinear grid (lat/lon)

   08.02.21  meier-fleischer(at)dkrz.de
"""
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import xarray as xr

# -- open netcdf file
ds = xr.open_dataset("../notebooks/export_28January2021.nc ")

fig , ax = plt.subplots(figsize=(9 , 6))

ax = plt.axes(projection=ccrs.PlateCarree())

ax.coastlines(resolution='50m' , linewidth=0.3 , color='black')

ax.gridlines(draw_labels=True , linewidth=0.5 , color='gray' ,
             xlocs=range(-180 , 180 , 30) , ylocs=range(-90 , 90 , 30))

ax.set_title('Wind velocity' , fontsize=10 , fontweight='bold')

ax.quiver(ds.longitude[::2] , ds.latitude[::2] , ds.u10[0 , ::2 , ::2] , ds.v10[0 , ::2 , ::2] ,
          transform=ccrs.PlateCarree())

plt.show()
# plt.savefig('plot_matplotlib_vector_rect.png' , bbox_inches='tight' , dpi=100)