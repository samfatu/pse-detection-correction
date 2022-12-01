import pafy
from unused_functions.frame_functions import *
from functions.help_functions import *
from datetime import datetime
import cv2.cv2 as cv2

time0 = datetime.now()

# INITIALISE
previousDisplayFrame = np.zeros((225, 300, 3))
previousRelativeLuminance = 0
lastChanges = (0.0, 0.0)
frameCount = 0

# THRESHOLDS
thresholds = 0.25/9, 0.25  # 2.8%, 25.0%

# SET VIDEO CAPTURE
videos = [
    ("https://www.youtube.com/watch?v=GuLcxg5VGuo", 'pafy'),  # barney video cv
    ("https://www.youtube.com/watch?v=B4wSFjR9TMQ", 'pafy'),  # pokemon
    ("https://www.youtube.com/watch?v=FkhfLNfWIHA", 'pafy'),  # flashing images
    ("https://www.youtube.com/watch?v=XqZsoesa55w", 'pafy'),  # baby shark
    ("https://www.youtube.com/watch?v=0EqSXDwTq6U", 'pafy'),  # charlie bit my finger
    ('path', 'local'),  # pokemon local
    ('path', 'local'),  # peat recording local
    ('path', 'local'),  # lecture recording 1
    ('path', 'local'),  # lecture recording 2
]
video = videos[0]

if video[1] == 'pafy':
    capture = cv2.VideoCapture(pafy.new(video[0]).getbest(preftype="mp4").url)
else:
    capture = cv2.VideoCapture(video[0])


frameRate = capture.get(cv2.CAP_PROP_FPS)
# captureLength = capture.get(cv2.CAP_PROP_FRAME_COUNT)
# captureWidth = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
# captureHeight = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
analysisSize = (300, 225)

time1 = datetime.now()

# MAIN LOOP FOR EACH FRAME

while True:

    frameCount += 1
    check, frame = capture.read()

    if check:
        # CALCULATIONS
        displayFrame = cv2.resize(frame, analysisSize)
        relativeLuminance = w3c_relative_luminance.calculate_relative_luminance(displayFrame)
        relativeLuminanceLimits = relative_luminance_both_limits(relativeLuminance, previousRelativeLuminance)
        lastChanges = update_both_last_flashes(lastChanges, relativeLuminanceLimits, frameRate)
        flashes = cross_reference_both_transitions(lastChanges, relativeLuminanceLimits)
        flashCounts = flash_both_frames_separator(flashes)
        flash_detect_printout_both(flashes, flashCounts, frameCount, frameRate, thresholds)

        # REMEMBER LAST FRAME
        previousDisplayFrame = displayFrame
        previousRelativeLuminance = relativeLuminance

        continue
    break

# END CAPTURE AND MONITORS
capture.release()
cv2.destroyAllWindows()

time2 = datetime.now()

print((time1 - time0).total_seconds())

print((time2 - time1).total_seconds())

# print(captureLength/frameRate)
