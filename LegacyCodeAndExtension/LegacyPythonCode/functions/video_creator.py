import numpy as np
from cv2 import cv2

import help_functions

video_name = 'path'
video = cv2.VideoWriter(video_name, 0, 30, (1024, 768))

# frame1 = np.array([[(255,255,255), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]*3]*4, dtype='uint8')
# frame2 = np.array([[(255,255,255), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]*3+[(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]]*3+[[(0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]*4], dtype='uint8')

count = 0
# while count < 100:
#     count += 1
#     print(count)
#     print(frame1)
#     image = np.zeros((768, 1024, 3), np.uint8)
#     if count % 2 == 1:
#         image = cv2.resize(frame2, (1024, 768), interpolation=cv2.INTER_NEAREST)
#     video.write(image)
#     functions.help_functions.display_content(image, max_value=255)
#     functions.help_functions.display_content(frame2, max_value=255)
#     functions.help_functions.display_content(frame1, max_value=255)
#     cv2.waitKey(1)


while count < 100:
    count += 1
    print(count)
    image = np.zeros((768, 1024, 3), np.uint8)
    if count % 4 < 2:
        image[:] = (255, 0, 0)
    else:
        image[:] = (0, 96, 0)
    video.write(image)
    # CAPTURE IS GETTING (255 14 0) and (0 80 0)
    # FILE IS GETTING (250 0 0) and (0 94 0)
#
# while count < 200:
#     count += 1
#     print(count)
#     image = np.zeros((768, 1024, 3), np.uint8)
#     if count % 4 < 2:
#         image[:] = (150, 150, 150)
#     else:
#         image[:] = (80, 115, 255)
#     video.write(image)
#     # CAPTURE IS GETTING (149 149 146) and (73 126 255)
#     # FILE IS GETTING (146 149 147) and (77 114 252)
#
#
# while count < 300:
#     count += 1
#     print(count)
#     image = np.zeros((768, 1024, 3), np.uint8)
#     if count % 4 < 2:
#         image[:] = (0, 90, 180)
#     else:
#         image[:] = (50, 0, 255)
#     video.write(image)
#     # CAPTURE IS GETTING (0 92 255) and (47 27 255)
#     # FILE IS GETTING (0 88 176) and (48 0 253)
#
# video.release()
