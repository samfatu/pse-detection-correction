import numpy as np


"""
A red flash is defined as any pair of opposing transitions involving a saturated red 
"""


"""
The current working definition in the field for "pair of opposing transitions involving a saturated red" is where, 
for either or both states involved in each transition, R/(R+ G + B) >= 0.8, and the change in the value of (
R-G-B)x320 is > 20 (negative values of (R-G-B)x320 are set to zero) for both transitions. R, G, B values range from 
0-1 as specified in “relative luminance” definition.
"""


def red_saturation_limits(red_saturation, previous_red_saturation, red_majority, previous_red_majority):
    red_saturation_condition = red_saturation_minimum(red_saturation, previous_red_saturation)
    lighter = red_majority_limit(red_majority, previous_red_majority, red_saturation_condition, direction='lighter')
    darker = red_majority_limit(red_majority, previous_red_majority, red_saturation_condition, direction='darker')
    # "Exception: Flashing with "squares" smaller than 0.1 degree"
    # TODO: add average smoothing with approximate size to exclude small squares
    return lighter, darker


def red_majority_limit(red_majority, previous_red_majority, red_saturation_condition, direction='lighter'):
    delta_red_majority = red_majority - previous_red_majority
    if direction == 'lighter':
        # "the change in the value of (R-G-B)x320 is > 20"
        condition_a = np.where(delta_red_majority >= 20, 1, 0)
        return np.array(np.multiply(condition_a, red_saturation_condition), dtype=np.uint8)
    if direction == 'darker':
        # "the change in the value of (R-G-B)x320 is > 20"
        condition_a = np.where(delta_red_majority <= -20, 1, 0)
        return np.array(np.multiply(condition_a, red_saturation_condition), dtype=np.uint8)


def red_saturation_minimum(red_saturation, previous_red_saturation):
    # "for either or both states involved in each transition, R/(R+ G + B) >= 0.8"
    max_red_saturation = np.maximum(red_saturation, previous_red_saturation)
    # "R/(R+ G + B) >= 0.8"
    threshold_red_saturation = np.where(max_red_saturation > 0.8, 1, 0)
    return threshold_red_saturation
