from cv2 import cv2
import config
from w3c_guidelines.colour_equations import relative_luminance as w3c_rl
from w3c_guidelines.colour_equations import red_saturation as w3c_rs
from w3c_guidelines.general_flash_and_red_flash_thresholds import general_flash_thresholds as w3c_gft
from w3c_guidelines.general_flash_and_red_flash_thresholds import red_flash_thresholds as w3c_rft
from w3c_guidelines.general_flash_and_red_flash_thresholds import area_of_flashes as w3c_aof
from w3c_guidelines.general_flash_and_red_flash_thresholds import pair_of_opposing_changes as w3c_pooc
from w3c_guidelines.general_flash_and_red_flash_thresholds import screen_viewing as w3c_sv


def run(filename):
    print(filename)
    # INITIALISE ZEROS
    previous_relative_luminance = 0
    previous_red_saturation = 0
    previous_red_majority = 0
    recent_general_changes = (0.0, 0.0)
    recent_red_changes = (0.0, 0.0)
    frame_count = 0
    general_flashes_list = []
    red_flashes_list = []

    capture = cv2.VideoCapture(filename)

    while True:
        # GET NEW FRAME
        frame_count += 1
        # print(time.time())
        check, frame = capture.read()
        if not check:
            # END CAPTURE AND MONITORS
            capture.release()
            break
        GitHub.Other.Python.functions.help_functions.display_content(frame, max_value=255)
        # CALCULATIONS
        # render the frame onto a screen
        rendered_frame = w3c_sv.render_onto_display(frame, w3c_sv.frame_shape)
        # smaller frame for calculations
        # TODO: this should come from small flash exception
        # TODO: pass aspect ratio and grain
        # TODO: pick between frame render and manual shape data
        rendered_frame = cv2.resize(rendered_frame, (300, 225))
        GitHub.Other.Python.functions.help_functions.display_content(rendered_frame, max_value=255)
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
        general_flashes_list.extend(general_detected_flashes)
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
        red_flashes_list.extend(red_detected_flashes)
        # REMEMBER LAST FRAME
        previous_relative_luminance = relative_luminance
        previous_red_saturation = red_saturation
        previous_red_majority = red_majority
    ret_list = []
    for fl in general_flashes_list+red_flashes_list:
        ret_list.append((fl.flash_type, fl.start_frame, fl.end_frame))
        # print(fl.flash_type, fl.start_frame, fl.end_frame)
    return ret_list


if __name__ == '__main__':
    run('/Media/Pokemon.mp4')
