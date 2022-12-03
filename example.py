import time

import numpy as np
import matplotlib.pyplot as plt

from PhotosensitivitySafetyEngine.guidelines.w3c import *


def low_pass_filter(adata: np.ndarray, bandlimit: int = 3, sampling_rate: int = 30) -> np.ndarray:
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    bandlimit_index = int(bandlimit * adata.size / sampling_rate)

    fsig = np.fft.fft(adata)

    for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
        fsig[i] = 0

    adata_filtered = np.fft.ifft(fsig)

    return np.real(adata_filtered)


THRESHOLD = 3

normal_file = 'pokemon.mp4'
test_file = "out.avi"
start = time.time()
result = w3c_guideline.analyse_file(test_file, show_live_chart=False, show_dsp=False, show_analysis=True)
end = time.time()

# TODO HSV çevrilip luminance kanalı ortalaması alınarak gidilecek

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
print("General Flashes", general_flashes)
print("Red Flashes", red_flashes)

print("\nTIME : ", end="")
print(end - start)

V_PATH = "./pokemon.mp4"
capture = cv2.VideoCapture(V_PATH)
w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

print("CaptureWidth : ", w, "\n"
                            "CaptureHeight : ", h)

frame_end = red_flashes[1][1]
frame_start = red_flashes[1][0]
frame_count = frame_end - frame_start
capture.set(1, frame_start)
video_slice = np.ones((frame_count, h, w, 3), dtype=np.uint8)

for f in range(frame_count):
    check, frame = capture.read()
    if check:
        video_slice[f] = frame
        # print(frame[:, :, 2])
        # cv2.imshow('Video', video_slice[f]), cv2.waitKey(1)
        # time.sleep(0.01)

vs_original = video_slice.copy()

print(video_slice.shape)

# for x in range(w):
#     for y in range(h):
#         red_values = video_slice[:, y, x, 2]
#         #
#         # _fft_freq = np.fft.fftfreq(len(red_values), d=1 / 30)
#         # _fft = np.fft.fft(red_values)
#         #
#         # half_freq = _fft_freq[:len(red_values) // 2]
#         # for i in range(len(half_freq)):
#         #     if half_freq[i] > 3:  # cut off all frequencies higher than 0.005
#         #         _fft[i] = 0.0
#         #         _fft[len(red_values) // 2 + i] = 0.0
#         #
#         # video_slice[:, y, x, 2] = np.fft.ifft(_fft)
#         video_slice[:, y, x, 2] = low_pass_filter(red_values,bandlimit = 0.0000002,sampling_rate=30)

# FPS/6
up_speed = int(30//6)
for frame in range(0, frame_count, 2):
    for x in range(w):
        for y in range(h):
            video_slice[frame:frame + up_speed, y, x] = np.average(video_slice[frame:frame + up_speed, y, x], axis=0)
    print(frame)

out = cv2.VideoWriter('out.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (w, h))
normal_out = cv2.VideoWriter('out_normal.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (w, h))
for frame in range(frame_count):
    out.write(video_slice[frame])
    normal_out.write(vs_original[frame])
    # cv2.imshow('Video', video_slice[frame]), cv2.waitKey(1)
    # cv2.imshow('Video2', vs_original[frame]), cv2.waitKey(1)
    time.sleep(0.01)

out.release()
normal_out.release()
