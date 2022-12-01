from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.engine.analysis import GuidelineProcess, Display
from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries.function_objects import *
from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries import common_functions, custom_functions
import numpy as np

# FUNCTION OBJECTS
function_objects = lambda properties: {
    'colorCurve': common_functions.colorCurve('RGB2XYZ'),
    'relativeLuminance': common_functions.relativeLuminance(),
    'relativeLuminanceLighter': common_functions.changeDetect(direction=1, minimum=20/properties['candelas']),
    'relativeLuminanceDarker': common_functions.changeDetect(direction=-1, minimum=20/properties['candelas']),
    'relativeLuminanceCondition': common_functions.pastOrPresentThreshold(160/properties['candelas'], direction=-1),
    'bothConditions': common_functions.twoConditions(),
    'combinedAreaCondition': ArrayToValue(lambda x: np.average(x) > 0.25),
    'fullFlashCountGeneral': ValueHistoriesToValue(lambda x, y: custom_functions.count_flashes(x, y, frame_rate=properties['frame_rate'])),
    'threshold': ValueToValue(lambda x: x > 3)
}

# PROCESSING PIPELINE
processing_pipeline = [
    ('colorCurve', 0),
    ('relativeLuminance', 1),
    ('relativeLuminanceLighter', 2),
    ('relativeLuminanceDarker', 2),
    ('relativeLuminanceCondition', 2),
    ('bothConditions', (3, 5)),
    ('bothConditions', (4, 5)),
    ('combinedAreaCondition', 6),
    ('combinedAreaCondition', 7),
    ('fullFlashCountGeneral', (8, 9), "General Flashes"),
    ('threshold', 10, "Fail")
]

# GUIDELINE OBJECT CREATION
ofcom_guideline = GuidelineProcess(function_objects, processing_pipeline)
# display_properties = Display(display_resolution=(1024, 768), display_diameter=16, display_distance=24)

# EXECUTION
# ofcom_guideline.analyse_file('path', display_properties, speedup=5, show_live_analysis=False, show_live_chart=False)
