import time

import numpy as np
import matplotlib.pyplot as plt

from PhotosensitivitySafetyEngine.guidelines.w3c import *

THRESHOLD = 3

def analysis(video_path, show_live_chart=False, show_dsp=False, show_analysis=False):
    analysis_start = time.time()
    analysis_result = w3c_guideline.analyse_file(video_path, show_live_chart=show_live_chart,
                                                 show_dsp=show_dsp, show_analysis=show_analysis)
    print(f'\nANALYSIS TIME : {time.time() - analysis_start}')
    return analysis_result


def frame_intervals(result):
    is_general, is_red = False, False
    general_start, red_start = None, None

    red_flashes, general_flashes = [], []

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

    print("Frame Interval Results")
    print("General Flashes", general_flashes)
    print("Red Flashes", red_flashes)

    return general_flashes, red_flashes


def read_video_sequence(path, frame_start, frame_end):
    capture = cv2.VideoCapture(path)

    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_count = frame_end - frame_start

    capture.set(1, frame_start)

    BGR_sequence = np.ones((frame_count, height, width, 3), dtype=np.uint8)
    HSV_sequence = np.ones((frame_count, height, width, 3), dtype=np.uint8)

    FPS = int(capture.get(cv2.CAP_PROP_FPS))
    for f in range(frame_count):
        check, frame = capture.read()
        if check:
            HSV_sequence[f] = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            BGR_sequence[f] = frame

    original_sequence = BGR_sequence.copy()

    return FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence


def average_correction(video_sequence, FPS, interval):
    average_interval = int(FPS // interval)

    for i in range(0, frame_count):
        video_sequence[i] = np.average(video_sequence[i:i + average_interval], axis=0)


def write_video(original_video, corrected_video, FPS):
    frame_count, height, width, dim = corrected_video.shape

    corrected = cv2.VideoWriter('sequence_corrected_video.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), FPS,
                                (width, height))
    original = cv2.VideoWriter('sequence_video.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), FPS, (width, height))

    for frame in range(frame_count):
        corrected.write(corrected_video[frame])
        original.write(original_video[frame])

    corrected.release()
    original.release()


if __name__ == "__main__":
    original_video_path = 'pokemon.mp4'
    sequence_corrected_video_path = "sequence_corrected_video.avi"
    sequence_video_path = "sequence_video.avi"

    analysis_result = analysis(original_video_path)

    general_flashes, red_flashes = frame_intervals(analysis_result)

    frame_start, frame_end = red_flashes[1][0], red_flashes[1][1]

    FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = read_video_sequence(original_video_path,
                                                                                          frame_start, frame_end)
    # Changed the given video
    average_correction(BGR_sequence, FPS, 6)

    write_video(original_sequence, BGR_sequence, FPS)

    # Analyze corrected video
    corrected_analysis_result = analysis(sequence_corrected_video_path, show_analysis=True)


'''
# def average_correction_hsv(vid):
#     # FPS/4
#     up_speed = 5
#     for frm in range(0, frame_count, 3):
#         for w in range(width):
#             for h in range(height):
#                 vid_vals = vid[frm:frm + up_speed, h, w]
#                 # print(std_vals)
#                 if (np.max(vid_vals, axis=0)) - (np.min(vid_vals, axis=0)) > 60:
#                     out[frm:frm + up_speed, h, w] = np.average(out[frm:frm + up_speed, h, w], axis=0)
#         print(frm)
'''


def hsv_to_bgr(hsv, bgr):
    for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
        bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)


def low_pass_filter(adata: np.ndarray, bandlimit: int = 3, sampling_rate: int = 30) -> np.ndarray:
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    bandlimit_index = int(bandlimit * adata.size / sampling_rate)
    fsig = np.fft.fft(adata)

    for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
        fsig[i] = 0

    adata_filtered = np.fft.ifft(fsig)

    return np.real(adata_filtered)
