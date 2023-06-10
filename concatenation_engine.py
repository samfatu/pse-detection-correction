from moviepy.editor import VideoFileClip, clips_array
import cv2
import numpy as np


def join_videos_side_by_side_moviepy(video1_path, video2_path, output_path):
    # Load the video clips
    video1 = VideoFileClip(video1_path)
    video2 = VideoFileClip(video2_path)

    # Resize the videos to have the same height
    video1 = video1.resize(height=video2.h)

    # Place the videos side by side
    final_video = clips_array([[video1, video2]])

    # Set the output video file path and save the final video
    final_video.write_videofile(output_path, codec='libx264')

    # Close the video clips
    video1.close()
    video2.close()


def join_videos_side_by_side_cv2(video_path1, video_path2, output_path):
    # Open the two videos
    video1 = cv2.VideoCapture(video_path1)
    video2 = cv2.VideoCapture(video_path2)

    # Get the properties of videos (frame width, height and FPS)
    frame_width = int(video1.get(cv2.CAP_PROP_FRAME_WIDTH) + video2.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = max(int(video1.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(video2.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fps = min(video1.get(cv2.CAP_PROP_FPS), video2.get(cv2.CAP_PROP_FPS))

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    percent = 0
    while True:
        ret1, frame1 = video1.read()
        ret2, frame2 = video2.read()

        # If both frames were successfully read
        if ret1 and ret2:
            # Resize frames
            frame1 = cv2.resize(frame1, (int(video1.get(cv2.CAP_PROP_FRAME_WIDTH)), frame_height))
            frame2 = cv2.resize(frame2, (int(video2.get(cv2.CAP_PROP_FRAME_WIDTH)), frame_height))

            # Concatenate horizontally (i.e., on the x-axis)
            output_frame = np.concatenate((frame1, frame2), axis=1)
            out.write(output_frame)
        else:
            break
        percent += 1
    # Release everything
    video1.release()
    video2.release()
    out.release()


def concatenate_images(image_left_path, image_right_path, concatenated_image_name):
    # Resimleri okuma
    img1 = cv2.imread(image_left_path)
    img2 = cv2.imread(image_right_path)

    # İki resmi yatay olarak birleştirme
    combined_img = cv2.hconcat([img1, img2])

    # Birleşik resmi kaydetme
    cv2.imwrite(concatenated_image_name, combined_img)