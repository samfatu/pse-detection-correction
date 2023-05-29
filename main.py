import os
import numpy as np
import matplotlib.pyplot as plt
from custom_video import CustomVideo
from correction_engine import CorrectionEngine
from concatenate_videos import join_videos_side_by_side

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
        corrected_video_path = f"./corrected_folder/{file.strip('.mp4')}.avi"
        print(f"{path}/{file}")
        original_video = CustomVideo(f"{path}/{file}")
        original_video.analyse_video()

        correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
        correction_engine.apply_correction()
        # apply_correction_on_video(original_video, corrected_video_path) # Generates corrected video on given path

        corrected_video = CustomVideo(corrected_video_path)
        corrected_video.analyse_video()

        compare(original_video, corrected_video)
        join_videos_side_by_side(f"{path}/{file}",corrected_video_path, f"./concatenated2/{file.strip('.mp4')}.mp4")


if __name__ == "__main__":
    # original_video_path = './input_folder/1.mp4'
    # corrected_video_path = "./corrected_folder/1.avi"

    # original_video = CustomVideo(original_video_path)
    # original_video.analyse_video()

    # correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
    # correction_engine.apply_correction()

    # corrected_video = CustomVideo(corrected_video_path)
    # corrected_video.analyse_video()

    # compare(original_video, corrected_video)
    analyse_folder()