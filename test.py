import dobot_python_api as dobot
import time

from dobot_python_api.api.enums import *

conn = dobot.create_connection()

dobot.set_ptp_jump_params(conn, 40.0, 150.0)

dobot.move(conn, (240.0, 0.0, 70.0, 0.0), dobot.PTP_MODE.MOVJ_XYZ)


dobot.set_ir_switch(conn, True, dobot.SensorPort.GP4)

ind = dobot.start_belt(conn, 0.5)

curr = dobot.get_queued_cmd_current_index(conn)
while ind > curr:
    curr = dobot.get_queued_cmd_current_index(conn)
    print(ind, curr)

start_time = time.time()
ir = 0
while ir != 1:
    ir = dobot.get_ir(conn, SensorPort.GP4)

duration = time.time() - start_time
dobot.stop_belt(conn)
# --------

dobot.move(conn, (220.0, -175.0, 100, 0), dobot.PTP_MODE.JUMP_XYZ)
dobot.set_gripper(conn, True, True)
time.sleep(2.0)
dobot.move(conn, (0.0, 0.0, 40.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)
time.sleep(2.0)
dobot.move(conn, (0.0, 100.0, 0.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)
time.sleep(2.0)
dobot.move(conn, (0.0, -100.0, 0.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)
time.sleep(1.0)
dobot.move(conn, (0.0, 0.0, -40.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)
time.sleep(1.0)
dobot.set_gripper(conn, True, False)
time.sleep(1.0)
dobot.move(conn, (0.0, 0.0, 20.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.set_gripper(conn, False, False)
# --------

ind = dobot.start_belt(conn, -0.5)

curr = dobot.get_queued_cmd_current_index(conn)

while ind > curr:
    curr = dobot.get_queued_cmd_current_index(conn)

start_time = time.time()
d = 0 
while d <= duration:
    d = time.time() - start_time

dobot.stop_belt(conn)

dobot.api.disconnect(conn)
