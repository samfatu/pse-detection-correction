from PhotosensitivitySafetyEngine.libraries.function_objects import *
import numpy as np


def colorCurve(curve):
    curves = {
        'RGB2sRGB': lambda X: X / 255,
        'RGB2XYZ': lambda X: ((X / 255 + 0.055) / 1.055) ** 2.4 if X / 255 > 0.03928 else X / 255 / 12.92
    }
    return InputToArray(curves[curve])


def relativeLuminance():
    return ArrayChannelsToArray(lambda R, G, B: 0.2126 * R + 0.7152 * G + 0.0722 * B, vector_form=True)


def absoluteLuminance():
    return ArrayChannelsToArray(lambda R, G, B: 1/3 * R + 1/3 * G + 1/3 * B, vector_form=True)


def changeDetect(direction=1, minimum=0):
    return ArrayAndPastToArray(lambda Present, Past: np.where(direction*(Present - Past) >= minimum, 1, 0), vector_form=True)


def pastOrPresentThreshold(threshold, direction=1):
    if direction == 1:
        return ArrayAndPastToArray(lambda Present, Past: np.where(np.maximum(Present, Past) >= threshold, 1, 0), vector_form=True)
    if direction == -1:
        return ArrayAndPastToArray(lambda Present, Past: np.where(np.minimum(Present, Past) <= threshold, 1, 0), vector_form=True)


def colorProportion(red=0, green=0, blue=0):
    return ArrayChannelsToArray(lambda R, G, B: np.divide(red * R + green * G + blue * B, (R + G + B), out=np.zeros(R.shape, dtype=float), where=(R + G + B) != 0), vector_form=True)


def twoConditions(logic=np.logical_and):
    return ArraysToArray(lambda Array1, Array2: logic(Array1, Array2), vector_form=True)


# NOT IN W3C
def colorValue(red=0, green=0, blue=0):
    return ArrayChannelsToArray(lambda R, G, B: red * R + green * G + blue * B, vector_form=True)


def threshold(threshold, direction=1):
    if direction == 1:
        return ArrayToArray(lambda Array: np.where(Array >= threshold, 1, 0), vector_form=True)
    if direction == -1:
        return ArrayToArray(lambda Array: np.where(Array <= threshold, 1, 0), vector_form=True)
