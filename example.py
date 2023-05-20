import numpy as np
import matplotlib.pyplot as plt
from custom_video import CustomVideo
from correction_engine import CorrectionEngine

def compare(original_video, corrected_video):
    pass

if __name__ == "__main__":
    original_video_path = 'ep2.mp4'
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


# def hsv_to_bgr(hsv, bgr):
#     for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
#         bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)