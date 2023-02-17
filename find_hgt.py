import os
import numpy as np
import laspy
import utm
import pyproj
import time

# Colonius
input_lat = 50.946944444
input_lon = 6.931944444

# Unicenter
input_lat = 50.921800459
input_lon = 6.932576158

# Koeln Triangle
input_lat = 50.940305556
input_lon = 6.971777778

# Dom
input_lat = 50.941520367
input_lon = 6.957295594

# Koeln Triangle
input_lat = 50.940305556
input_lon = 6.971777778

# Define conversion functions
def latlon_to_utm(lat, lon):
    # Convert lat/lon to UTM coordinates
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return utm_x, utm_y

# Start timer
start_time = time.time()

# Convert input lat/lon to UTM
input_utm_x, input_utm_y = latlon_to_utm(input_lat, input_lon)

# Define search radius and find bounding box
search_radius = 600
min_x = input_utm_x - search_radius
max_x = input_utm_x + search_radius
min_y = input_utm_y - search_radius
max_y = input_utm_y + search_radius

idx_min_x = int(min_x // 1000)
idx_max_x = int(max_x // 1000)
idx_min_y = int(min_y // 1000)
idx_max_y = int(max_y // 1000)

# Iterate through all .laz files in folder and open only those within bounding box
highest_elevation = -float("inf")
for filename in os.listdir("lidar_data"):
    if filename.endswith(".laz"):
        min_laz_x = int(filename.split("_")[2]) * 1000
        min_laz_y = int(filename.split("_")[3]) * 1000
        max_laz_x = min_laz_x + 999.9
        max_laz_y = min_laz_y + 999.9

        if (max_laz_x >= min_x and min_laz_x <= max_x) and (max_laz_y >= min_y and min_laz_y <= max_y):
            # Open .laz file and extract elevation data
            las = laspy.read('lidar_data/' + filename)
            print('processing %s'%(filename))
            x = las.x
            y = las.y
            z = las.z
            class_val = las.classification
            
            # Calculate distance from input point
            distance = np.sqrt((x - input_utm_x)**2 + (y - input_utm_y)**2)
            
            # Find highest elevation within search radius with classification 20
            # https://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/nutzerinformationen.pdf
            in_radius = (distance <= search_radius) & (class_val == 20)
            max_elevation = np.max(z[in_radius])

            if max_elevation > highest_elevation:
                highest_elevation = max_elevation

# Print result
print(f"Highest elevation in {search_radius}m radius around ({input_lat}, {input_lon}): {highest_elevation:.2f}m above geoid")

# End timer and print execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds")

# TODO next: open all files for the bounding bo (with margins), read x, y, z with class 20, stack them horizontally, and process the whole sets
