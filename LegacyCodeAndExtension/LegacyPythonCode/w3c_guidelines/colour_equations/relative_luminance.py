import numpy as np
from cv2 import cv2

"""
relative luminance
the relative brightness of any point in a colorspace, normalized to 0 for darkest black and 1 for lightest white

NOTE For the sRGB colorspace, the relative luminance of a color is defined as L = 0.2126 * R + 0.7152 * G + 0.0722 * B
where R, G and B are defined as: 

if RsRGB <= 0.03928 then R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4
if GsRGB <= 0.03928 then G = GsRGB/12.92 else G = ((GsRGB+0.055)/1.055) ^ 2.4
if BsRGB <= 0.03928 then B = BsRGB/12.92 else B = ((BsRGB+0.055)/1.055) ^ 2.4
"""


def calculate_relative_luminance(frame):
    # TODO (low priority): make this calculate just once
    curve_lut = calculate_relative_luminance_curve()
    curve_rgb = cv2.LUT(frame, curve_lut)
    # relative luminance of a color is defined as L = 0.2126 * R + 0.7152 * G + 0.0722 * B
    relative_luminance = np.dot(curve_rgb[..., :3], [0.0722, 0.7152, 0.2126])
    return relative_luminance


def calculate_relative_luminance_curve():
    lut = np.divide(np.arange(256, dtype='uint8'), 255)
    # "R = RsRGB/12.92 else R = ((RsRGB+0.055)/1.055) ^ 2.4"
    lut = np.maximum(np.divide(lut, 12.92), np.power(np.divide(lut + 0.055, 1.055), 2.4))
    return lut
