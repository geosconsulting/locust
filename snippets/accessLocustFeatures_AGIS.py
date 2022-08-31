from arcgis.gis import GIS
import pandas as pd
import matplotlib.pyplot as plt

gis = GIS(url='https://hqfao.maps.arcgis.com', username='fabio.lana_hqfao', password='2019_Famews_0')

locust_items = gis.content.search("Locust", item_type="Feature Layer", max_items=5)
swarm_items = gis.content.search("Swarms", item_type="Feature Layer", max_items=5)

swarm_layers = swarm_items[1].layers
swarm_layer = swarm_layers[0]

print(swarm_layer.properties.drawingInfo.renderer.type)
print(swarm_layer.properties.capabilities)

swarm_layer_filtered = swarm_layer.query(where="STARTDATE > '2020-06-15'")
print(len(swarm_layer_filtered.features))

sdf_swarms = swarm_layer_filtered.sdf
sdf_swarms['SHAPE'].head()

print(swarm_layer_filtered.features[0].geometry)
print(swarm_layer_filtered.features[0].attributes)

layer_locust = None
for item in locust_items:
    nome_item = item.name
    if nome_item == 'LocustCore_Master':
        layer_locust = item

for fl in layer_locust:
    print(fl)

flayers = layer_locust.layers
flayer = flayers[0]
print(flayer)

sdf = flayer.query(where="STARTDATE > '2020-05-05'").sdf

print(sdf.columns)

sdf.groupby(by="COUNTRYID")["OBJECTID"].count()
plt.bar(sdf.COUNTRYID, sdf.AREAHA)
plt.show()
