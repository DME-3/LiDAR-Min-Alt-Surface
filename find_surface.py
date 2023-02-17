import os
import numpy as np
import laspy
import utm
import pyproj
import time
import sys
from tqdm import tqdm

# Define the bounding box coordinates in WGS-84
LAT_MIN, LAT_MAX = 50.896393, 50.967115
LON_MIN, LON_MAX = 6.919968, 7.005756

LAT_MIN, LAT_MAX = 50.935333, 50.942379
LON_MIN, LON_MAX = 6.956799, 6.967634

# Minimum Z to consider
Z_MIN = 50

# Classification to consider
lastReturnNichtBoden = 20
brueckenpunkte = 17
class_ok = [brueckenpunkte, lastReturnNichtBoden]

# Radius in meters
radius = 600

# Define conversion functions
def latlon_to_utm(lat, lon):
    # Convert lat/lon to UTM coordinates
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return utm_x, utm_y

def find_files(lat_min, lat_max, lon_min, lon_max):
   
    bbox_min_x, bbox_min_y = latlon_to_utm(lat_min, lon_min)
    bbox_min_x = bbox_min_x - radius
    bbox_min_y = bbox_min_y - radius

    bbox_max_x, bbox_max_y = latlon_to_utm(lat_max, lon_max)
    bbox_max_x = bbox_max_x + radius
    bbox_max_y = bbox_max_y + radius

    # Determine the necessary .laz files based on the easting and northing coordinates
    min_easting = int(bbox_min_x) // 1000
    min_northing = int(bbox_min_y) // 1000
    max_easting = int(bbox_max_x) // 1000
    max_northing = int(bbox_max_y) // 1000

    laz_files = []

    for easting in range(min_easting, max_easting + 1):
        for northing in range(min_northing, max_northing + 1):
            filename = f"/Users/patatino/Dev_local/Python/lasersurface/lidar_data/3dm_32_{easting:03d}_{northing:04d}_1_nw.laz"
            laz_files.append(filename)

    return laz_files

def load_files(laz_files):

    # Initialize empty arrays for point coordinates and elevations
    x_all = np.array([])
    y_all = np.array([])
    z_all = np.array([])

    for file in tqdm(laz_files):
        las = laspy.read(file)
        print('processing %s'%(file))
        x = las.x
        y = las.y
        z = las.z
        class_val = las.classification

        mask = (np.isin(class_val, class_ok))&(z>=Z_MIN)

        # Stack point coordinates and elevations
        x_all = np.hstack((x_all, x[mask]))
        y_all = np.hstack((y_all, y[mask]))
        z_all = np.hstack((z_all, z[mask]))

        print(sys.getsizeof(x_all))

        #laspy.LasReader.close(las)
    
    return x_all, y_all, z_all

def find_z(x_all, y_all, z_all, x, y):

    # Calculate distance from input point
    distance = np.sqrt((x_all - x)**2 + (y_all - y)**2)

    # Find highest elevation within search radius
    in_radius = distance <= radius
    z_max = np.max(z_all[in_radius])

    return z_max

def create_surface(lat_min, lat_max, lon_min, lon_max, resolution, x_all, y_all, z_all):
    # Define UTM zone and hemisphere letter
    zone_num = 32
    zone_let = 'U'

    # Convert bounding box limits to UTM coordinates
    x_min, y_min = utm.from_latlon(lat_min, lon_min, zone_num, zone_let)[:2]
    x_max, y_max = utm.from_latlon(lat_max, lon_max, zone_num, zone_let)[:2]

    # Create 1D arrays of X and Y coordinates
    x = np.arange(x_min, x_max, resolution)
    y = np.arange(y_min, y_max, resolution)

    # Create 2D arrays of X and Y coordinates
    xx, yy = np.meshgrid(x, y)

    # Calculate Z values using user-defined function find_z(x, y)
    zz = np.zeros_like(xx)
    for i in tqdm(range(xx.shape[0])):
        for j in range(xx.shape[1]):
            zz[i, j] = find_z(x_all, y_all, z_all, xx[i, j], yy[i, j])

    return xx, yy, zz

laz_files = find_files(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX)
print('The bounding box corresponds to %s files in total'%(len(laz_files)))

print('loading files...')

# Start timer
start_time = time.time()

x_all, y_all, z_all = load_files(laz_files)

# End timer and print execution time
end_time = time.time()
execution_time = end_time - start_time

print('loading finished')

print(f"Execution time: {execution_time:.2f} seconds")

xx, yy, zz = create_surface(LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, 10, x_all, y_all, z_all)

print('done')