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
result = w3c_guideline.analyse_file(normal_file, show_live_chart=False, show_dsp=False, show_analysis=True)
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
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

print("CaptureWidth : ", width, "\n"
                                "CaptureHeight : ", height)

frame_end = red_flashes[1][1]
frame_start = red_flashes[1][0]
frame_count = frame_end - frame_start
capture.set(1, frame_start)
video_slice_BGR = np.ones((frame_count, height, width, 3), dtype=np.uint8)
video_slice_HSV = np.ones((frame_count, height, width, 3), dtype=np.uint8)

for f in range(frame_count):
    check, frame = capture.read()
    if check:
        video_slice_HSV[f] = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        video_slice_BGR[f] = frame

vs_original = video_slice_BGR.copy()


def average_correction(vid):
    # FPS/6
    up_speed = int(30 // 6)
    for frm in range(0, frame_count, 2):
        for w in range(width):
            for h in range(height):
                vid[frm:frm + up_speed, h, w] = np.average(vid[frm:frm + up_speed, h, w], axis=0)
        print(frm)


def average_correction_hsv(vid):
    # FPS/4
    up_speed = int(30 // 4)
    for frm in range(0, frame_count, 2):
        for w in range(width):
            for h in range(height):
                vid[frm:frm + up_speed, h, w, 2] = np.average(vid[frm:frm + up_speed, h, w, 2], axis=0)
        print(frm)


def hsv_to_bgr(hsv, bgr):
    for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
        print(idx_BGR, idx_HSV)
        bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)


average_correction(video_slice_BGR)

# ALGORITHM YASIR
# average_correction_hsv(video_slice_HSV)
# hsv_to_bgr(video_slice_HSV, video_slice_BGR)

out = cv2.VideoWriter('out.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (width, height))
normal_out = cv2.VideoWriter('out_normal.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (width, height))
for frame in range(frame_count):
    out.write(video_slice_BGR[frame])
    normal_out.write(vs_original[frame])
    # cv2.imshow('Video', video_slice[frame]), cv2.waitKey(1)
    # cv2.imshow('Video2', vs_original[frame]), cv2.waitKey(1)
    time.sleep(0.01)

out.release()
normal_out.release()
