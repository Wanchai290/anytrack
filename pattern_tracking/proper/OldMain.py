from threading import Event

import cv2 as cv

from pattern_tracking.proper import constants
from pattern_tracking.proper.DistanceObserver import DistanceObserver
from pattern_tracking.proper.OldGUI import OldGUI
from pattern_tracking.proper.TemplateTracker import TemplateTracker
from pattern_tracking.proper.TrackerManager import TrackerManager
from pattern_tracking.proper.VideoReader import VideoReader


class OldMain:

    def __init__(self):
        self.__halt_event = Event()

        self.__TRACKER_MANAGER = TrackerManager()

        # <<< required as there's no GUI at the moment to add a tracker
        self.__TRACKER_MANAGER.add_tracker(TemplateTracker("Default"))
        self.__TRACKER_MANAGER.add_tracker(TemplateTracker("Auxiliary"))
        self.__TRACKER_MANAGER.set_active_tracker("Default")
        self.__DISTANCE_OBSERVER = \
            DistanceObserver(
                "DistanceDefault",
                self.__TRACKER_MANAGER.get_tracker("Default"),
                self.__TRACKER_MANAGER.get_tracker("Auxiliary")
            )
        # >>>

        self.__LIVE_FEED = VideoReader(0, False, self.__halt_event)
        self.__LIVE_FEED.run_threaded()

        self.__GUI = OldGUI(
            constants.WINDOW_NAME,
            self.__LIVE_FEED.grab_frame(block=True)[1].shape,
            self.__TRACKER_MANAGER,
            self.__halt_event
        )

    def run(self):
        self.__GUI.start_gui()

        while not self.__halt_event.is_set():
            live_frame = self.__LIVE_FEED.grab_frame(block=True)[1]
            edited_frame = self.__TRACKER_MANAGER.update_trackers(live_frame, drawing_sheet=live_frame.copy())
            self.__GUI.change_frame_to_display(edited_frame)
            d = self.__DISTANCE_OBSERVER.distance()
            if d != 0:
                print(d)
        cv.destroyAllWindows()


if __name__ == '__main__':
    worker = OldMain()
    worker.run()
