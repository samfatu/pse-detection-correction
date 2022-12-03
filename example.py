import time

import numpy as np
import matplotlib.pyplot as plt

from PhotosensitivitySafetyEngine.guidelines.w3c import *

THRESHOLD = 3

start = time.time()
result = w3c_guideline.analyse_file('pokemon.mp4', show_live_chart=False, show_dsp=False, show_analysis=False)
end = time.time()

is_general = False
is_red = False

general_start = None
red_start = None

red_flashes = []
general_flashes = []
for i, (general, red) in enumerate(zip(result["General Flashes"], result["Red Flashes"])):
    if red > THRESHOLD and not is_red:
        is_red = True
        red_start = i

    elif red < THRESHOLD and is_red:
        is_red = False
        red_flashes.append((red_start, i))

    if general - red > THRESHOLD and not is_general:
        is_general = True
        general_start = i
    elif general - red < THRESHOLD and is_general:
        is_general = False
        general_flashes.append((general_start, i))
print()
print(general_flashes)
print(red_flashes)
# start = 535
# end = 679
# subs = np.array(result["General Flashes"]) - np.array(result["Red Flashes"])
# print(subs[subs <= -1])
# print(result["Red Flashes"][start:end])
print("\nTIME : ", end="")
print(end - start)

V_PATH = "./pokemon.mp4"
capture = cv2.VideoCapture(V_PATH)
w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(w, h)
frame_count = red_flashes[1][1] - red_flashes[1][0]
print(frame_count)
print("FPS OF THE VIDEO : ", int(capture.get(cv2.CAP_PROP_FPS)))
print(red_flashes[0][0])
capture.set(1, red_flashes[1][0])
video_slice = np.ones((frame_count, h, w, 3), dtype=np.uint8)
print(video_slice.shape)
print(capture)
for f in range(frame_count):
    check, frame = capture.read()
    if check:
        video_slice[f] = frame
        # print(frame[:, :, 2])
        # cv2.imshow('Video', video_slice[f]), cv2.waitKey(1)
        # time.sleep(0.01)

print(video_slice.shape)

for x in range(w):
    for y in range(h):
        red_values = video_slice[:, y, x, 2]
        print(red_values)

        _fft = np.fft.fft(red_values)
        # _fft.real = 0
        # video_slice[:, y, x, 0] = np.fft.ifft(_fft)
        _fft_freq = np.fft.fftfreq(len(red_values), d=1 / 30)
        idx_5 = np.where(_fft_freq == 5)[0][0]
        idx_n5 = np.where(_fft_freq == -5)[0][0]
        # print(
        # idx_5,idx_n5
        # )

        _fft.real[idx_n5:] = 255
        _fft.real[0:idx_5] = 255
        video_slice[:, y, x, 2] = np.fft.ifft(_fft)
        # plt.plot(_fft_freq, _fft.real)
        # plt.show()
        # print(fft)
#


# for frame in range(frame_count):
#     print(np.std(video_slice[frame:frame + 10, :, :, :]))
for frame in range(frame_count):
    cv2.imshow('Video', video_slice[frame]), cv2.waitKey(1)
    time.sleep(0.01)
