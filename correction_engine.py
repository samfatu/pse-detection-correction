from custom_video import CustomVideo
from PhotosensitivitySafetyEngine.guidelines.w3c import *

class CorrectionEngine:
    def __init__(self, video:CustomVideo, output_path:str):
        self.video = video
        self.output_path = output_path

    # def low_pass_filter(self, adata: np.ndarray, bandlimit: int = 3, sampling_rate: int = 30) -> np.ndarray:
    #     # translate bandlimit from Hz to dataindex according to sampling rate and data size
    #     bandlimit_index = int(bandlimit * adata.size / sampling_rate)
    #     fsig = np.fft.fft(adata)

    #     for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
    #         fsig[i] = 0

    #     adata_filtered = np.fft.ifft(fsig)

    #     return np.real(adata_filtered)

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