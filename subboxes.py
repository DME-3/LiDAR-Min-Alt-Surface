import utm
import numpy as np

def latlon_to_utm(lat, lon):
    # Convert lat/lon to UTM coordinates
    utm_x, utm_y, _, _ = utm.from_latlon(lat, lon)

    return utm_x, utm_y

def create_sub_boxes(lat_min, lat_max, lon_min, lon_max, box_size=1000):
    sub_boxes = []

    bbox_min_x, bbox_min_y = latlon_to_utm(lat_min, lon_min)
    bbox_max_x, bbox_max_y = latlon_to_utm(lat_max, lon_max)

    x_corners = []
    y_corners = []

    x_corners = np.arange(bbox_min_x, bbox_max_x,  box_size)
    x_corners = np.append(x_corners, bbox_max_x)

    y_corners = np.arange(bbox_min_y, bbox_max_y,  box_size)
    y_corners = np.append(y_corners, bbox_max_y)

    for x in x_corners:
        for y in y_corners:
            if end_box == False:
                min_x = x
                min_y = y
                end_box = True
            else:
                max_x = x
                max_y = y
                end_box = False
            


    return sub_boxes

lat_min, lat_max, lon_min, lon_max = 50.8634, 51.0923, 6.7004, 7.2049

sub_boxes = create_sub_boxes(lat_min, lat_max, lon_min, lon_max)

print(f"Number of sub boxes: {len(sub_boxes)}")

for sub_box in sub_boxes:
    print(sub_box)