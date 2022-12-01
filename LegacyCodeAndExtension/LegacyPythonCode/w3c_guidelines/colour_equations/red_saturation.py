import numpy as np
from cv2 import cv2

"""
The current working definition in the field for "pair of opposing transitions involving a saturated red" is where, 
for either or both states involved in each transition, R/(R+ G + B) >= 0.8, and the change in the value of (
R-G-B)x320 is > 20 (negative values of (R-G-B)x320 are set to zero) for both transitions. R, G, B values range from 
0-1 as specified in “relative luminance” definition.
"""


def calculate_red_saturation(frame):
    # "R, G, B values range from 0-1 as specified in “relative luminance” definition"
    curve_lut = calculate_relative_luminance_curve()
    curve_rgb = cv2.LUT(frame, curve_lut)
    # "R/(R+ G + B)"
    numerator = np.dot(curve_rgb[..., :3], [0, 0, 1])
    denominator = np.dot(curve_rgb[..., :3], [1, 1, 1])
    # note: this definition has a divide by zero problem
    red_saturation = np.divide(numerator, denominator, out=np.zeros(numerator.shape, dtype=float), where=denominator != 0)
    return red_saturation


def calculate_red_majority(frame):
    # "(R-G-B)x320"
    curve_lut = calculate_relative_luminance_curve()
    curve_rgb = cv2.LUT(frame, curve_lut)
    red_majority = np.maximum(np.multiply(np.dot(curve_rgb[..., :3], [-1, -1, 1]), 320), 0)
    return red_majority


def calculate_relative_luminance_curve():
    lut = np.divide(np.arange(256, dtype='uint8'), 255)
    # "R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4"
    lut = np.array([((X + 0.055) / 1.055) ** 2.4 if X > 0.03928 else X / 12.92 for X in lut])
    # lut = np.maximum(np.divide(lut, 12.92), np.power(np.divide(lut + 0.055, 1.055), 2.4))
    return lut
