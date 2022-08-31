from owslib.wms import WebMapService
wms = WebMapService('https://geospatial.jrc.ec.europa.eu/geoserver/copernicus/wms?', version='1.1.1')

print(wms.identification.type)
print(wms.identification.version)
print(wms.identification.title)
print(wms.identification.abstract)

for item in list(wms.contents):
    print(item)

print(wms['copernicus:GVI_S3A_EVI_20210311'].styles)
print(wms['copernicus:GVI_S3A_EVI_20210311'].boundingBox)
print(wms['copernicus:GVI_S3A_EVI_20210311'].boundingBoxWGS84)

# img = wms.getmap(layers=['copernicus:GVI_S3A_EVI_20210311'],
#                  styles=['GVI'],
#                  srs='EPSG:4326',
#                  bbox=(-17.99553571429349, -5.004464285710448, 60.004464285702745, 37.99553571428749),
#                  size=(300, 250),
#                  format='image/jpeg',
#                  transparent=True)
#
# out = open('GVI_S3A_EVI_20210311.jpg', 'wb')
# out.write(img.read())
# out.close()

