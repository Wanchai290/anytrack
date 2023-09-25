from collections import namedtuple
from enum import Enum

from src.pattern_tracking.logic.tracker.FixedPointTracker import FixedPointTracker
from src.pattern_tracking.logic.tracker.KCFTracker import KCFTracker
from src.pattern_tracking.logic.tracker.TemplateTracker import TemplateTracker

TrackerTypeData = namedtuple("TrackerTypeData", "name constructor")


class TrackerType(Enum):
    """
    Describes the different types of tracker that are available in the app
    Their data is accessible by name, and are defined by the named tuple TrackerTypeData,
    located in the same file as this class.
    """
    TEMPLATE_TRACKER = TrackerTypeData("Template tracker", TemplateTracker)
    KCF_TRACKER = TrackerTypeData("KCF Tracker", KCFTracker)
    FIXED_POINT_TRACKER = TrackerTypeData("Fixed Point tracker", FixedPointTracker)