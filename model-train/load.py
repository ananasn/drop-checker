import turicreate as tc


test_set = tc.SFrame({
    'image': [tc.Image('black-verf1.jpg'),
              tc.Image('black-verf2.jpg'),
              tc.Image('black-verf3.jpg')]
    })

model = tc.load_model('drop-mark.model')

prediction = model.predict(test_set)

print(prediction)
annotated_images = tc.one_shot_object_detector.util.draw_bounding_boxes(
    test_set['image'],
    prediction
    )

for i, img in enumerate(annotated_images):
    img.save(f'image-{i}.jpg')