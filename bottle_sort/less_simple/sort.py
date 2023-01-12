import threading
from detector import *


model = init_model('../yolov5_model/bottles/weights/best.pt')

pipeline = init_camera()


def get_bottles():
    global image
    for _ in range(2):
        bottles, image = get_detected_objects(get_image(pipeline), model)
        return bottles

def preview(): 
    while True:
        global image
        if image == none: image = np.zeros((480, 640, 3), dtype = "uint8")

        display_preview(image)

def enable_preview():
    thread = threading.Thread(target=preview)
    thread.start()
    return thread


enable_preview()

for pos in get_bottles():
    print(f'pos: {pos}, color: {get_color(image, pos)}')
