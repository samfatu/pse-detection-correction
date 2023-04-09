import sys, os, math, random
import cv2
import numpy as np
import matplotlib.pyplot as plt

def add_noise_flash(sequence):
    #generate sinwave with freq between 3-6 hz
    #only affect smaller rectangle
    #get fps as param
    #add random phase to sin wave
    samples = np.linspace(0, 2 * np.pi * 3 * 24, len(sequence))
    sin_wave = 128 * np.sin(samples)
    noised_sequence = []
    for i, frame in enumerate(sequence):
        frame = frame.astype(np.float64)
        frame += sin_wave[i]
        frame = frame.astype(np.uint8)
        noised_sequence.append(frame)
    return noised_sequence

def add_noise_red():
    pass

def add_noise(capture, is_flash):
    pass

def main():
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
        noise_span =  (fps / 3) * 12#4
        start_frame = 0

        video_frames = []
        for _ in range(frame_count):
            check, frame = capture.read()
            video_frames.append(frame)
        while start_frame < frame_count - noise_span:
            start_frame = random.randint(start_frame, frame_count - noise_span)
            end_frame = start_frame + int(noise_span)
            print("adding noise between frames: ", start_frame, end_frame)
            print(f"general:{start_frame}-{end_frame}", file=video_info_file)

            print(start_frame/fps, end_frame/fps, " (in seconds)")
            #add noise
            noised_sequence = add_noise_flash(video_frames[start_frame:end_frame])
            for i in range(end_frame - start_frame):
                video_frames[start_frame + i] = noised_sequence[i]
            start_frame = end_frame

        noised_video = cv2.VideoWriter(f'{output_folder}/{video_name}_noised.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                        fps, (video_width, video_height))

        for frame in range(frame_count):
            noised_video.write(video_frames[frame])

        noised_video.release()
        video_info_file.close()


if __name__ == "__main__":
    main()