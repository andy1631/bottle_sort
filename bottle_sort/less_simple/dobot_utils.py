import dobot_python_api as dobot
import time

from dobot_python_api.api.enums import *

from enum import Enum

from detector import Color

class BottlePosition(Enum):
    ONE = (205.0, -175.0, 46.0)
    TWO = (145.0, -215.0, 46.0)
    THREE = (25.0, -255.0, 46.0)


home_pos = (240.0, 0.0, 70.0, 0.0) 

def init_dobot(dev):
    c = dobot.create_connection(dev)
    dobot.set_ptp_jump_params(c, 40.0, 150.0)
    dobot.home(c)
    dobot.move(c, home_pos, dobot.PTP_MODE.MOVJ_XYZ)
    dobot.set_ir_switch(c, True, dobot.SensorPort.GP4)
    return c

def belt_forward(c):
    ind = dobot.start_belt(c, 0.5)

    curr = dobot.get_queued_cmd_current_index(c)
    while ind > curr:
        curr = dobot.get_queued_cmd_current_index(c)

    start_time = time.time()
    ir = 0
    while ir != 1:
        ir = dobot.get_ir(c, SensorPort.GP4)
    duration = time.time() - start_time
    dobot.stop_belt(c)

    return duration

def belt_backward(c, d):
    dobot.start_belt(c, -0.5)   
    dobot.wait(c, int(d * 1000))
    dobot.stop_belt(c)


def place_bottle(c, color):
    dobot.move(c, (216.0, -153.0, 100, 0), dobot.PTP_MODE.JUMP_XYZ)
    dobot.set_gripper(c, True, True)
    dobot.wait(c, 1000)

    match color:
        case Color.BLUE:
            dobot.move(c, (0.0, 0.0, 40.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ_INC)
            dobot.move(c, (150.0, 250.0, 100.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)
            dobot.move(c, (145.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)

        case Color.YELLOW:
            dobot.move(c, (96.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)

        case Color.PINK:
            dobot.move(c, (45.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)


    dobot.set_gripper(c, True, False)
    dobot.wait(c, 1000)
    dobot.set_gripper(c, False, False)

    dobot.move(c, home_pos, dobot.PTP_MODE.JUMP_XYZ)

def pickup_bottle(c, pos):

    dobot.move(c, pos.value, dobot.PTP_MODE.JUMP_XYZ)

    dobot.set_gripper(c, True, True)

    dobot.wait(c, 1000)

    dobot.move(c, (216.0, 102.0, 103.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)

    dobot.set_gripper(c, True, False)
    dobot.wait(c, 1000)
    dobot.set_gripper(c, False, False)

    dobot.move(c, home_pos, dobot.PTP_MODE.JUMP_XYZ)
