# Anytrack - User manual

This small guide gives an overview of the functionalities
in this application. Refer to this guide for any question on how
it works. If you are looking for the development 
technical guide, please see [here](./DEV_MANUAL.md) 

# Table of contents
- Loading a video feed
	- From a video file
	- Using a connected camera
	- From a custom external server
- Tracker management
	- Creating a new tracker
	- Tracker types
	- Defining a detection region
	- Switch to a specific tracker
- Plotting tracker data

# Loading a video feed
## From a video file
The application supports loading a video file to use as reference. On the main
window, click on the "Video" tab in the top-left, then on "Launch from video".
It should support the most common video formats that are used everyday. The
".avi" extension has been tested and works properly.
The video files management comes from the library OpenCV, so any format that
works with it should work with the app.

## Using a connected camera
You can use an integrated webcam or USB camera to get the video feed. For now,
there is no selection of the video input possible. If you have multiple cameras
and/or webcams, you must disable the ones you do not want to use.

From the "Video" tab, click on "Use live camera feed" and the application will
search for the first valid video input it finds. Please note that if another
software has control of the video input, the application will no tbe able to use
it. Most of the time, when an application uses a video device, it gains
exclusive control of the device and the video feed captured. So you need to
close all the programs that might take control of your camera.

## From a custom external server
A small custom system has been designed to allow the application to receive
video data. The setup is a little complicated and will not be covered in this
guide. Please refer to the [the following file](../custom_integrations/tixier_mita_lab/README.md).
It is a step by step explanation on how to setup an external device (in this
case a RaspberryPi) to serve as a video feed provider for a computer, over
a direct Ethernet connection.

# Tracker management
## Creating a new tracker
To create a new tracker, click on the "Tracker" tab in the top-left corner, and
click on "New tracker". In the pop-up that appears, you can give a convenient
name for the created tracker, and select its type. The name has no influence on
the tracker and how it works. You can choose which type of algorithm the tracker must use :

- Template Tracker  
OpenCV's implementation of the Normalized Cross-Correlation algorithm for template matching.
Read more about its implementation [here](https://docs.opencv.org/4.x/df/dfb/group__imgproc__object.html#gga3a7850640f1fe1f58fe91a2d7583695dac6677e2af5e0fae82cc5339bfaef5038)


- KCF Tracker  
OpenCV's implementation of Kernelized Correlation Filters.


- Fixed point  
Not a real tracker, will just act as a fixed point. Useful for distance measurements.

After clicking "OK", left-click anywhere on the current video loaded and a white square 
will appear around the clicked region. The white squared region will update on every frame and represents
the closest region matching your input. All trackers created are independent

## Defining a detection region
If you have at least one active tracker, it will try to find the compute the closest
pattern it can find on the current frame. To limit the tracker's search region, 
hold the right click button of your mouse, and drag & drop your mouse to draw a rectangular
search region. 

## Switch to a specific tracker
In the `Trackers` tab, hover your cursor over the `Switch Trackers` tab.
The active tracker affected by your inputs will be highlighted with an orange arrow
next to it.

# Plotting tracker data
It is possible to plot the distance between two trackers relative to time.
With at least two different trackers, click on the `Plots` tab, and select `Create a new plot`.
Specify the name of the plot and both trackers to plot distance against.
The FPS field is only used to compute valid time values for the x-axis, set it to
1 if you do not care about it.

The plot should appear on the right. You can right-click on it to export the data of the plot.