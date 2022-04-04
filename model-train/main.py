import turicreate as tc

train_set = tc.SFrame({
    'image': [tc.Image('black-train.png')],
    'label': ['drop']
    })

test_set = tc.SFrame({
    'image': [tc.Image('black-verf1.jpg'),
              tc.Image('black-verf2.jpg'),
              tc.Image('black-verf3.jpg')]
    })

model = tc.one_shot_object_detector.create(train_set,
                                           'label',
                                           max_iterations=100)

model.save('drop-mark.model')

test_set['predictions'] = model.predict(test_set)
annotated_images = tc.one_shot_object_detector.util.draw_bounding_boxes(
    test_set['images'],
    test_set[
        'predictions'])

for i, img in enumerate(annotated_images):
    img.save(f'image-{i}.jpg')



