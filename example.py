import time
import numpy as np
import matplotlib.pyplot as plt
from PhotosensitivitySafetyEngine.guidelines.w3c import *

THRESHOLD = 3

class CustomVideo:
    def __init__(self, video_path):
        self.video_path = video_path
        self.capture = cv2.VideoCapture(self.video_path)
        self.video_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.FPS = int(self.capture.get(cv2.CAP_PROP_FPS))

        self.analysis_result = []
        self.flashes = []

    def analyse_video(self):
        self.analysis_result = analysis(self.video_path)
        self.flashes = frame_intervals(self.analysis_result)
        print()

    def read_video_sequence(self, frame_interval):
        frame_count = frame_interval[2] - frame_interval[1]
        self.capture.set(1, frame_interval[1])

        BGR_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)
        HSV_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)

        for f in range(frame_count):
            check, frame = self.capture.read()
            if check:
                HSV_sequence[f] = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                BGR_sequence[f] = frame

        original_sequence = BGR_sequence.copy()

        return self.FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence

    def get_frame_interval(self, frame_interval):
        self.capture.set(1, frame_interval[0])

        frame_count = frame_interval[1] - frame_interval[0]
        BGR_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)

        for f in range(frame_count):
            check, frame = self.capture.read()
            if check:
                BGR_sequence[f] = frame

        return BGR_sequence

    def get_flashes(self):
        return self.flashes


def analysis(video_path, show_live_chart=False, show_dsp=False, show_analysis=False):
    print(f'Video analysis started...')
    analysis_start_time = time.time()
    analysis_result = w3c_guideline.analyse_file(video_path, show_live_chart=show_live_chart,
                                                 show_dsp=show_dsp, show_analysis=show_analysis)
    print(f'\nAnalysis took {(time.time() - analysis_start_time):.3f} seconds.')
    return analysis_result

def frame_intervals(result):
    #print(result)
    is_general, is_red, is_both = False, False, False
    general_start, red_start, both_start = None, None, None

    flashes = []
    for i, (general, red) in enumerate(zip(result["General Flashes"], result["Red Flashes"])):
        #  RED  GENERAL
        #   >3   <=3   ->> ONLY RED
        #   >3    >3   ->> BOTH
        #  <=3    >3   ->> ONLY GENERAL
        #  <=3   <=3   ->> CORRECT
        is_frame_both = general > THRESHOLD and red > THRESHOLD
        is_frame_general = general > THRESHOLD and not is_frame_both
        is_frame_red = red > THRESHOLD and not is_frame_both

        if is_frame_both and not is_both:
            is_both = True
            both_start = i
        elif not is_frame_both and is_both:
            is_both = False
            flashes.append(('both', both_start, i))

        if is_frame_general and not is_general:
            is_general = True
            general_start = i
        elif not is_frame_general and is_general:
            is_general = False
            flashes.append(('general', general_start, i))

        if is_frame_red and not is_red:
            is_red = True
            red_start = i
        elif not is_frame_red and is_red:
            is_red = False
            flashes.append(('red', red_start, i))

    if is_general:
        flashes.append(('general', general_start, len(result["General Flashes"])))
    elif is_red:
        flashes.append(('red', red_start, len(result["Red Flashes"])))

    print("Frame Interval Results")
    print("Flashes", flashes)

    return flashes


def average_correction(video_sequence, FPS, frame_count, interval=15):
    average_interval = int(FPS // interval)
    corrected_sequence = video_sequence.copy()
    for i in range(0, frame_count):
        lower = i - average_interval if i - average_interval > 0 else 0
        upper = i + average_interval if i + average_interval < frame_count else frame_count
        corrected_sequence[i] = np.average(video_sequence[lower:upper], axis=0)
    return corrected_sequence

def apply_correction_on_video(original_video, output_path):
    print(f'Correction started...')
    corrected_sequences = []

    for frame_info in original_video.flashes:
        if frame_info[0] == 'general':
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(frame_info)
            corrected_sequence = average_correction(BGR_sequence, FPS, frame_count) # Change correction method
            corrected_sequences.append(corrected_sequence)
        else:
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(frame_info)
            corrected_sequence = average_correction(BGR_sequence, FPS, frame_count) # Change correction method
            corrected_sequences.append(corrected_sequence)

    write_corrected_sequences(original_video, corrected_sequences, output_path)
    print()

def write_corrected_sequences(original_video, corrected_sequences, output_path):
    corrected = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), original_video.FPS,
                                (original_video.video_width, original_video.video_height))
    first_part = original_video.get_frame_interval((0, original_video.flashes[0][1]))

    for frame in first_part:
        corrected.write(frame)

    for (i, corrected_sequence) in zip(range(len(original_video.flashes)), corrected_sequences):
        for frame in corrected_sequence:
            corrected.write(frame)

        next_interval = (original_video.flashes[i][2], original_video.flashes[i + 1][1] if (i + 1) < len(original_video.flashes) else original_video.frame_count)
        next_part = original_video.get_frame_interval(next_interval)
        for frame in next_part:
            corrected.write(frame)

    corrected.release()

def compare(original_video, corrected_video):
    pass

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
    corrected_video_path = "corrected_video.avi"

    original_video = CustomVideo(original_video_path)
    original_video.analyse_video()

    #apply_correction_on_video(original_video, corrected_video_path) # Generates corrected video on given path

    #corrected_video = CustomVideo(corrected_video_path)
    #corrected_video.analyse_video()


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