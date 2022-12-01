import cv2.cv2 as cv2
import numpy as np


class Plotter:
    def __init__(self, plot_width, plot_height):
        self.width = plot_width
        self.height = plot_height
        self.color = (0, 0, 0)
        self.val = []
        self.plot_canvas = np.ones((self.height, self.width, 3))*255

    # Update new values in plot
    def plot(self, val, label="Unnamed Plot", line=True):
        self.val.append(int(val))
        while len(self.val) > self.width:
            self.val.pop(0)

        self.show_plot(label, line=line)

    # Show plot using opencv imshow
    def show_plot(self, label, line=True):
        self.plot_canvas = np.ones((self.height, self.width, 3))*255
        cv2.line(self.plot_canvas, (0, int(self.height-45)), (self.width, int(self.height-45)), (0, 255, 0), 1)
        if not line:
            cv2.line(self.plot_canvas, (0, int(self.height - 45 - 255/36)), (self.width, int(self.height - 45 - 255/36)), (255, 0, 0), 1)
            cv2.line(self.plot_canvas, (0, int(self.height - 45 - 255/4)), (self.width, int(self.height - 45 - 255/4)), (255, 0, 0), 1)
        for i in range(len(self.val)-1):
            cv2.line(self.plot_canvas, (i, int(self.height-45) - self.val[i]*(line)), (i+line, int(self.height-45) - self.val[i+line]), self.color, 1)

        cv2.imshow(label, self.plot_canvas)
        cv2.waitKey(10)
