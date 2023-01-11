import threading
import numpy as np
import time
from detector_multithread_log import *
#import dobot_python_api as dobot
#from dobot_python_api.api.enums import *

def get_diff(p1, p2):
    diff = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])
    return diff

def get_robo_point(p, diff): return (p[0] + diff[0], p[1] + diff[1], p[2] + diff[2]) 
# Initialize model and start streaming
#start_detection("../yolov5_model/yolov5n_klopfer/weights/best.pt")
def print_results(q, dobot_pos):
    diff = 0
    while True: 
        if q.empty(): continue

        detected_objects = q.get() 
        cls, conf, x_img, y_img, x, y, z = detected_objects[0]
        x *= 1000
        y *= 1000
        z *= 1000

        if diff == 0: diff = get_diff((x, y, z), dobot_pos)

        print((x, y, z))

        print(diff)
        pos_res = get_robo_point((x,y,z), diff) 
       
        # Print detected objects
        print(pos_res)

#def adjust(q):
#    for i in range(10):
#        if q.empty():
#            i -= 1
#            continue

t, q = start_detection("yolov5_model/bottles/weights/best.pt")

# Enable live preview
enable_preview()

# Get detected objects

"""
conn = dobot.create_connection()

dobot.set_ptp_jump_params(conn, 40.0, 150.0)
dobot.home(conn)
dobot.move(conn, (60.0, -200.0, 70.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)
dobot.wait(conn, 5000)
ind = dobot.set_gripper(conn, True, True)
curr = dobot.get_queued_cmd_current_index(conn)
while ind > curr:
    curr = dobot.get_queued_cmd_current_index(conn)

dobot.wait(conn, 10000)
dobot.move(conn, (60.0, -200.0, 80.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)
"""

t2 = threading.Thread(target=print_results, args=(q,(60, -200, 70)))
t2.start()
t.join()
t2.join()
