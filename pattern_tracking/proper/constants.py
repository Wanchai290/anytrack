# -- Constants
# Name of the window displayed to the user
WINDOW_NAME = 'Live template matching prototype'

# Number of pixels defining the width and height
# of the region of interest
POI_WIDTH, POI_HEIGHT = 50, 50

# When detecting a template in the current live feed,
# if the detection is not at least above the given
# number, then we should not apply a rectangle
DETECTION_THRESHOLD = 0.91
