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

# Subsampling factor for points cloud
SSFACTOR = 4

# Subbox size and grid resolution
box_size = 2000
resolution = 100 # 100 takes 20', 50 takes 80' (4 times more), 20 takes 345'

# Classification to consider
# https://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/nutzerinformationen.pdf
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
            filename = f"./lidar_data/3dm_32_{easting:03d}_{northing:04d}_1_nw.laz"
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
        x = las.x[::SSFACTOR]
        y = las.y[::SSFACTOR]
        z = las.z[::SSFACTOR]
        class_val = las.classification[::SSFACTOR]

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

    return x, y, zz

# Start timer
start_time = time.time()

bbox_min_x, bbox_min_y = latlon_to_utm(LAT_MIN, LON_MIN)
bbox_max_x, bbox_max_y = latlon_to_utm(LAT_MAX, LON_MAX)

x_edges = []
y_edges = []

x_edges = np.arange(bbox_min_x, bbox_max_x,  box_size)
x_edges = np.append(x_edges, bbox_max_x)

y_edges = np.arange(bbox_min_y, bbox_max_y,  box_size)
y_edges = np.append(y_edges, bbox_max_y)

x_len = len(x_edges)
y_len = len(y_edges)

print('x_len: %s, y_len: %s, number of boxes: %s'%(str(x_len), str(y_len), str((x_len-1)*(y_len-1))))

cols, rows = (x_len-1, y_len-1)

# Initialise 2D lists (which will contain arrays and not scalar, so 2D np array does not work here)
x_results = [[0 for i in range(cols)] for j in range(rows)]
y_results = [[0 for i in range(cols)] for j in range(rows)]
z_results = [[0 for i in range(cols)] for j in range(rows)]

# iterate on subboxes
for i in range(x_len - 1): # subboxes along x axis (longitude)
    for j in range(y_len - 1): # subboxes along y axis (latitude)

        laz_files = find_files(x_edges[i], x_edges[i+1], y_edges[j], y_edges[j+1])

        x_all, y_all, z_all = load_files(laz_files)

        x, y, zz = create_surface(x_edges[i], x_edges[i+1], y_edges[j], y_edges[j+1], resolution, x_all, y_all, z_all)

        x_results[i][j] = x # 1D array of x coordinates
        y_results[i][j] = y # 1D array of y coordinates
        z_results[i][j] = zz # 2D array of z elevations

# End timer and print execution time
end_time = time.time()
execution_time = end_time - start_time

print(f"Processed in {execution_time:.2f} seconds.")

with open('./xyz_pickles/x_results.pkl','wb') as f:
    pickle.dump(x_results, f)

with open('./xyz_pickles/y_results.pkl','wb') as f:
    pickle.dump(y_results, f)

with open('./xyz_pickles/z_results.pkl','wb') as f:
    pickle.dump(z_results, f)

print('done')

# TODO: subsampling. clean code