import time

from PhotosensitivitySafetyEngine.guidelines.w3c import *

SEIZURE_THRESHOLD = 3


class CustomVideo:
    def __init__(self, video_path):
        self.__video_path = video_path
        self.__capture = cv2.VideoCapture(self.__video_path)
        self.video_width = int(self.__capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.__capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = int(self.__capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.FPS = int(self.__capture.get(cv2.CAP_PROP_FPS))

        self.analysis_result = []
        self.flashes = []

    def analyse_video(self, show_analysis=True):
        print(f'Video analysis started...')
        analysis_start_time = time.time()
        self.analysis_result = w3c_guideline.analyse_file(self.__video_path, show_live_chart=False,
                                                          show_dsp=False, show_analysis=show_analysis)
        print(f'\nAnalysis took {(time.time() - analysis_start_time):.3f} seconds.')
        self.check_frame_intervals(self.analysis_result)

    def read_video_sequence(self, sequence_start, sequence_end):
        frame_count = sequence_end - sequence_start
        self.__capture.set(1, sequence_start)

        BGR_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)
        HSV_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)

        for f in range(frame_count):
            check, frame = self.__capture.read()
            if check:
                HSV_sequence[f] = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                BGR_sequence[f] = frame

        original_sequence = BGR_sequence.copy()

        return self.FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence

    def get_frame_interval(self, interval_start, interval_end):
        self.__capture.set(1, interval_start)
        frame_count = interval_end - interval_start

        if frame_count < 0:
            return None
        BGR_sequence = np.ones((frame_count, self.video_height, self.video_width, 3), dtype=np.uint8)

        for f in range(frame_count):
            check, frame = self.__capture.read()
            if check:
                BGR_sequence[f] = frame

        return BGR_sequence

    def check_frame_intervals(self, analysis_result):
        is_general, is_red, is_all = False, False, False
        general_start, red_start, all_start = 0, 0, 0

        flashes = []

        for i, (general, red) in enumerate(zip(analysis_result["General Flashes"], analysis_result["Red Flashes"])):
            if general - red >= SEIZURE_THRESHOLD and not is_general:
                is_general = True
                general_start = i
            elif general - red < SEIZURE_THRESHOLD and is_general:
                is_general = False
                flashes.append(('general', general_start, i))
            if red >= SEIZURE_THRESHOLD and not is_red:
                is_red = True
                red_start = i
            elif red < SEIZURE_THRESHOLD and is_red:
                is_red = False
                flashes.append(('red', red_start, i))

        if is_general:
            flashes.append(('general', general_start, self.frame_count))
        elif is_red:
            flashes.append(('red', red_start, self.frame_count))

        print("Frame Interval Results")
        print("Flashes", flashes)

        self.flashes = flashes

    def get_flashes(self):
        return self.flashes
