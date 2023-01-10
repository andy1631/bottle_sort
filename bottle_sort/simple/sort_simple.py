import dobot_python_api as dobot
import util


c = dobot.create_connection()

util.init(c)

util.pickup(c, util.Color.WHITE)

d = util.belt_forward(c)

#util.place_bottle(c, util.Color.WHITE)

dobot.wait(c, 2000)

util.belt_backward(c, d)

util.pickup(c, util.Color.GREEN)


d = util.belt_forward(c)

#util.place_bottle(c, util.Color.GREEN)

dobot.wait(c, 2000)

util.belt_backward(c, d)

#dobot.wait(c, 5000)
util.pickup(c, util.Color.BROWN)

d = util.belt_forward(c)

#util.place_bottle(c, util.Color.BROWN)

dobot.wait(c, 2000)

util.belt_backward(c, d)


dobot.api.disconnect(c)
