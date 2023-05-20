import time

from PhotosensitivitySafetyEngine.guidelines.w3c import *
from epileptic_seizure_trigger import *

def average_correction(video_sequence, FPS, frame_count, interval=15):
    average_interval = int(FPS // interval)
    corrected_sequence = video_sequence.copy()
    for i in range(0, frame_count):
        lower = i - average_interval if i - average_interval > 0 else 0
        upper = i + average_interval if i + average_interval < frame_count else frame_count
        corrected_sequence[i] = np.average(video_sequence[lower:upper], axis=0)
    return corrected_sequence


def gaussian_blur_correction(video_sequence, FPS, frame_count, interval=3):
    average_interval = int(FPS // interval)
    red_lower = (0, 0, 200)
    red_upper = (100, 100, 255)

    corrected_sequence = video_sequence.copy()
    for i in range(0, frame_count):
        lower = i - average_interval if i - average_interval > 0 else 0
        upper = i + average_interval if i + average_interval < frame_count else frame_count
        corrected_sequence[i] = np.average(video_sequence[lower:upper], axis=0)
        mask_red = cv2.inRange(corrected_sequence[i], red_lower, red_upper)
        # Maskeyi uygula
        corrected_sequence[i] = cv2.bitwise_and(corrected_sequence[i], corrected_sequence[i], mask=mask_red)

    return corrected_sequence


def apply_average_correction_on_video(original_video, output_path, interval=2):
    print(f'Correction started...')
    corrected_sequences = []
    now = time.time()
    for frame_info in original_video.flashes:
        if frame_info[0] == 'general':
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(
                frame_info[1], frame_info[2])
            corrected_sequence = average_correction(BGR_sequence, FPS, frame_count,
                                                    interval=interval)  # Change correction method
            corrected_sequences.append(corrected_sequence)
        else:
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(
                frame_info[1], frame_info[2])
            corrected_sequence = average_correction(BGR_sequence, FPS, frame_count,
                                                    interval=interval)  # Change correction method
            corrected_sequences.append(corrected_sequence)
    print(f"Correction passed {time.time() - now} seconds")
    write_corrected_sequences(original_video, corrected_sequences, output_path)


def apply_gaussian_correction_on_video(original_video, output_path):
    print(f'Correction started...')
    corrected_sequences = []
    now = time.time()
    for frame_info in original_video.flashes:
        if frame_info[0] == 'general':
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(
                frame_info)
            corrected_sequence = gaussian_blur_correction(BGR_sequence, FPS, frame_count)  # Change correction method
            corrected_sequences.append(corrected_sequence)
        else:
            FPS, frame_count, original_sequence, BGR_sequence, HSV_sequence = original_video.read_video_sequence(
                frame_info)
            corrected_sequence = gaussian_blur_correction(BGR_sequence, FPS, frame_count)  # Change correction method
            corrected_sequences.append(corrected_sequence)
    print(f"Correction passed {time.time() - now} seconds")
    write_corrected_sequences(original_video, corrected_sequences, output_path)


def write_corrected_sequences(original_video, corrected_sequences, output_path):
    corrected = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), original_video.FPS,
                                (original_video.video_width, original_video.video_height))
    if not len(original_video.flashes):
        for frame in original_video.get_frame_interval((0, original_video.frame_count)):
            corrected.write(frame)
        return
    first_part = original_video.get_frame_interval(0, original_video.flashes[0][1])

    for frame in first_part:
        corrected.write(frame)

    for (i, corrected_sequence) in zip(range(len(original_video.flashes)), corrected_sequences):
        for frame in corrected_sequence:
            corrected.write(frame)
        next_interval = (original_video.flashes[i][2], original_video.flashes[i + 1][1] if (i + 1) < len(
            original_video.flashes) else original_video.frame_count)
        next_part = original_video.get_frame_interval(next_interval[0], next_interval[1])
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
    original_video_path = 'Seizure_Warning.mp4'
    corrected_video_path = "corrected_video.avi"
    corrected_video_path_second = "corrected_video_second.avi"

    video_original = CustomVideo(original_video_path)
    video_original.analyse_video(False)
    for f in video_original.flashes:
        print(f)
    exit(0)
    apply_average_correction_on_video(video_original, corrected_video_path)
    video_corrected = CustomVideo(corrected_video_path)

    # print(video_corrected.flashes)
    video_corrected.analyse_video()

# def analysis(video_path, show_live_chart=False, show_dsp=False, show_analysis=True):
#     print(f'Video analysis started...')
#     analysis_start_time = time.time()
#     analysis_result = w3c_guideline.analyse_file(video_path, show_live_chart=show_live_chart,
#                                                  show_dsp=show_dsp, show_analysis=show_analysis)
#     print(f'\nAnalysis took {(time.time() - analysis_start_time):.3f} seconds.')
#     return analysis_result


# def hsv_to_bgr(hsv, bgr):
#     for (idx_HSV, idx_BGR) in zip(range(len(hsv)), range(len(bgr))):
#         bgr[idx_BGR] = cv2.cvtColor(hsv[idx_HSV], cv2.COLOR_HSV2BGR)
#
#
# def low_pass_filter(adata: np.ndarray, bandlimit: int = 3, sampling_rate: int = 30) -> np.ndarray:
#     # translate bandlimit from Hz to dataindex according to sampling rate and data size
#     bandlimit_index = int(bandlimit * adata.size / sampling_rate)
#     fsig = np.fft.fft(adata)
#
#     for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
#         fsig[i] = 0
#
#     adata_filtered = np.fft.ifft(fsig)
#
#     return np.real(adata_filtered)

# def frame_intervals(result):
#     is_general, is_red = False, False
#     general_start, red_start = None, None
#
#     flashes = []
#
#     for i, (general, red) in enumerate(zip(result["General Flashes"], result["Red Flashes"])):
#         if general - red > THRESHOLD and not is_general and not is_red:
#             is_general = True
#             general_start = i
#         elif general - red < THRESHOLD and is_general and not is_red:
#             is_general = False
#             flashes.append(('general', general_start, i))
#
#         if red > THRESHOLD and not is_red and not is_general:
#             is_red = True
#             red_start = i
#         elif red < THRESHOLD and is_red and not is_general:
#             is_red = False
#             flashes.append(('red', red_start, i))
#
#     print("Frame Interval Results")
#     print("Flashes", flashes)
#
#     return flashes


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
