import numpy as np


# ADD DOCSTRING
def flash_detect_printout(flash, flash_counts, frame_count, frame_rate, thresholds):
    global_minimum_threshold, global_maximum_threshold = thresholds
    regional_flash_found = False
    for frame_offset in range(len(flash_counts)):
        if flash_counts[frame_offset] >= global_minimum_threshold:
            one_flash = np.where(flash == frame_offset + 1, 1, 0)
            if np.sum(find_all_rectangle_sums(one_flash)) > 0:
                regional_flash_found = True
                print("FLASH @", round((frame_count - frame_rate + frame_offset)/frame_rate, 1), "-", round(frame_count/frame_rate, 1))
    return regional_flash_found


def flash_detect_printout_both(both_flashes, flash_counts, frame_count, frame_rate, thresholds):
    lighter_darker_flash, darker_lighter_flash = both_flashes
    lighter_darker_flash_counts, darker_lighter_flash_counts = flash_counts
    flash_detect_printout(lighter_darker_flash, lighter_darker_flash_counts, frame_count, frame_rate, thresholds)
    flash_detect_printout(darker_lighter_flash, darker_lighter_flash_counts, frame_count, frame_rate, thresholds)


def all_large_flashes(both_flashes, flash_counts, thresholds):
    lighter_darker_flash, darker_lighter_flash = both_flashes
    lighter_darker_flash_counts, darker_lighter_flash_counts = flash_counts
    lighter_darker_flashes = half_large_flashes(lighter_darker_flash, lighter_darker_flash_counts, thresholds)
    darker_lighter_flashes = half_large_flashes(darker_lighter_flash, darker_lighter_flash_counts, thresholds)
    return lighter_darker_flashes + darker_lighter_flashes


def half_large_flashes(flash, flash_count, thresholds):
    found_flashes = []
    global_minimum_threshold, global_maximum_threshold = thresholds
    for frame_offset in range(len(flash_count)):
        if flash_count[frame_offset] >= global_minimum_threshold:
            one_flash = np.where(flash == frame_offset+1, 1, 0)
            if np.sum(find_all_rectangle_sums(one_flash)) > 0:
                found_flashes.append(one_flash)
    return found_flashes


def calculate_all_area_averages(flash_matrix, fragment_dimensions):
    m_y, m_x = flash_matrix.shape
    f_y, f_x = fragment_dimensions
    horizontal_sum = np.cumsum(flash_matrix, axis=0)
    rectangular_sum = np.cumsum(horizontal_sum, axis=1)
    big_rectangle = rectangular_sum[f_y-1:m_y, f_x-1:m_x]
    tall_rectangle = rectangular_sum[0:m_y-f_y+1, f_x-1:m_x]
    long_rectangle = rectangular_sum[f_y-1:m_y, 0:m_x-f_x+1]
    small_rectangle = rectangular_sum[0:m_y-f_y+1, 0:m_x-f_x+1]
    center_rectangle = big_rectangle - tall_rectangle - long_rectangle + small_rectangle
    return np.divide(center_rectangle, f_y * f_x)


def all_area_averages_filter(all_area_totals, regional_threshold, allow_equal=True):
    if allow_equal:
        return np.where(all_area_totals >= regional_threshold, 1, 0)
    return np.where(all_area_totals > regional_threshold, 1, 0)


def find_all_rectangle_sums(array):
    area_averages = calculate_all_area_averages(array, (75, 100))
    return all_area_averages_filter(area_averages, 0.25)


def show_rectangle_covered_area(area_filtered):
    area_filtered_padded = np.pad(area_filtered, ((74, 74), (99, 99)))
    find_all_ones = calculate_all_area_averages(area_filtered_padded, (75, 100))
    return all_area_averages_filter(find_all_ones, 0, allow_equal=False)


def show_brightest_rectangle(both_flashes):
    lighter_darker_flash, darker_lighter_flash = both_flashes
    lighter_averages = calculate_all_area_averages(lighter_darker_flash, (75, 100))
    darker_averages = calculate_all_area_averages(darker_lighter_flash, (75, 100))
    black_rectangle = np.zeros(both_flashes[0].shape)
    max_lighter_averages = np.amax(lighter_averages)
    max_darker_averages = np.amax(darker_averages)
    if max(max_lighter_averages, max_darker_averages) > 0:
        if max_lighter_averages >= max_darker_averages:
            rectangle_start = np.unravel_index(np.argmax(lighter_averages, axis=None), lighter_averages.shape)
        else:
            rectangle_start = np.unravel_index(np.argmax(darker_averages, axis=None), darker_averages.shape)
        y_len, x_len = lighter_darker_flash.shape
        ys, ye = rectangle_start[0], rectangle_start[0]+74
        xs, xe = rectangle_start[1], rectangle_start[1]+99
        x_line = np.concatenate((np.zeros(xs), np.ones(xe-xs), np.zeros(x_len-xe)))
        y_line = np.concatenate((np.zeros(ys), np.ones(ye-ys), np.zeros(y_len-ye)))
        black_rectangle[ys] = x_line
        black_rectangle[ye] = x_line
        black_rectangle[:, xs] = y_line
        black_rectangle[:, xe] = y_line
    return black_rectangle


def show_one_rectangle(one_flash):
    averages = calculate_all_area_averages(one_flash, (75, 100))
    black_rectangle = np.zeros(one_flash.shape)
    rectangle_start = np.unravel_index(np.argmax(averages, axis=None), averages.shape)
    y_len, x_len = one_flash.shape
    ys, ye = rectangle_start[0], rectangle_start[0]+74
    xs, xe = rectangle_start[1], rectangle_start[1]+99
    x_line = np.concatenate((np.zeros(xs), np.ones(xe-xs), np.zeros(x_len-xe)))
    y_line = np.concatenate((np.zeros(ys), np.ones(ye-ys), np.zeros(y_len-ye)))
    black_rectangle[ys] = x_line
    black_rectangle[ye] = x_line
    black_rectangle[:, xs] = y_line
    black_rectangle[:, xe] = y_line
    return black_rectangle


def maximum_safe_transition(frame, previous_frame):
    frame, previous_frame = frame.astype(float), previous_frame.astype(float)
    frame_delta = np.subtract(frame, previous_frame)
    new_frame_delta = np.maximum(np.minimum(frame_delta, 10), -10)
    new_frame = np.add(previous_frame, new_frame_delta)
    return new_frame.astype(int)


def safe_transition_on_flashes(unsafe_frame, safe_frame, flash_area):
    flash_area_three_channel = np.zeros_like(unsafe_frame)
    flash_area_three_channel[:, :, 0] = flash_area
    flash_area_three_channel[:, :, 1] = flash_area
    flash_area_three_channel[:, :, 2] = flash_area
    safe_part = np.multiply(safe_frame, flash_area_three_channel)
    unsafe_part = np.multiply(unsafe_frame, np.subtract(1, flash_area_three_channel))
    return np.add(safe_part, unsafe_part)
