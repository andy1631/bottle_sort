import dobot_utils 
import detector

c1 = dobot_utils.init_dobot('/dev/ttyUSB0')
c2 = dobot_utils.init_dobot('/dev/ttyUSB1')

model = detector.init_model('../yolov5_model/bottles/weights/best.pt')

pipeline = detector.init_camera()


thread = detector.enable_preview()


while True:
    bottles = detector.get_detected_objects(detector.get_image(pipeline), model)

    bottles = sorted(bottles, key=lambda bottle: bottle[1][0])

    for bottle, pos in zip(bottles, dobot_utils.BottlePosition):
        print(f'pos: {bottle[1]}, color: {bottle[0].value}')
        dobot_utils.pickup_bottle(c1, pos)
        delta = dobot_utils.belt_forward(c1)
        ind = dobot_utils.place_bottle(c2, bottle[0])
        dobot_utils.wait_for(c2, ind)
        dobot_utils.belt_backward(c1, delta)
        

    thread.join()
