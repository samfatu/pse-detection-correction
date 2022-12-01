from cv2 import cv2

address = 'path'
name = address.replace('/', '.').split('.')[-2]
z
capture = cv2.VideoCapture(address)

check, frame = capture.read()
height, width, _ = frame.shape
video_name = 'path'+name+'.avi'
video = cv2.VideoWriter(video_name, 0, 30, (1024, 768))

while check:
    print('one')
    # GET NEW FRAME
    frame2 = cv2.resize(frame, (1024, 768))
    video.write(frame2)
    check, frame = capture.read()
video.release()
