from detector import *


model = init_model('../yolov5_model/bottles/weights/best.pt')

pipeline = init_camera()

bottles = []

for _ in range(2):
    objects, image = get_detected_objects(get_image(pipeline), model)

    display_preview(image)
    bottles = objects


for pos in bottles:
    print(f'pos: {pos}, color: {get_color(image, pos)}')
