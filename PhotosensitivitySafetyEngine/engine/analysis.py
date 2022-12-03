import math
import time
import numpy as np
import cv2
from matplotlib import pyplot as plt


class GuidelineProcess:
    def __init__(self, objects, pipeline):
        self.objects = objects
        self.pipeline = pipeline

    def analyse_file(self, path, display=None, speedup=10, show_live_chart=True, show_dsp=True, show_analysis=True):
        if display is None:
            display = Display()
        capture = cv2.VideoCapture(path)
        print("FPS OF THE VIDEO : ", int(capture.get(cv2.CAP_PROP_FPS)))
        display.set_property('frame_rate', int(capture.get(cv2.CAP_PROP_FPS)))
        display.set_property('analysis_resolution',
                             tuple([int(x / speedup) for x in display.get_property('display_resolution')]))
        print(tuple([int(x / speedup) for x in display.get_property('display_resolution')]))
        objects_with_properties = self.objects(display.properties())
        value_register = Register()
        while True:
            check, frame = capture.read()
            if not check:
                break
            # PIPELINE
            values = [display.render(frame)]
            for (fun, xs, *_) in self.pipeline:
                values.append(
                    objects_with_properties[fun].run(*[values[x] for x in xs] if type(xs) is tuple else [values[xs]]))

            # CHART VALUES
            value_register.add_all(self.pipeline, values)
            if show_live_chart:
                value_register.live_plot()
            if show_dsp:
                cv2.imshow('Video', values[0]), cv2.waitKey(1)
            print('', end=f'\r{int(capture.get(cv2.CAP_PROP_POS_FRAMES))}/{int(capture.get(cv2.CAP_PROP_FRAME_COUNT))}')
        cv2.destroyAllWindows()
        if show_analysis:
            value_register.plot()
            plt.show()
        # print(value_register.values)
        return value_register.values


class Display:
    def __init__(self, display_resolution=(1024, 768), display_diameter=16, display_distance=24, nits=200):
        display_size = tuple(
            [display_diameter * x1 / sum([x2 ** 2 for x2 in display_resolution]) ** 0.5 for x1 in display_resolution])
        degree_field = lambda a: tuple([math.sin(a * math.pi / 180) * display_distance / x for x in display_size])
        self.data = {
            'display_resolution': display_resolution,
            'analysis_resolution': display_resolution,
            'display_diameter': display_diameter,
            'display_distance': display_distance,
            'display_size': display_size,
            'degree_field': degree_field,
            'frame_rate': 30,
            'candelas': nits
        }

    def set_property(self, name, value):
        self.data[name] = value

    def get_property(self, name):
        return self.data[name]

    def properties(self):
        return self.data

    def render(self, frame):
        screen = np.zeros((self.data['analysis_resolution'][1], self.data['analysis_resolution'][0], 3))
        if frame.shape[0] / self.data['analysis_resolution'][1] > frame.shape[1] / self.data['analysis_resolution'][0]:
            size = int(frame.shape[1] / frame.shape[0] * self.data['analysis_resolution'][1]), \
                   self.data['analysis_resolution'][1]
            position = int((self.data['analysis_resolution'][0] - size[0]) / 2), 0
        else:
            size = self.data['analysis_resolution'][0], int(
                frame.shape[0] / frame.shape[1] * self.data['analysis_resolution'][0])
            position = 0, int((self.data['analysis_resolution'][1] - size[1]) / 2)
        resized_frame = cv2.resize(frame, size)
        screen[position[1]:position[1] + size[1], position[0]:position[0] + size[0]] = resized_frame
        return np.array(screen, dtype='uint8')


class Register:
    def __init__(self):
        self.values = {}
        self.figure = None

    def add(self, name, x):
        if name in self.values.keys():
            self.values[name].append(x)
        else:
            self.values[name] = [x]

    def add_all(self, pipeline, values):
        for i in range(len(pipeline)):
            if len(pipeline[i]) > 2:
                self.add(pipeline[i][2], values[i + 1])

    def get(self, name):
        return self.values[name]

    def plot(self):
        plt.ioff()
        plt.close('all')
        fig, axs = plt.subplots(len(self.values.keys()))
        titles = list(self.values.keys())
        for i in range(len(titles)):
            axs[i].plot(np.arange(len(self.values[titles[i]])), self.values[titles[i]])
            axs[i].fill_between(np.arange(len(self.values[titles[i]])), 0, self.values[titles[i]], alpha=.3)
            axs[i].set_title(titles[i])

        fig.canvas.manager.set_window_title('Analysis Results')
        fig.tight_layout()

    def live_plot(self):
        if self.figure is None:
            plt.ion()
            fig, axs = plt.subplots(len(self.values.keys()))
            titles = list(self.values.keys())
            lin = []
            for i in range(len(titles)):
                axs[i].set_title(titles[i])
                line, = axs[i].plot(np.arange(len(self.values[titles[i]])) / 30, self.values[titles[i]])
                lin.append(line)
            self.figure = fig, axs, lin
            fig.canvas.manager.set_window_title('Live Analysis')
            plt.tight_layout()
        fig, axs, lin = self.figure
        titles = list(self.values.keys())
        for i in range(len(titles)):
            lin[i].set_xdata(np.arange(len(self.values[titles[i]])) / 30)
            lin[i].set_ydata(self.values[titles[i]])
            axs[i].relim()
            axs[i].autoscale_view(True, True, True)
        fig.canvas.draw()
        fig.canvas.flush_events()


class Timer:
    def __init__(self):
        self.times = {}
        self.last_time = time.time()

    def time(self, name):
        if name in self.times.keys():
            self.times[name] += time.time() - self.last_time
        else:
            self.times[name] = time.time() - self.last_time
        self.last_time = time.time()

    def print(self):
        print(self.times)

    def plot(self):
        plt.ioff()
        fig, axes = plt.subplots(2, 2)
        colors = plt.cm.gist_ncar(np.arange(len(self.times.keys())) / len(self.times.keys()))
        axes[0, 0].pie(self.times.values(),
                       explode=[0 if any(i.isdigit() for i in a) else 0.1 for a in self.times.keys()], startangle=90,
                       counterclock=False, colors=colors)
        for i in range(len(self.times.keys())):
            axes[1, 0].bar(i, list(self.times.values())[i], color=colors[i], label=list(self.times.keys())[i])
        axes[1, 0].axes.xaxis.set_visible(False)
        handles, labels = axes[1, 0].get_legend_handles_labels()
        axes[0, 1].axis('off'), axes[1, 1].axis('off')
        fig.legend(handles, labels, loc='right')
        fig.canvas.manager.set_window_title('Analysis Timing')
        fig.tight_layout()
