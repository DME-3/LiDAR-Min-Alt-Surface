import os
import numpy as np
import pyproj
import laspy
import pickle

def find_surface(min_x, min_y, max_x, max_y, resolution = 10):
    # Convert the bounding box coordinates from WGS-84 to EPSG:25832
    wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')
    epsg25832 = pyproj.Proj(init='epsg:25832')
    min_x, min_y = pyproj.transform(wgs84, epsg25832, min_x, min_y)
    max_x, max_y = pyproj.transform(wgs84, epsg25832, max_x, max_y)

    # Determine the necessary .laz files based on the easting and northing coordinates
    min_easting = int(min_x) // 1000
    min_northing = int(min_y) // 1000
    max_easting = int(max_x) // 1000
    max_northing = int(max_y) // 1000

    laz_files = []
    for easting in range(min_easting, max_easting + 1):
        for northing in range(min_northing, max_northing + 1):
            filename = f"/Users/patatino/Dev_local/Python/lasersurface/lidar_data/3dm_32_{easting:03d}_{northing:04d}_1_nw.laz"
            laz_files.append(filename)

    # Initialize the surface array with the appropriate shape
    easting_range = (max_easting - min_easting) * 1000
    northing_range = (max_northing - min_northing) * 1000
    shape = (int(northing_range / resolution), int(easting_range / resolution))
    surface = np.zeros(shape)

    # Process each .laz file
    for filename in laz_files:
        print(filename)
        lasfile = laspy.read(filename)
        x = lasfile.x
        y = lasfile.y
        z = lasfile.z

        # Iterate through the points in the .laz file
        for i in range(len(x)):
            # Check if the point is within the bounding box
            if x[i] < min_x or x[i] > max_x or y[i] < min_y or y[i] > max_y:
                continue

            # Find the index of the point in the surface array
            easting_index = int((x[i] - min_x) / resolution)
            northing_index = int((y[i] - min_y) / resolution)

            # Update the surface array with the maximum altitude
            surface[northing_index, easting_index] = max(surface[northing_index, easting_index], z[i])

    return surface

# Define the bounding box coordinates in WGS-84
LAT_MIN, LAT_MAX = 50.935333, 50.942379
LON_MIN, LON_MAX = 6.956799, 6.967634
min_x, min_y, max_x, max_y = LON_MIN, LAT_MIN, LON_MAX, LAT_MAX

# Find the surface
surface = find_surface(min_x, min_y, max_x, max_y, resolution = 100)

print(surface)

with open('test.pkl','wb') as f:
    pickle.dump(surface, f)