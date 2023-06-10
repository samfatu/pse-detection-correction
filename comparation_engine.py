import os
from custom_video import CustomVideo
from correction_engine import CorrectionEngine
from concatenation_engine import *


def compare(original_video, corrected_video):
    original_total_flash, corrected_total_flash = original_video.flashing_frame_count, corrected_video.flashing_frame_count
    original_percentage = original_total_flash / original_video.frame_count
    corrected_percentage = corrected_total_flash / original_video.frame_count
    if original_percentage:
        return f'---------------------------------------VIDEO INFO\n' \
               f'Original Video Path : {original_video.video_path}, ' \
               f'Corrected Video Path : {corrected_video.video_path}\n' \
               f'Original Video FPS : {original_video.FPS}, Corrected Video FPS : {corrected_video.FPS}\n' \
               f'Original Video Codec : {original_video.codec}, Corrected Video Codec : {corrected_video.codec}\n\n' \
               f'---------------------------------------PERCENTAGE INFO\n' \
               f'Original seizure percentage: {original_percentage * 100 :.2f}% \n' \
               f'Corrected seizure percentage: {corrected_percentage * 100 :.2f}% \n' \
               f'Video is corrected by ' \
               f'{((original_percentage - corrected_percentage) / original_percentage) * 100 :.2f}%\n\n' \
               f'---------------------------------------FLASH FRAME INTERVAL INFO\n' \
               f'Original flashes : {original_video.flashes}\n' \
               f'Corrected flashes : {corrected_video.flashes}'
    else:
        return f'Video is not corrupted already'


def analyse_folder(input_path, output_path,analysis_output=False):
    files = [f for f in os.listdir(input_path) if not f.startswith('.')]
    if not os.path.exists("./corrected_folder"):
        # Dosya yolu yoksa, o dosya yolunu oluşturur
        os.makedirs("./corrected_folder")
        print("./corrected_folder created!")
    for file in files:
        corrected_video_path = f"./corrected_folder/{file.strip('.mp4')}.avi"
        print(f"{input_path}/{file}")
        original_video = CustomVideo(f"{input_path}/{file}")
        if analysis_output:
            original_video.analyse_video(save_path=f"{output_path}/{file.strip('.mp4')}_original.png")
        else:
            original_video.analyse_video()
        print(f"original FPS {original_video.FPS}")
        correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
        correction_engine.apply_correction()

        corrected_video = CustomVideo(corrected_video_path)
        corrected_video.analyse_video()
        if analysis_output:
            corrected_video.analyse_video(save_path=f"{output_path}/{file.strip('.mp4')}_corrected.png")
        else:
            corrected_video.analyse_video()

        compare_output = compare(original_video, corrected_video)
        with open(f"{output_path}/{file.strip('.mp4')}.txt", 'w+') as f:
            print(compare_output, file=f)
        if analysis_output:
            concatenate_images(f"{output_path}/{file.strip('.mp4')}_original.png",
                               f"{output_path}/{file.strip('.mp4')}_corrected.png",
                               f"{output_path}/{file.strip('.mp4')}_both.png")

        print(f"corrected FPS {corrected_video.FPS}")
        join_videos_side_by_side_cv2(f"{input_path}/{file}", corrected_video_path,
                                     f"{output_path}/{file}")
def analyse_video(input_video_path, output_path, analysis_output=False):
    if not os.path.exists("./corrected_folder"):
        # Dosya yolu yoksa, o dosya yolunu oluşturur
        os.makedirs("./corrected_folder")
        print("./corrected_folder created!")

    original_video = CustomVideo(input_video_path)
    if analysis_output:
        original_video.analyse_video(save_path=f"{output_path}/original_video_analysis.png")
    else:
        original_video.analyse_video()

    corrected_video_path = f"./corrected_folder/corrected_video.mp4"
    correction_engine = CorrectionEngine(video=original_video, output_path=corrected_video_path)
    correction_engine.apply_correction()

    corrected_video = CustomVideo(corrected_video_path)
    if analysis_output:
        corrected_video.analyse_video(save_path=f"{output_path}/corrected_video_analysis.png")
    else:
        corrected_video.analyse_video()
    compare_output = compare(original_video, corrected_video)

    if analysis_output:
        concatenate_images(f"{output_path}/original_video_analysis.png", f"{output_path}/corrected_video_analysis.png",
                           f"{output_path}/analysis_both.png")
    with open(f"{output_path}/correction_info.txt", 'w+') as f:
        print(compare_output, file=f)
    join_videos_side_by_side_cv2(input_video_path, corrected_video_path,
                                 f"{output_path}/concatenated_video.mp4")
