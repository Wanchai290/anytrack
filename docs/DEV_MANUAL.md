# Development guide
This small markdown is here to explain the architecture of the application,
notably how to implement a new tracker to test. It is not an extensive guide on how the
application, but rather the outline of the application.

## Table of contents
- Main architecture, UI and logic
- Implementing your tracker
- Custom protocol with ZeroMQ

## Main architecture, UI and logic
The application is a QT app based around the QMainWindow object.

The `Main` class is here to connect all the logical components together.
To continuously compute the new tracked region's position, we use an instance
of the `BackgroundCmoputation` worker class, whose job is just to process tracker
data by updating the found region in the next frame, and updating other components
that require this data, such as the `FrameDisplayWidget` which needs to display the widget
to the screen, and the `LivePlotterDockWidget` who needs to update its plots.
This way, the main work revolves around this background computation. It takes care of fetching
the next frame and updating the other components, in a separate thread from the UI thread.

### UI design
The parent UI object in the application is the `AppMainWindow` class. It contains
one object processing logic, which is the `TrackerManager`, and contains the other
UI objects such as the two displayed widget : the `FrameDisplayWidget` which is the main
widget displayed on the QT Main Window, and the `LivePlotterDockWidget` which is a container
displayed on the right of the screen.

UI objects only contain code to handle the user interface, they do not call functions
processing logic. But the objects that need it are connected to the logic-processing objects.
For example, the `FrameDisplayWidget` class is linked with an instance of the `TrackerManager` object
to detect whether there are any trackers defined, before allowing the user to define a tracked region
or a detection region.

You can find all the UI elements in the `qt_gui` folder.

### Logic processing

The logical processing is performed in the `logic` folder. It is based on the
use of abstract classes to define shared behaviour between different implementations


- `video/AbstractFrameProvider`  
Used to outline how we should be able to receive frames
from an external (or internal) source. Based off a Queue in which frames
must be put and retrieved from.
All the other files are just implementations extending the base
abstract class.


- `tracker/AbstractTracker`  
Defines the capabilities of a tracker in the application, and provides
some functions to help with default behaviour.
The three implemented trackers are in the same folder


The `tracker` folder also contains two additional objects,
where the `TrackerManager` class is only used by the
main application to manage the creation and storage of multiple trackers.

The last class `TrackerType` is an enum that defines the available tracker
implementations the user can choose from. Thus, when implementing a new
tracker, you need to modify this enum with a new line for your implementation.
This single modification will make your tracker available to the user, you can
see the implementation details in the `TrackerManager` class

## Implementing your tracker
1. Extend the `AbstractTracker` class 
2. Implement the `update()` method
3. (optional) Override `set_detection_region()` to return nothing if your implementation doesn't use the region
4. Add an entry to the TrackerType enum with a new TrackerTypeData object, and specify your tracker's name and constructor

Note that your constructor must call the abstract class' constructor.
You can override any non-abstract method in `AbstractTracker` if required.

## Custom protocol with ZeroMQ
This protocol has been created for the needs of the internship. It is meant to transfer
a NumPy matrix of arbitrary size.

The `comm_protocol` contains a dummy ZeroMQ publisher and subscriber to test the protocol.
You can run the `zmq_sock_test.sh` script to either test the protocol, or only run the publisher
to run it alongside the main application (by selecting `Video -> From ZMQ socket`).
You can read about its usage [here](../custom_integrations/tixier_mita_lab/README.md).