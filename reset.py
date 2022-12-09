import dobot_python_api as dobot
import time

from dobot_python_api.api.enums import *

conn = dobot.create_connection()

dobot.stop_belt(conn)

dobot.home(conn)



dobot.api.disconnect(conn)
