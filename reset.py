#!/bin/python3

import dobot_python_api as dobot
import time

from dobot_python_api.api.enums import *

conn = dobot.create_connection()

dobot.stop_belt(conn)
dobot.set_gripper(conn, True, False)
dobot.wait(conn, 2000)
dobot.set_gripper(conn, False, False)

dobot.home(conn)



dobot.api.disconnect(conn)
