import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import utm
import geojsoncontour

# Define conversion functions
def utm_to_latlon(x, y):
    # Convert lat/lon to UTM coordinates
    lat, lon = utm.to_latlon(x, y, 32, 'U')

    return lat, lon

# Define conversion functions
def latlon_to_utm(lat, lon):
    # Convert lat/lon to UTM coordinates
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return utm_x, utm_y

def transform_geojson_to_wgs84(geojson_str):
    # Parse the GeoJSON string into a Python dictionary
    geojson = json.loads(geojson_str)
    
    # Transform each coordinate in the GeoJSON object from UTM zone 32N to WGS84
    for feature in geojson['features']:
        if feature['geometry']['type'] == 'Polygon':
            for i in range(len(feature['geometry']['coordinates'])):
                for j in range(len(feature['geometry']['coordinates'][i])):
                    x, y = feature['geometry']['coordinates'][i][j]
                    lat, lon = utm.to_latlon(x, y, 32, 'N')
                    feature['geometry']['coordinates'][i][j] = [lon, lat]
        elif feature['geometry']['type'] == 'MultiPolygon':
            for i in range(len(feature['geometry']['coordinates'])):
                for j in range(len(feature['geometry']['coordinates'][i])):
                    for k in range(len(feature['geometry']['coordinates'][i][j])):
                        x, y = feature['geometry']['coordinates'][i][j][k]
                        lat, lon = utm.to_latlon(x, y, 32, 'N')
                        feature['geometry']['coordinates'][i][j][k] = [lon, lat]
        elif feature['geometry']['type'] == 'LineString':
            for i in range(len(feature['geometry']['coordinates'])):
                x, y = feature['geometry']['coordinates'][i]
                lat, lon = utm.to_latlon(x, y, 32, 'N')
                feature['geometry']['coordinates'][i] = [lon, lat]
    
    # Convert the Python dictionary back to a GeoJSON string
    transformed_geojson_str = json.dumps(geojson)
    
    # Return the transformed GeoJSON string
    return transformed_geojson_str



with open('x_results.pkl','rb') as f:
    x_results = pickle.load(f)

with open('y_results.pkl','rb') as f:
    y_results = pickle.load(f)

with open('z_results.pkl','rb') as f:
    z_results = pickle.load(f)

x_array = np.array([])

for i in range(len(x_results)):
  x_array = np.concatenate((x_array, x_results[i][0]))

y_array = np.array([])

for j in range(len(y_results)):
  y_array = np.concatenate((y_array, y_results[0][j]))

lst = z_results

row=len(lst)
col=len(lst[0])

for j in range(0, row):
  print('j=%s'%(j))
  for i in range(0, col):
    print('i=%s'%(i))
    print(z_results[i][j].shape)
    if i==0:
      z_array_row = z_results[0][j]
    else:
      z_array_row = np.hstack((z_array_row, z_results[i][j]))
  
  if j==0:
    z_array = z_array_row
  else:
    z_array = np.vstack((z_array, z_array_row))

z_array_ft = z_array / 0.3048 + 1000

levels=np.arange(1200,2200,100)

fig = plt.figure(figsize =(2, 2))
ax = fig.add_subplot(111)

contour = ax.contour(x_array, y_array, z_array_ft, cmap = 'jet', levels=levels)

geojson = geojsoncontour.contour_to_geojson(
    contourf=contour,
    ndigits=3,
    unit='ft'
)

wgs84_geojson = transform_geojson_to_wgs84(geojson)

with open('contour_geojson.json', 'w') as file:
    file.write(wgs84_geojson)



fig = plt.figure(figsize =(2, 2))
ax = fig.add_subplot(111)
contourf = ax.contourf(x_array, y_array, z_array_ft, cmap = 'jet', levels=levels)

geojsonf = geojsoncontour.contourf_to_geojson(
    contourf=contourf,
    ndigits=3,
    unit='ft'
)

wgs84_geojsonf = transform_geojson_to_wgs84(geojsonf)

with open('contourf_geojsonf.json', 'w') as file:
    file.write(wgs84_geojsonf)

