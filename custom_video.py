import time
from PhotosensitivitySafetyEngine.guidelines.w3c import *

THRESHOLD = 1
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
        self.analysis_result = self.analysis(self.video_path)
        self.flashes = self.frame_intervals(self.analysis_result)
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


    @property
    def flashing_frame_count(self):
        count = 0
        for _,start,end in self.flashes:
            count += end - start
        return count

    def analysis(self, video_path, show_live_chart=False, show_dsp=False, show_analysis=False):
      print(f'Video analysis started...')
      analysis_start_time = time.time()
      analysis_result = w3c_guideline.analyse_file(video_path, show_live_chart=show_live_chart,
                                                  show_dsp=show_dsp, show_analysis=show_analysis)
      print(f'\nAnalysis took {(time.time() - analysis_start_time):.3f} seconds.')
      return analysis_result

    def frame_intervals(self, result):
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
