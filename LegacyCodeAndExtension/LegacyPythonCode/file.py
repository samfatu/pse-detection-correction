import numpy as np
from cv2 import cv2
import config
from w3c_guidelines.colour_equations import relative_luminance as w3c_rl
from w3c_guidelines.colour_equations import red_saturation as w3c_rs
from w3c_guidelines.general_flash_and_red_flash_thresholds import general_flash_thresholds as w3c_gft
from w3c_guidelines.general_flash_and_red_flash_thresholds import red_flash_thresholds as w3c_rft
from w3c_guidelines.general_flash_and_red_flash_thresholds import area_of_flashes as w3c_aof
from w3c_guidelines.general_flash_and_red_flash_thresholds import screen_viewing as w3c_sv
from w3c_guidelines.aggregating_functions import aggregation as w3c_ag
import matplotlib.pyplot as plt


def run(filename):
    print(filename)
    # INITIALISE ZEROS
    previous_relative_luminance = 0
    previous_red_saturation = 0
    previous_red_majority = 0
    frame_count = 0
    general_flashes_lighter = []
    general_flashes_darker = []
    general_flashes_counter = []
    red_flashes_lighter = []
    red_flashes_darker = []
    red_flashes_counter = []

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
        relative_luminance = w3c_rl.calculate_relative_luminance(frame)
        general_limits = w3c_gft.general_limits(relative_luminance, previous_relative_luminance)
        general_flashes_lighter.append(np.max(w3c_aof.find_all_rectangle_sums(general_limits[0])))
        general_flashes_darker.append(np.max(w3c_aof.find_all_rectangle_sums(general_limits[1])))
        general_flashes_counter.append(w3c_ag.count_flashes(general_flashes_lighter, general_flashes_darker, config.frame_rate))
        # RED FLASHES
        # detect changes in saturated red
        red_saturation = w3c_rs.calculate_red_saturation(frame)
        print(sum(red_saturation))
        red_majority = w3c_rs.calculate_red_majority(frame)
        print(sum(red_majority))
        red_change_limits = w3c_rft.red_saturation_limits(red_saturation, previous_red_saturation, red_majority, previous_red_majority)
        print(sum(red_change_limits[0]))
        print(sum(red_change_limits[1]))
        red_flashes_lighter.append(np.max(w3c_aof.find_all_rectangle_sums(red_change_limits[0])))
        red_flashes_darker.append(np.max(w3c_aof.find_all_rectangle_sums(red_change_limits[1])))
        red_flashes_counter.append(w3c_ag.count_flashes(red_flashes_lighter, red_flashes_darker, config.frame_rate))
        # REMEMBER LAST FRAME
        previous_relative_luminance = relative_luminance
        previous_red_saturation = red_saturation
        previous_red_majority = red_majority
    print(general_flashes_lighter)
    print(general_flashes_darker)
    print(red_flashes_lighter)
    print(red_flashes_darker)
    plt.plot(np.arange(len(general_flashes_counter)) / config.frame_rate, general_flashes_counter)
    plt.plot(np.arange(len(general_flashes_counter)) / config.frame_rate, red_flashes_counter)
    plt.plot(np.arange(len(general_flashes_counter)) / config.frame_rate, [3] * len(general_flashes_counter))
    plt.ylabel('Flash Counts')
    plt.show()
    return None


if __name__ == '__main__':
    print(run('/MediaOut/video.avi'))
