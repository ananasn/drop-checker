import cv2 as cv
import turicreate as tc

CAMERA = 0

cap = cv.VideoCapture(CAMERA)
model = tc.load_model('olddrop-mark.model')


if not cap.isOpened():
    exit()

while True:
    ret, frame = cap.read()
    if ret:
        image = tc.Image(_image_data=frame.tobytes(),
                         _width = frame.shape[1],
                         _height=frame.shape[0],
                         _channels=frame.shape[2],
                         _format_enum=2,
                         _image_data_size=frame.size
                         )
        prediction = model.predict(image)
        print(prediction)
        if len(prediction) > 0:
            best = max(prediction, key=lambda x: x['confidence'])
            print(best)
            annotated_images = tc.one_shot_object_detector.util.draw_bounding_boxes(
                image,
                [best]
                )
        cv.imshow('stream', annotated_images.pixel_data)
    if cv.waitKey(1) == ord('q'):
        break