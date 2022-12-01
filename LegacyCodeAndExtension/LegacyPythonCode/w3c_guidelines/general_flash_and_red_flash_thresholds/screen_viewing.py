from cv2 import cv2
import numpy as np

"""
Exception: Flashing that is a fine, balanced, pattern such as white noise or an alternating checkerboard pattern with 
"squares" smaller than 0.1 degree (of visual field at typical viewing distance) on a side does not violate the 
thresholds. 
"""

"""For general software or Web content, using a 341 x 256 pixel rectangle anywhere on the displayed screen area when 
the content is viewed at 1024 x 768 pixels will provide a good estimate of a 10 degree visual field for standard 
screen sizes and viewing distances (e.g., 15-17 inch screen at 22-26 inches). """


display_properties = {'width': 1024, 'height': 768, 'size': 16, 'distance': 24}
# TODO: "10 degree visual field on the screen"
frame_shape = (display_properties['width'], display_properties['height'])
# TODO: first, make this fullHD
# TODO: second, carefully resize first
# frame_shape = (480, 320)
visual_field = (341, 256)

# "25% of any 10 degree visual field on the screen"
# regional_threshold = 0.25
# if below global_minimum_threshold there cannot be any rectangles
# global_minimum_threshold = 0.25 / (frame_shape[0] * frame_shape[1] / visual_field[0] / visual_field[1])


def render_onto_display(frame, display_size, size=None, position=(0, 0), interpolation=cv2.INTER_LINEAR):
    screen = np.zeros((display_size[1], display_size[0], 3))
    if size is None:
        if frame.shape[0]/display_size[1] > frame.shape[1]/display_size[0]:
            size = int(frame.shape[1]/frame.shape[0]*display_size[1]), display_size[1]
            position = int((display_size[0]-size[0])/2), 0
        else:
            size = display_size[0], int(frame.shape[0]/frame.shape[1]*display_size[0])
            position = 0, int((display_size[1]-size[1])/2)
    resized_frame = cv2.resize(frame, size, interpolation=interpolation)
    screen[position[1]:position[1] + size[1], position[0]:position[0] + size[0]] = resized_frame
    return np.array(screen, dtype='uint8')


def resize(frame, shape):
    test_array = np.array([[1, 100], [1, 100]], dtype='uint8')
    horizontal_sum = np.cumsum(test_array, axis=0)
    rectangular_sum = np.array(np.cumsum(horizontal_sum, axis=1), dtype='uint8')
    print(test_array)
    print(rectangular_sum)
    resized_sum = cv2.resize(rectangular_sum, (1+1, 1+1), interpolation=cv2.INTER_LINEAR)
    print(resized_sum)
    resized_sum = np.c_[np.zeros(len(resized_sum)), resized_sum]
    resized_sum = np.r_[[np.zeros(len(resized_sum[0]))], resized_sum]
    horizontal_delta_sum = resized_sum[1:] - resized_sum[:-1]
    delta_sum = horizontal_delta_sum[:, 1:] - horizontal_delta_sum[:, :-1]
    print(delta_sum)
    horizontal_sum = np.cumsum(frame, axis=0)
    rectangular_sum = np.cumsum(horizontal_sum, axis=1)
    resized_sum = cv2.resize(rectangular_sum, shape, interpolation=cv2.INTER_LINEAR)
    print(resized_sum)
