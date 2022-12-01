import numpy as np

"""
or the combined area of flashes occurring concurrently occupies no more than a total of .006 steradians within any 10 
degree visual field on the screen (25% of any 10 degree visual field on the screen) at typical viewing distance 
"""


# TODO: "10 degree visual field on the screen"
# https://www.w3.org/TR/2016/NOTE-WCAG20-TECHS-20161007/G176
frame_shape = (225, 300)
visual_field = (75, 100)

# "25% of any 10 degree visual field on the screen"
regional_threshold = 0.25
# if below global_minimum_threshold there cannot be any rectangles
global_minimum_threshold = 0.25 / (frame_shape[0] * frame_shape[1] / visual_field[0] / visual_field[1])


class Flash:
    def __init__(self, start_frame, end_frame, flash_type):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.flash_type = flash_type


def detect_flashes(both_flashes, flash_counts, frame_count, frame_rate, flash_type=''):
    lighter_darker_flash, darker_lighter_flash = both_flashes
    lighter_darker_flash_counts, darker_lighter_flash_counts = flash_counts
    lighter_darker_flashes = detect_flash(lighter_darker_flash, lighter_darker_flash_counts, frame_count, frame_rate, flash_type+'_DLD')
    darker_lighter_flashes = detect_flash(darker_lighter_flash, darker_lighter_flash_counts, frame_count, frame_rate, flash_type+'_LDL')
    return lighter_darker_flashes + darker_lighter_flashes


def detect_flash(flash, flash_counts, frame_count, frame_rate, flash_type=''):
    regional_flashes_found = []
    for frame_offset in range(len(flash_counts)):
        if flash_counts[frame_offset] >= global_minimum_threshold:
            one_flash = np.where(flash == frame_offset + 1, 1, 0)
            if np.sum(find_all_rectangle_sums(one_flash)) > 0:
                flash_object = Flash(frame_count - frame_rate + frame_offset, frame_count, flash_type)
                regional_flashes_found.append(flash_object)
    return regional_flashes_found


def find_all_rectangle_sums(array):
    area_averages = calculate_all_area_averages(array, visual_field)
    return all_area_averages_filter(area_averages)


def all_area_averages_filter(all_area_totals, allow_equal=True):
    if allow_equal:
        return np.where(all_area_totals >= regional_threshold, 1, 0)
    return np.where(all_area_totals > regional_threshold, 1, 0)


def calculate_all_area_averages(flash_matrix, fragment_dimensions):
    m_y, m_x = flash_matrix.shape
    f_y, f_x = fragment_dimensions
    horizontal_sum = np.cumsum(flash_matrix, axis=0)
    rectangular_sum = np.cumsum(horizontal_sum, axis=1)
    big_rectangle = rectangular_sum[f_y - 1:m_y, f_x - 1:m_x]
    tall_rectangle = rectangular_sum[0:m_y - f_y + 1, f_x - 1:m_x]
    long_rectangle = rectangular_sum[f_y - 1:m_y, 0:m_x - f_x + 1]
    small_rectangle = rectangular_sum[0:m_y - f_y + 1, 0:m_x - f_x + 1]
    center_rectangle = big_rectangle - tall_rectangle - long_rectangle + small_rectangle
    return np.divide(center_rectangle, f_y * f_x)
