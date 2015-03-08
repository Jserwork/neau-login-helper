from JwcLoginHelper import JwcLoginHelper
from RuijieHelper import RuijieHelper

import tornado.ioloop
import tornado.web

class JwcLoginHandler(tornado.web.RequestHandler):
  def get(self):
    stuid = self.get_argument("stuid")
    pswd  = self.get_argument("pswd")
    host  = self.get_argument("host")

    if stuid == None or pswd == None or host == None:
      self.write("Invalid params")
      return

    result = JwcLoginHelper(stuid, pswd, host).login()
    while(result['errcode'] == 3):
      result = JwcLoginHelper(stuid, pswd, host).login()

    self.write(json.dumps(result))

class RjLoginHandler(tornado.web.RequestHandler):
  def get(self):
    stuid = self.get_argument("stuid")
    pswd  = self.get_argument("pswd")

    if stuid == None or pswd == None:
      self.write("Invalid params")
      return

    self.write(RuijieHelper(stuid, pswd).login())

application = tornado.web.Application([
    (r"/jwc", JwcLoginHandler),
    (r"/rj", RjLoginHandler),
])

if __name__ == '__main__':
  application.listen(80)
  tornado.ioloop.IOLoop.instance().start()
