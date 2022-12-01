import numpy as np


"""
A general flash is defined as a pair of opposing changes in relative luminance

A red flash is defined as any pair of opposing transitions involving a saturated red 

a flash or rapidly changing image sequence is below the threshold (i.e., content passes) if (...) there are no more than 
three general flashes and / or no more than three red flashes within any one-second period;
"""


# "general flash is defined as a pair of opposing changes"
def update_last_flashes(last_changes, both_relative_luminance_limits, frame_rate):
    last_lighter, last_darker = last_changes
    limit_relative_luminance_lighter, limit_relative_luminance_darker = both_relative_luminance_limits
    last_lighter = update_last_flash(last_lighter, limit_relative_luminance_lighter, frame_rate)
    last_darker = update_last_flash(last_darker, limit_relative_luminance_darker, frame_rate)
    return last_lighter, last_darker


def update_last_flash(last_change, limit_relative_luminance, frame_rate):
    return np.maximum(np.maximum(last_change - 1, 0), limit_relative_luminance * frame_rate)


def cross_reference_transitions(last_changes, both_relative_luminance_limits):
    last_lighter, last_darker = last_changes
    limit_relative_luminance_lighter, limit_relative_luminance_darker = both_relative_luminance_limits
    lighter_darker_flash = cross_reference_single_transitions(last_lighter, limit_relative_luminance_darker)
    darker_lighter_flash = cross_reference_single_transitions(last_darker, limit_relative_luminance_lighter)
    return lighter_darker_flash, darker_lighter_flash


def cross_reference_single_transitions(last_change, limit_relative_luminance_opposite):
    return np.array(last_change * limit_relative_luminance_opposite, dtype=int)


def flash_frames_separator(both_flashes):
    lighter_darker_flash, darker_lighter_flash = both_flashes
    lighter_darker_flash_counts = flash_frames_separator_single(lighter_darker_flash)
    darker_lighter_flash_counts = flash_frames_separator_single(darker_lighter_flash)
    return lighter_darker_flash_counts, darker_lighter_flash_counts


def flash_frames_separator_single(flash_frames):
    flash_counts = np.bincount(np.ravel(flash_frames))
    return (flash_counts / sum(flash_counts))[1:]