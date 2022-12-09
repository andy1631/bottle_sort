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

start_time = time.time()
ir = 0
while ir != 1:
    ir = dobot.get_ir(conn, SensorPort.GP4)

duration = time.time() - start_time
dobot.stop_belt(conn)
# --------

dobot.move(conn, (217.0, -153.0, 100, 0), dobot.PTP_MODE.JUMP_XYZ)
dobot.set_gripper(conn, True, True)

dobot.wait(conn, 2000)

dobot.move(conn, (0.0, 0.0, 40.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.wait(conn, 2000)

dobot.move(conn, (0.0, 100.0, 0.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.wait(conn, 2000)

dobot.move(conn, (0.0, -100.0, 0.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.wait(conn, 1000)

dobot.move(conn, (0.0, 0.0, -40.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.wait(conn, 1000)

dobot.set_gripper(conn, True, False)

dobot.wait(conn, 1000)

dobot.move(conn, (0.0, 0.0, 20.0, 0), dobot.PTP_MODE.MOVJ_XYZ_INC)

dobot.set_gripper(conn, False, False)
# --------

dobot.start_belt(conn, -0.5)

print(duration)

dobot.wait(conn, int(duration * 1000))

dobot.stop_belt(conn)



#ablegen: 45, 250, 60, 0
dobot.api.disconnect(conn)
