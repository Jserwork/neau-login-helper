#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib
import urllib2
from PIL import Image
from jwcfonts import code, codeCount, codeWidth, codePrefix, codeHash, codeLocPrefix
import json

import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class JwcLoginHelper:

  CodePath  = "/validateCodeAction.do"
  VerifyPath = "/loginAction.do"

  def __init__(self, stuid, pswd, host):
    self.stuid = stuid
    self.pswd  = pswd
    self.host = host

  # 0 -- success  1 -- connectError  2 -- identifyError  3 -- codeError   
  def login(self):

    # 获取验证码图片和cookie
    self._getCookieAndCodeImg()
    if self.getCookieSuccess != True:
      return {'errcode': 1, 'errmsg': 'connect error'}

    # 识别验证码
    self._identifyCode()

    # 通过网络验证验证码
    self._verifyAccount()
    return self.loginResult

  def _verifyAccount(self):
    params = {"dzslh": "", "eflag": "", "evalue": "", "fs": "", "lx": "", "tips": "", "zjh1": "", 
      "mm": self.pswd, "v_yzm": self.code, "zjh": self.stuid }
    headers = {'Cookie': self.cookie}
    data = urllib.urlencode(params)
    req = urllib2.Request(self.host + self.VerifyPath, data, headers)
    try:
      res = urllib2.urlopen(req)
    except:
      pass
    else:
      result = res.read()
      if "frameset" in result:
        self.loginResult = {'errcode': 0, 'ticket': self.cookieValue}
        return
      result = result.decode('gb2312')
      if "你输入的证件号不存在" in result:
        self.loginResult = {'errcode': 2, 'errmsg': 'username or password wrong'}
      elif "你输入的验证码错误" in result:
        self.loginResult = {'errcode': 3, 'errmsg': 'code wrong'}
      else:
        self.loginResult = {'errcode': 4, 'errmsg': 'unknow wrong'}

  def _getCookieAndCodeImg(self):
    try:
      res = urllib2.urlopen(url=self.host + self.CodePath, timeout=3)
      if res.getcode() == 200:
        self.cookie = res.info()['Set-Cookie']
      else:
        return
    except:
      self.getCookieSuccess = False
    else:
      self.getCookieSuccess = True
      self.cookieValue = self.cookie[11:32]
      self.codeImg = Image.open(io.BytesIO(res.read()))

  def _identifyCode(self):
    ip = self.codeImg.convert("L").load()
    ps = [[0 for w in range(60)] for h in range(20)]
    for h in range(20):
      for w in range(60):
        if ip[w,h] <= 128:
          ps[h][w]=1
    codeArr = []
    for index in range(1, 5):
      char = self._getCodeChar(ps, str(index))
      codeArr.append(char)
    codeStr = ""
    for item in codeArr:
      codeStr += item
    self.code = codeStr

  def _getCodeChar(self, ps, index):
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
