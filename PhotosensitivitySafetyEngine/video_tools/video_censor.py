import os
import cv2


def video_censor(address_in, analysis_result, fallback_frames=None, frames_before=0):
    frames_to_hide = analysis_result
    for i in range(len(analysis_result)):
        if sum(analysis_result[i:min(i+frames_before, len(analysis_result))]):
            frames_to_hide[i] = True
    if fallback_frames is not None:
        for i in range(len(frames_to_hide)):
            if sum(frames_to_hide[max(0, i-fallback_frames):min(i+fallback_frames, len(analysis_result))]) == 2*fallback_frames:
                frames_to_hide[i] = False

    address_out = os.path.splitext(address_in)[0]+'_censored.avi'
    capture = cv2.VideoCapture(address_in)
    writer = cv2.VideoWriter(address_out, 0, int(capture.get(cv2.CAP_PROP_FPS)), (int(capture.get(3)), int(capture.get(4))))
    frame = 0
    for x in frames_to_hide:
        if x:
            _, _ = capture.read()
        else:
            check, frame = capture.read()
        writer.write(frame)
    writer.release()
