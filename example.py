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

class CorrectionEngine:
    def __init__(self, video:CustomVideo, output_path:str):
        self.video = video
        self.output_path = output_path

    def low_pass_filter(self, adata: np.ndarray, bandlimit: int = 3, sampling_rate: int = 30) -> np.ndarray:
        # translate bandlimit from Hz to dataindex according to sampling rate and data size
        bandlimit_index = int(bandlimit * adata.size / sampling_rate)
        fsig = np.fft.fft(adata)

        for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
            fsig[i] = 0

        adata_filtered = np.fft.ifft(fsig)

        return np.real(adata_filtered)

    # Correct general flash by averaging frames in an interval
    def general_correction_v1(self, frame_info):
        interval = 6
        general_interval = int(self.video.FPS // interval)
        sequence_start = max(frame_info[1] - general_interval, 0)
        sequence_end = min(frame_info[2] + general_interval, self.video.frame_count)

        FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = self.video.read_video_sequence((frame_info[0], sequence_start, sequence_end))
        corrected_sequence = BGR_sequence.copy()

        for i in range(general_interval, frame_count):
            lower = max(i - general_interval, 0)
            upper = min(i + general_interval, frame_count)
            corrected_sequence[i] = np.average(BGR_sequence[lower:upper], axis=0)

        return corrected_sequence[general_interval:frame_count - general_interval]

    def adjust_brightness(self, frame, brightness_factor):
        # Brightness factor: >1 to increase, <1 to decrease, 1 to keep unchanged
        adjusted_frame = np.clip(frame * brightness_factor, 0, 255).astype(np.uint8)
        return adjusted_frame

    # Corrects general flash by downgrading the brigthness of the frames
    def general_correction_brightness(self, frame_info):
        FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = self.video.read_video_sequence(frame_info)

        corrected_sequence = BGR_sequence.copy()
        for i in range(0, frame_count):
            corrected_sequence[i] = self.adjust_brightness(corrected_sequence[i], 0.3)

        return corrected_sequence

    def red_correction(self, frame_info):
        print("red correction")
        FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = self.video.read_video_sequence(frame_info)

        corrected_sequence = BGR_sequence.copy()
        corrected_sequence[:, :, :, 2] = (corrected_sequence[:, :, :, 2] * 0.1).astype(np.uint8)

        return corrected_sequence


    def both_correction(self, video_sequence, FPS, frame_count, interval=15):
        print("both correction")
        pass

    def choose_algorithm(self, correction_type):
        if correction_type == 'general':
            return self.general_correction_v1
        elif correction_type == 'red':
            return self.red_correction  # TODO: Algoritmaları değiştir
        elif correction_type == 'both':
            return self.general_correction_v1  # TODO: both yap
        else:
            print("Unknown situation")
            return

    def apply_correction(self):
        print(f'Correction started...')
        corrected_sequences = []

        for frame_info in self.video.flashes:
            algorithm = self.choose_algorithm(frame_info[0])
            corrected_sequence = algorithm(frame_info) # Change correction method
            corrected_sequences.append(corrected_sequence)
        #print('from apply_Correction', corrected_sequences)
        self.save(corrected_sequences)
        print()

    def save(self, corrected_sequences):
        corrected = cv2.VideoWriter(self.output_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.video.FPS,
                                    (self.video.video_width, self.video.video_height))
        first_part = self.video.get_frame_interval((0, self.video.flashes[0][1]))
        for frame in first_part:
            corrected.write(frame)

        for (i, corrected_sequence) in zip(range(len(self.video.flashes)), corrected_sequences):
            for frame in corrected_sequence:
                corrected.write(frame)

            next_interval = (self.video.flashes[i][2], self.video.flashes[i + 1][1] if (i + 1) < len(self.video.flashes) else self.video.frame_count)
            next_part = self.video.get_frame_interval(next_interval)
            for frame in next_part:
                corrected.write(frame)

        corrected.release()

def analysis(video_path, show_live_chart=False, show_dsp=False, show_analysis=False):
    print(f'Video analysis started...')
    analysis_start_time = time.time()
    analysis_result = w3c_guideline.analyse_file(video_path, show_live_chart=show_live_chart,
                                                 show_dsp=show_dsp, show_analysis=show_analysis)
    print(f'\nAnalysis took {(time.time() - analysis_start_time):.3f} seconds.')
    return analysis_result

def frame_intervals(result):
    if len(result.keys()) == 0:
        print("video is oky")
        return

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

def compare(original_video, corrected_video):
    pass

def hsv_to_bgr(hsv, bgr):
    for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
        bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)

if __name__ == "__main__":
    original_video_path = 'output_folder/pexels-i̇brahimacikgozart-15346791-1280x720-60fps_noised.avi'
    # sequence_corrected_video_path = "sequence_corrected_video.avi"
    # sequence_video_path = "sequence_video.avi"
    corrected_video_path = "corrected_video.avi"

    original_video = CustomVideo(original_video_path)
    original_video.analyse_video()

    correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
    correction_engine.apply_correction()
    # apply_correction_on_video(original_video, corrected_video_path) # Generates corrected video on given path

    corrected_video = CustomVideo(corrected_video_path)
    corrected_video.analyse_video()
