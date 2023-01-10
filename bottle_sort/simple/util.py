import dobot_python_api as dobot
import time

from enum import Enum

from dobot_python_api.api.enums import *


class Color(Enum):
    BROWN = 1
    GREEN = 2
    WHITE = 3

home_pos = (240.0, 0.0, 70.0, 0.0) 

def init(c):
    dobot.set_ptp_jump_params(c, 40.0, 150.0)
    dobot.home(c)
    dobot.move(c, home_pos, dobot.PTP_MODE.MOVJ_XYZ)
    dobot.set_ir_switch(c, True, dobot.SensorPort.GP4)


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
        case Color.BROWN:
            dobot.move(c, (0.0, 0.0, 40.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ_INC)
            dobot.move(c, (150.0, 250.0, 100.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)
            dobot.move(c, (145.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)

        case Color.GREEN:
            dobot.move(c, (96.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)

        case Color.WHITE:
            dobot.move(c, (45.0, 250.0, 51.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)


    dobot.set_gripper(c, True, False)
    dobot.wait(c, 1000)
    dobot.set_gripper(c, False, False)

    dobot.move(c, home_pos, dobot.PTP_MODE.JUMP_XYZ)

def pickup(c, color):
    match color:
        case Color.BROWN:
            dobot.move(c, (45.0, -250.0, 46.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)
        case Color.GREEN:
            dobot.move(c, (96.0, -250.0, 40.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)
        case Color.WHITE:
            dobot.move(c, (145.0, -250.0, 46.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)

    dobot.set_gripper(c, True, True)

    dobot.move(c, (216.0, 102.0, 100.0, 0.0), dobot.PTP_MODE.JUMP_XYZ)

    dobot.set_gripper(c, True, False)
    dobot.wait(c, 1000)
    dobot.set_gripper(c, False, False)

    dobot.move(c, home_pos, dobot.PTP_MODE.JUMP_XYZ)

