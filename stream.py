import time

import cv2 as cv
import numpy as np
import turicreate as tc


class CameraStream:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = cv.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise f'Cannot capture camera'

    def stream(self, period=0):
        prev_t = 0
        while True:
            ret, frame = self.cap.read()
            if ret:
                curr_t = time.time()
                if curr_t - prev_t > period:
                    prev_t = curr_t
                    yield frame


class WindowHandler:
    def __init__(self, name='stream', exit_btn='q'):
        self.name = name
        self.exit_btn = exit_btn

    def show(self, frame):
        cv.imshow(self.name, frame)
        if cv.waitKey(1) == ord(self.exit_btn):
            exit()


class DropcheckerDetector:
    def __init__(self, name):
        self.model = tc.load_model(name)
        self.img = None
        self.predictions = None

    def preprocess(self, frame):
        self.img = tc.Image(_image_data=frame.tobytes(),
                            _width=frame.shape[1],
                            _height=frame.shape[0],
                            _channels=frame.shape[2],
                            _format_enum=2,
                            _image_data_size=frame.size
                            )

    def predict(self, frame):
        self.predictions = self.model.predict(self.img)
        return True if len(self.predictions) > 0 else False

    def search_best(self):
        self.best = max(self.predictions, key=lambda x: x['confidence'])
        return self.best

    def get_coordinates(self):
        coord = self.best['coordinates']
        x = int(coord['x'])
        y = int(coord['y'])
        h = int(coord['height'])
        w = int(coord['width'])

        y0 = y + int(h / 2)
        y_offset = y + int(2 * h / 3)

        x0 = x - int(w / 2)
        x_offset = x + int(w / 2)

        return x0, y0, x_offset, y_offset

    def get_frame_box(self):
        annotated_image = \
            tc.one_shot_object_detector.util.draw_bounding_boxes(
                self.img,
                [self.best]
                )
        return annotated_image.pixel_data

    def detect(self, frame):
        self.preprocess(frame)
        if self.predict(frame):
            self.search_best()
            return self.get_coordinates()

    def crop(self, frame, x0, y0, x, y):
        return frame[y0:y, x0:x]


class HSVColor:
    def __init__(self, hue, saturation, value):
        self.hue = hue * 2
        self.saturation = saturation
        self.value = value

    def __str__(self):
        return f'{self.hue}, {self.saturation}, {self.value}'

    def is_yellow(self):
        return True if 40 <= self.hue < 70 else False

    def is_blue(self):
        return True if 170 <= self.hue < 270 else False


class ColorDetector:
    def __init__(self, frame):
        self.img = self.preprocess(frame)

    def preprocess(self, frame):
        return cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    def detect(self):
        avg_color_per_col = np.average(self.img, axis=0)
        main_color = np.average(avg_color_per_col, axis=0)
        color = HSVColor(*main_color)
        return color


if __name__ == '__main__':
    st = CameraStream()
    viewer = WindowHandler()
    detector = DropcheckerDetector('olddrop-mark.model')
    for frame in st.stream():
        coord = detector.detect(frame)
        if coord:
            cropped = detector.crop(frame, *coord)
            color_detector = ColorDetector(cropped)
            color = color_detector.detect()
            print(color)
            print(color.is_yellow(), color.is_blue())
            frame = detector.get_frame_box()

            viewer.show(cropped)
