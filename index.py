#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import cStringIO
from JwcLoginHelper import JwcLoginHelper
from RuijieHelper import RuijieHelper
from PIL import Image
from jwcfonts import code, codeCount, codeWidth, codePrefix, codeHash, codeLocPrefix

import tornado.ioloop
import tornado.web
import tornado.wsgi

class JwcLoginHandler(tornado.web.RequestHandler):
  def get(self):
    stuid = self.get_argument("stuid")
    pswd  = self.get_argument("pswd")
    host  = self.get_argument("host")
    enable_proxy = self.get_argument('enableProxy', default=False)

    if stuid == None or pswd == None or host == None:
      self.write("Invalid params")
      return

    result = JwcLoginHelper(stuid, pswd, host, enable_proxy).login()
    while(result['errcode'] == 3):
      result = JwcLoginHelper(stuid, pswd, host, enable_proxy).login()

    self.write(json.dumps(result))

class RjLoginHandler(tornado.web.RequestHandler):
  def get(self):
    stuid = self.get_argument("stuid")
    pswd  = self.get_argument("pswd")

    if stuid == None or pswd == None:
      self.write("Invalid params")
      return

    self.write(RuijieHelper(stuid, pswd).login())

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.write("Hello, world! - Tornado\n")

def _identifyCode(codeImg):
  ip = codeImg.convert("L").load()
  ps = [[0 for w in range(60)] for h in range(20)]
  for h in range(20):
    for w in range(60):
      if ip[w,h] <= 128:
        ps[h][w]=1
  codeArr = []
  for index in range(1, 5):
    char = _getCodeChar(ps, str(index))
    codeArr.append(char)
  codeStr = ""
  for item in codeArr:
    codeStr += item
  return codeStr

def _getCodeChar(ps, index):
  prefix = codeLocPrefix[index]
  chars = {}
  for charNum in range(62):
    char = str(charNum)
    hitTimes = 0
    for r in range(20):
      for c in range(codeWidth[char]):
        if code[char][r][c] != 0 and ps[r][c+prefix+codePrefix[char]] != 0:
          hitTimes += 1
    if codeCount[char] != 0:
      hitRate = hitTimes/codeCount[char]
      if hitRate != 1.0:
        chars[char] = hitRate
      else:
        return codeHash[char]

  maxHitRate = 0.0
  hitChar = ""
  for k, v in chars.items():
    if v > maxHitRate:
      maxHitRate = v
      hitChar = k
  return codeHash[hitChar]

class CaptchaHandler(tornado.web.RequestHandler):
  def post(self):
    data = tornado.escape.json_decode(self.request.body)
    decode_str = data["base64"].decode("base64")
    file_like = cStringIO.StringIO(decode_str)
    img = Image.open(file_like)
    result = _identifyCode(img)
    self.write(result)

app = tornado.web.Application([
  (r"/", MainHandler),
  (r"/jwc", JwcLoginHandler),
  (r"/rj", RjLoginHandler),
  (r"/captcha", CaptchaHandler),
])

if __name__ == '__main__':
  app.listen(18080)
  tornado.ioloop.IOLoop.instance().start()
