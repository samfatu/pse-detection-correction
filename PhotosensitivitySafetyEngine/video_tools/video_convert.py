import os
import numpy as np
from PIL import Image
from cv2 import cv2


def convert_to_peat(address_in):
    # PEAT ONLY WORKS WITH UNCOMPRESSED 1024x768 30FPS AVI VIDEOS
    address_out = os.path.splitext(address_in)[0]+'_peat.avi'
    writer = cv2.VideoWriter(address_out, 0, 30, (1024, 768))
    capture = cv2.VideoCapture(address_in)
    for i in range(900):
        check, frame = capture.read()
        if not check:
            break
        frame2 = cv2.resize(frame, (1024, 768))
        writer.write(frame2)
    writer.release()


def images_to_peat(address_in):
    image_list = [cv2.imread(os.path.join(address_in, f)) for f in os.listdir(address_in)]
    print(image_list)
    address_out = os.path.splitext(address_in)[0]+'/peat.avi'
    writer = cv2.VideoWriter(address_out, 0, 30, (1024, 768))
    for i in range(300):
        print(i)
        frame = np.array(image_list[i % len(image_list)])
        frame2 = cv2.resize(frame, (1024, 768))
        writer.write(frame2)
    writer.release()
