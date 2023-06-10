import sys
from comparation_engine import *

if len(sys.argv) != 4:
    print("--> Help")
    print("--> -f folder_path output_path")
    print("corrects all videos in a folder and creates corrected videos in output_path")
    print("--> -v video_path output_path")
    print("corrects video and creates corrected video in output_path")
    print("--> -fa folder_path output_path")
    print("corrects all videos in a folder and creates corrected videos in output_path also creates photo for analyses")
    print("--> -v video_path output_path")
    print("corrects video and creates corrected video in output_path also creates photo for analyses")
    sys.exit(0)

if sys.argv[1] == '-f':
    folder_path = sys.argv[2]
    if not os.path.exists(folder_path):
        print("The folder does not exists !")
        sys.exit(0)
    output_path = sys.argv[3]
    if not os.path.exists(output_path):
        # Dosya yolu yoksa, o dosya yolunu oluşturur
        os.makedirs(output_path)
        print(f"'{output_path}' created!")
    analyse_folder(folder_path, output_path)
elif sys.argv[1] == '-v':
    video_path = sys.argv[2]
    if not os.path.exists(video_path):
        print("The file does not exists !")
        sys.exit(0)
    output_path = sys.argv[3]
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    analyse_video(video_path, output_path)
elif sys.argv[1] == '-fa':
    folder_path = sys.argv[2]
    if not os.path.exists(folder_path):
        print("The folder does not exists !")
        sys.exit(0)
    output_path = sys.argv[3]
    if not os.path.exists(output_path):
        # Dosya yolu yoksa, o dosya yolunu oluşturur
        os.makedirs(output_path)
        print(f"'{output_path}' created!")
    analyse_folder(folder_path, output_path,True)
elif sys.argv[1] == '-va':
    video_path = sys.argv[2]
    if not os.path.exists(video_path):
        print("The file does not exists !")
        sys.exit(0)
    output_path = sys.argv[3]
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    analyse_video(video_path, output_path, True)
else:
    print("--> Help")
    print("--> -f folder_path output_path")
    print("corrects all videos in a folder and creates corrected videos in output_path")
    print("--> -v video_path output_path")
    print("corrects video and creates corrected video in output_path")
    print("--> -fa folder_path output_path")
    print("corrects all videos in a folder and creates corrected videos in output_path also creates photo for analyses")
    print("--> -va video_path output_path")
    print("corrects video and creates corrected video in output_path also creates photo for analyses")
    sys.exit(0)
sys.exit(0)
