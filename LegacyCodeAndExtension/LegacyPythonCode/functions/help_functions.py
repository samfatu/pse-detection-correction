import traceback
import cv2.cv2 as cv2
import numpy as np


def display_content(display_frame, max_value=1):
    stack = traceback.extract_stack()
    display_name = stack[-2][3].replace(' ', '').replace('(', ',').replace(')', '').split(',')[1]
    display_frame_8bit = np.array(np.multiply(display_frame, 255 / max_value), dtype=np.uint8)
    cv2.imshow(display_name, display_frame_8bit)


def combine_images(display_frames):
    add_background = display_frames + [np.zeros((225, 300))]
    return np.maximum.reduce(add_background)
