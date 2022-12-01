import time

import pandas as pd
from matplotlib import pyplot as plt

from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries.function_objects import *
from PhotosensitivitySafetyEngine.PhotosensitivitySafetyEngine.libraries import common_functions as functions, custom_functions


import re
def count_flashes(flashes_lighter, flashes_darker, frame_rate):
    # this may be over-counting slightly
    flashes_lighter[0], flashes_darker[0] = 0, 0
    channel1, channel2 = flashes_lighter[-(frame_rate - 1):], flashes_darker[-(frame_rate - 1):]
    both_channels = ''
    for i in range(len(channel1)):
        if channel1[i] and channel2[i]:
            both_channels += 'X'
        elif channel1[i]:
            both_channels += '1'
        elif channel2[i]:
            both_channels += '2'
    both_channels = re.sub('1+', '1', both_channels)
    both_channels = re.sub('2+', '2', both_channels)
    count = len(both_channels)
    return count


# Function Objects
# rlCurve = InputToArray(lambda X: max(X / 255 / 12.92, ((X / 255 + 0.055) / 1.055) ** 2.4))
# relativeLuminance = ArrayToArrayChannels(lambda R, G, B: 0.2126 * R + 0.7152 * G + 0.0722 * B)
# lighter = ArrayAndPastToArray(lambda Present, Past: ((Present - Past) >= 0.1) * (Past <= 0.8))
# darker = ArrayAndPastToArray(lambda Present, Past: ((Present - Past) <= -0.1) * (Present <= 0.8))
# maximumRegion = ArrayToBoolean(lambda x: custom.area_averages_max(x, threshold=0.25))
# redSaturation = ArrayToArrayChannels(lambda R, G, B: R / (R + G + B) if R else 0)
# redMajority = ArrayToArrayChannels(lambda R, G, B: max(R - G - B, 0) * 320)
# redMajorityChangeUp = ArrayAndPastToArray(lambda Present, Past: (Present - Past) > 20)
# redMajorityChangeDown = ArrayAndPastToArray(lambda Present, Past: (Present - Past) < -20)
# redSaturationChange = ArrayAndPastToArray(lambda Present, Past: max(Present, Past) >= 0.8)
# bothConditions = ArraysToArray(lambda Array1, Array2: Array1 * Array2)
rlCurve = functions.colorCurve(curve='RGB2XYZ')
relativeLuminance = functions.relativeLuminance()
relativeLuminanceLighter = ArrayAndPastToArray(lambda Present, Past:  np.where(Present - Past >= 0.1, 1, 0) * np.where(Past <= 0.8, 1, 0), vector_form=True)
relativeLuminanceDarker = ArrayAndPastToArray(lambda Present, Past:  np.where(Past - Present >= 0.1, 1, 0) * np.where(Present <= 0.8, 1, 0), vector_form=True)
relativeLuminanceCondition = ArrayAndPastToArray(lambda Present, Past: np.where(np.minimum(Present, Past) <= 0.8, 1, 0), vector_form=True)
maximumRegion = ArrayToValue(lambda x: custom_functions.area_averages_max(x, threshold=0.25))
redSaturation = ArrayChannelsToArray(lambda R, G, B: np.divide(R, (R + G + B), out=np.zeros(R.shape, dtype=float), where=R != 0), vector_form=True)
redMajority = ArrayChannelsToArray(lambda R, G, B: np.maximum(R - G - B, 0) * 320, vector_form=True)
redMajorityChangeUp = ArrayAndPastToArray(lambda Present, Past: np.where(Present - Past > 20, 1, 0), vector_form=True)
redMajorityChangeDown = ArrayAndPastToArray(lambda Present, Past: np.where(Present - Past < -20, 1, 0), vector_form=True)
redSaturationCondition = ArrayAndPastToArray(lambda Present, Past: np.where(np.maximum(Present, Past) >= 0.8, 1, 0), vector_form=True)
bothConditions = ArraysToArray(lambda Array1, Array2: np.logical_and(Array1, Array2), vector_form=True)


general_flashes_lighter = []
general_flashes_darker = []
general_flashes_counter = []
red_flashes_lighter = []
red_flashes_darker = []
red_flashes_counter = []


def processingPipeline(stage_0):
    stage_01 = rlCurve.run(stage_0)
    stage_012 = relativeLuminance.run(stage_01)
    stage_0123 = relativeLuminanceLighter.run(stage_012)
    stage_0124 = relativeLuminanceDarker.run(stage_012)
    stage_012A = relativeLuminanceCondition.run(stage_012)
    stage_0123A = bothConditions.run(stage_0123, stage_012A)
    stage_0124A = bothConditions.run(stage_0124, stage_012A)
    stage_01235 = maximumRegion.run(stage_0123A)
    stage_01245 = maximumRegion.run(stage_0124A)
    stage_016 = redMajority.run(stage_01)
    stage_017 = redSaturation.run(stage_01)
    stage_0168 = redMajorityChangeUp.run(stage_016)
    stage_0169 = redMajorityChangeDown.run(stage_016)
    stage_017A = redSaturationCondition.run(stage_017)
    stage_017A_068 = bothConditions.run(stage_017A, stage_0168)
    stage_017A_069 = bothConditions.run(stage_017A, stage_0169)
    stage_07A_068_5 = maximumRegion.run(stage_017A_068)
    stage_07A_069_5 = maximumRegion.run(stage_017A_069)

    general_flashes_lighter.append(int(stage_01235))
    general_flashes_darker.append(int(stage_01245))
    general_flashes_counter.append(count_flashes(general_flashes_lighter, general_flashes_darker, 30))

    red_flashes_lighter.append(int(stage_07A_068_5))
    red_flashes_darker.append(int(stage_07A_069_5))
    red_flashes_counter.append(count_flashes(red_flashes_lighter, red_flashes_darker, 30))

    return [stage_01235, stage_01245, stage_07A_068_5, stage_07A_069_5]


# Dataframe
df = pd.DataFrame(columns=['Lighter', 'Darker', 'More-Red', 'Less-Red'])

capture = cv2.VideoCapture('path')
print(time.time())
for i in range(333):
    print(i)
    check, frame = capture.read()
    df.loc[i] = processingPipeline(frame)
print(time.time())
print(df.T.astype(int).to_string())

plt.plot(np.arange(len(general_flashes_counter)) / 30, general_flashes_counter)
plt.plot(np.arange(len(general_flashes_counter)) / 30, red_flashes_counter)
plt.plot(np.arange(len(general_flashes_counter)) / 30, [3] * len(general_flashes_counter))
plt.ylabel('Flash Counts')
plt.show()
