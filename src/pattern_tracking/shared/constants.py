WINDOW_NAME = 'Live template matching prototype'
"""Name of the window displayed to the user"""

POI_WIDTH, POI_HEIGHT = 25, 25
"""Number of pixels defining the width and height of the region of interest"""

DETECTION_THRESHOLD = 0.96
"""
When detecting a template in the current live feed,
if the detection is not at least above the given
number, then we should not apply a rectangle
"""

UPDATED = False
