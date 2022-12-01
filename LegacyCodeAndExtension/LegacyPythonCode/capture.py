import time
from threading import Thread

import numpy as np
from cv2 import cv2
from mss import mss
import config
from w3c_guidelines.colour_equations import relative_luminance as w3c_rl
from w3c_guidelines.colour_equations import red_saturation as w3c_rs
from w3c_guidelines.general_flash_and_red_flash_thresholds import general_flash_thresholds as w3c_gft
from w3c_guidelines.general_flash_and_red_flash_thresholds import red_flash_thresholds as w3c_rft
from w3c_guidelines.general_flash_and_red_flash_thresholds import area_of_flashes as w3c_aof
from w3c_guidelines.general_flash_and_red_flash_thresholds import pair_of_opposing_changes as w3c_pooc
# from w3c_guidelines.general_flash_and_red_flash_thresholds import screen_viewing as w3c_sv


# INITIALISE ZEROS
previous_relative_luminance = 0
previous_red_saturation = 0
previous_red_majority = 0
recent_general_changes = (0.0, 0.0)
recent_red_changes = (0.0, 0.0)
frame_count = 0
general_flashes_list = []
red_flashes_list = []


# THREADED 1920: 29 FPS
# NORMAL 1920: 17 FPS

# THREADED 4K: 12 FPS
# NORMAL 4K: 7 PFS


def threaded_grab():
    global sct_img
    global sct_fresh
    while True:
        sct_img = sct.grab(monitor)
        sct_fresh = True


sct = mss()
monitor = sct.monitors[1]
sct_img = 0
sct_fresh = False
thread = Thread(target=threaded_grab)
thread.start()
while not sct_fresh:
    pass

while True:
    # GET NEW FRAME
    while not sct_fresh:
        pass
    frame_count += 1
    rendered_frame = np.array(sct_img)[:, :, :3]
    sct_fresh = False
    # CALCULATIONS
    # render the frame onto a screen
    # (useless here)
    # smaller frame for calculations
    # TODO: this should come from small flash exception
    # TODO: pass aspect ratio and grain
    # TODO: pick between frame render and manual shape data
    rendered_frame = cv2.resize(rendered_frame, (300, 225))
    # functions.help_functions.display_content(rendered_frame, max_value=255)
    cv2.waitKey(1)
    # GENERAL FLASHES
    # detect changes in relative luminance
    relative_luminance = w3c_rl.calculate_relative_luminance(rendered_frame)
    general_limits = w3c_gft.general_limits(relative_luminance, previous_relative_luminance)
    # track pairs of opposing relative luminance changes
    recent_general_changes = w3c_pooc.update_last_flashes(recent_general_changes, general_limits, config.frame_rate)
    general_flashes = w3c_pooc.cross_reference_transitions(recent_general_changes, general_limits)
    # interpret pairs of opposing luminance changes
    general_flash_counts = w3c_pooc.flash_frames_separator(general_flashes)
    general_detected_flashes = w3c_aof.detect_flashes(general_flashes, general_flash_counts, frame_count, config.frame_rate, flash_type='general')
    for fl in general_detected_flashes:
        print(fl.flash_type, fl.start_frame, fl.end_frame, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # RED FLASHES
    # detect changes in saturated red
    red_saturation = w3c_rs.calculate_red_saturation(rendered_frame)
    red_majority = w3c_rs.calculate_red_majority(rendered_frame)
    red_change_limits = w3c_rft.red_saturation_limits(red_saturation, previous_red_saturation, red_majority, previous_red_majority)
    # track pairs of opposing red changes
    recent_red_changes = w3c_pooc.update_last_flashes(recent_red_changes, red_change_limits, config.frame_rate)
    red_flashes = w3c_pooc.cross_reference_transitions(recent_red_changes, red_change_limits)
    # interpret pairs of opposing red changes
    red_flash_counts = w3c_pooc.flash_frames_separator(red_flashes)
    red_detected_flashes = w3c_aof.detect_flashes(red_flashes, red_flash_counts, frame_count, config.frame_rate, flash_type='red')
    for fl in red_detected_flashes:
        print(fl.flash_type, fl.start_frame, fl.end_frame, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    # REMEMBER LAST FRAME
    previous_relative_luminance = relative_luminance
    previous_red_saturation = red_saturation
    previous_red_majority = red_majority
    GitHub.Other.Python.functions.help_functions.display_content(relative_luminance)

