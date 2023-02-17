import numpy as np
import laspy
import utm
import time
import pickle
from tqdm import tqdm

LAT_MIN, LAT_MAX = 50.935333, 50.942379
LON_MIN, LON_MAX = 6.956799, 6.967634

# Define the bounding box coordinates in WGS-84
LAT_MIN, LAT_MAX = 50.896393, 50.967115
LON_MIN, LON_MAX = 6.919968, 7.005756

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

def find_files(bbox_min_x, bbox_max_x, bbox_min_y, bbox_max_y):
       
    bbox_min_x = bbox_min_x - radius
    bbox_min_y = bbox_min_y - radius

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

    for file in laz_files:
        las = laspy.read(file)
        #print('processing %s'%(file))
        x = las.x
        y = las.y
        z = las.z
        class_val = las.classification

        mask = (np.isin(class_val, class_ok))&(z>=Z_MIN)

        # Stack point coordinates and elevations
        x_all = np.hstack((x_all, x[mask]))
        y_all = np.hstack((y_all, y[mask]))
        z_all = np.hstack((z_all, z[mask]))
    
    return x_all, y_all, z_all

def find_z(x_all, y_all, z_all, x, y):

    # Calculate distance from input point
    distance = np.sqrt((x_all - x)**2 + (y_all - y)**2)

    # Find highest elevation within search radius
    in_radius = distance <= radius
    z_max = np.max(z_all[in_radius])

    return z_max

def create_surface(x_min, x_max, y_min, y_max, resolution, x_all, y_all, z_all):

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

bbox_min_x, bbox_min_y = latlon_to_utm(LAT_MIN, LON_MIN)
bbox_max_x, bbox_max_y = latlon_to_utm(LAT_MAX, LON_MAX)

x_edges = []
y_edges = []

box_size=2000
resolution = 50

x_edges = np.arange(bbox_min_x, bbox_max_x,  box_size)
x_edges = np.append(x_edges, bbox_max_x)

y_edges = np.arange(bbox_min_y, bbox_max_y,  box_size)
y_edges = np.append(y_edges, bbox_max_y)

x_len = len(x_edges)
y_len = len(y_edges)

print('x_len: %s, y_len: %s, number of boxes: %s'%(str(x_len), str(y_len), str((x_len-1)*(y_len-1))))

xx_result = []
yy_result = []
zz_result = []

for i in tqdm(range(x_len - 1)):
    for j in tqdm(range(y_len - 1)):

        laz_files = find_files(x_edges[i], x_edges[i+1], y_edges[j], y_edges[j+1])

        #print('Current bounding box corresponds to %s files in total'%(len(laz_files)))
        print('Loading files...')

        # Start timer
        start_time = time.time()

        x_all, y_all, z_all = load_files(laz_files)

        # End timer and print execution time
        end_time = time.time()
        execution_time = end_time - start_time

        #print('loading finished')

        print(f"Loaded files in {execution_time:.2f} seconds. Finding elevations...")

        xx, yy, zz = create_surface(x_edges[i], x_edges[i+1], y_edges[j], y_edges[j+1], resolution, x_all, y_all, z_all)

        xx_result.append(xx)
        yy_result.append(yy)
        zz_result.append(zz)

with open('xx.pkl','wb') as f:
    pickle.dump(xx_result, f)

with open('yy.pkl','wb') as f:
    pickle.dump(yy_result, f)

with open('zz.pkl','wb') as f:
    pickle.dump(zz_result, f)

print('done')