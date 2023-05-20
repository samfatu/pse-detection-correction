import sys, os, math, random
import cv2
import numpy as np
import matplotlib.pyplot as plt

# TODO: Correection yapıldıktan sonra her flash sekansının başını düzeltmeyi kaçırıyor

def add_noise_red(frames, fps):
    flash_freq = 8  # Yanıp sönme frekansı (saniyede bir defa)
    flash_frame_interval = int(fps / flash_freq)  # Yanıp sönme aralığı
    noised_frames = []
    for i in range(len(frames)):
        frame = frames[i]
        # Her 'flash_frame_interval' frame'de, bir flash efekti uygula
        if i % flash_frame_interval == 0:
            # Kırmızı flash için, B ve G kanallarını azalt
            frame[:, :, 0] = frame[:, :, 0] * 0.5  # B
            frame[:, :, 1] = frame[:, :, 1] * 0.5  # G
        noised_frames.append(frame)
    return noised_frames


def add_noise_flash(frames, fps):
    flash_freq = 10 # Yanıp sönme frekansı (saniyede bir defa)
    flash_frame_interval = int(fps / flash_freq)  # Yanıp sönme aralığı
    noised_frames = []
    for i in range(len(frames)):
        frame = frames[i]
        # Her 'flash_frame_interval' frame'de, bir flash efekti uygula
        if i % flash_frame_interval == 0:
            # Genel flash için, tüm kanalları artır
            frame = cv2.add(frame, np.array([50.0]))
        noised_frames.append(frame)
    return noised_frames


def main():
    print(sys.argv)
    input_folder, output_folder = sys.argv[1:3]
    files = os.listdir(input_folder)
    for file in files:
        video_name = file.split(".")[0]
        video_info_file = open(f"{output_folder}/{video_name}_info.txt", "w+")
        print("Processing video: ", file)
        capture = cv2.VideoCapture(f"{input_folder}/{file}")
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(capture.get(cv2.CAP_PROP_FPS))
        video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        noise_span = (fps / 3) * 12  # 4
        start_frame = 0

        video_frames = []
        for _ in range(frame_count):
            check, frame = capture.read()
            video_frames.append(frame)
        while start_frame < frame_count - noise_span:
            start_frame = random.randint(start_frame, frame_count - noise_span)
            end_frame = start_frame + int(noise_span)
            if round(random.random()) == 0:
                print("adding red flashes between frames: ", start_frame, end_frame)
                print(start_frame / fps, end_frame / fps, " (in seconds)")
                print(f"red:{start_frame}-{end_frame}", file=video_info_file)
                noised_sequence = add_noise_red(video_frames[start_frame:end_frame], fps)
            else:
                print("adding general flashes between frames: ", start_frame, end_frame)
                print(start_frame / fps, end_frame / fps, " (in seconds)")
                print(f"general:{start_frame}-{end_frame}", file=video_info_file)
                noised_sequence = add_noise_flash(video_frames[start_frame:end_frame], fps)
            for i in range(end_frame - start_frame):
                video_frames[start_frame + i] = noised_sequence[i]
            start_frame = end_frame

        noised_video = cv2.VideoWriter(f'{output_folder}/{video_name}_noised.avi',
                                       cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                       fps, (video_width, video_height))

        for frame in range(frame_count):
            noised_video.write(video_frames[frame])

        noised_video.release()
        video_info_file.close()


if __name__ == "__main__":
    main()
