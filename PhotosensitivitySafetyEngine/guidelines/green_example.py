from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.engine.analysis import GuidelineProcess, Display
from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries.function_objects import *
from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries import common_functions
import numpy as np

# FUNCTION OBJECTS
function_objects = lambda properties: {
    'colorCurve': common_functions.colorCurve('RGB2XYZ'),
    'greenValue': common_functions.colorValue(green=1),
    'greenProportion': common_functions.colorProportion(green=1),
    'valueThreshold': common_functions.threshold(0.3),
    'proportionThreshold': common_functions.threshold(0.5),
    'greenFrameFragments': common_functions.twoConditions(),
    'greenFrameProportion': ArrayToValue(lambda x: np.average(x)),
    'greenFrameAlert': ValueToValue(lambda x: x > 0.03),
    'countGreenFrames': ValueHistoryToValue(lambda x: sum(x)),
    'threshold': ValueToValue(lambda x: x > 10)
}

# PROCESSING PIPELINE
processing_pipeline = [
    ('colorCurve', 0),
    ('greenValue', 1),
    ('greenProportion', 1),
    ('valueThreshold', 2),
    ('proportionThreshold', 3),
    ('greenFrameFragments', (4, 5)),
    ('greenFrameProportion', 6, "Green%"),
    ('greenFrameAlert', 7, "Too Green"),
    ('countGreenFrames', 8, "Total Too Green Frames"),
    ('threshold', 9, "Fail")

]

# GUIDELINE OBJECT CREATION
green_guideline = GuidelineProcess(function_objects, processing_pipeline)
display_properties = Display(display_resolution=(1024, 768), display_diameter=16, display_distance=24)

# EXECUTION
green_guideline.analyse_file('path', display_properties, speedup=5, show_live_analysis=False, show_live_chart=False)
green_guideline.analyse_live('path', speedup=5, show_live_analysis=False, show_live_chart=False)
