import numpy as np


def eight_bit():
    return np.arange(256)


def rgb():
    return [[a, b, c] for a in range(256) for b in range(256) for c in range(256)]
