from moviepy.editor import VideoFileClip, clips_array

def join_videos_side_by_side(video1_path, video2_path, output_path):
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

# Provide the file paths and output path
video1_path = "./input_folder/pokemon.mp4"
video2_path = "./corrected_folder/okemon_corrected.avi"
output_path = "./concatenated/pokemon.mp4"

# Call the function to join videos side by side and save the result
join_videos_side_by_side(video1_path, video2_path, output_path)