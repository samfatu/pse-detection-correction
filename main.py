import os
import numpy as np
import matplotlib.pyplot as plt
from custom_video import CustomVideo
from correction_engine import CorrectionEngine

def compare(original_video, corrected_video):
    original_total_flash, corrected_total_flash = original_video.flashing_frame_count, corrected_video.flashing_frame_count
    original_percentage = original_total_flash / original_video.frame_count
    corrected_percentage = corrected_total_flash / original_video.frame_count
    if original_percentage:
        print(f'Original perc: {original_percentage * 100 :.2f}% Corrected Perc: {corrected_percentage * 100 :.2f}%')
        print(f'Video is corrected by {((original_percentage - corrected_percentage) / original_percentage) * 100 :.2f}%')
    else:
        print(f'Video is not corrupted already')


def analyse_folder(path='./input_folder'):
    files = [f for f in os.listdir(path) if not f.startswith('.')]

    for file in files:
        corrected_video_path = f"./corrected_folder/{file.strip('.mp4')}_corrected.avi"
        print(f"{path}/{file}")
        original_video = CustomVideo(f"{path}/{file}")
        original_video.analyse_video()

        correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
        correction_engine.apply_correction()
        # apply_correction_on_video(original_video, corrected_video_path) # Generates corrected video on given path

        corrected_video = CustomVideo(corrected_video_path)
        corrected_video.analyse_video()

        compare(original_video, corrected_video)


if __name__ == "__main__":
    analyse_folder()

    # original_video_path = './input_folder/pokemon.mp4'
    # # sequence_corrected_video_path = "sequence_corrected_video.avi"
    # # sequence_video_path = "sequence_video.avi"
    # corrected_video_path = "corrected_video.avi"

    # original_video = CustomVideo(original_video_path)
    # original_video.analyse_video()

    # correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
    # correction_engine.apply_correction()
    # # apply_correction_on_video(original_video, corrected_video_path) # Generates corrected video on given path

    # corrected_video = CustomVideo(corrected_video_path)
    # corrected_video.analyse_video()

    # compare(original_video, corrected_video)


# def hsv_to_bgr(hsv, bgr):
#     for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
#         bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)
