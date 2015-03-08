#!/usr/bin python
# -*- coding: UTF-8 -*-

import urllib
import urllib2
from PIL import Image
import sys
from rjfonts import code, codeCount, codeWidth, codePrefix, codeHash, codeLocPrefix
import json

import io
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class RuijieHelper(object):

  baseUrl = "http://202.118.166.244:8080/selfservice/"

  verifyUrl = baseUrl + "module/scgroup/web/login_judge.jsf"
  indexUrl = baseUrl + "module/webcontent/web/index_self.jsf?"
  codeUrl = baseUrl + "common/web/verifycode.jsp"
  """login and get infomation from ruijie server"""
  def __init__(self, username, password):
    super(RuijieHelper, self).__init__()
    # request data
    self.username = username
    self.password = password
    self.verifyCode = None
    self.cookie = None

    # status mark
    self.getCookieSuccess = False
    self.loginSuccess = False
    self.accountError = False

  def login(self):

    self._getCookieAndCodeImg()
    while self.getCookieSuccess == False:
      self._getCookieAndCodeImg()
    self._verifyAccount()

    if self.loginSuccess:
      return {'errcode': 0, 'cookie': self.cookie, 'code': self.verifyCode}

    elif self.accountError:
      return {'errcode': 2}

    else:
      return RuijieHelper(self.username, self.password).login()

  def _getCookieAndCodeImg(self):
    try:
      res = urllib2.urlopen(url=self.codeUrl, timeout=3)
    except:
      pass
    else:
      if res.getcode() == 200:
        self.cookie = res.info()['Set-Cookie'][0:43]
        im = Image.open(io.BytesIO(res.read()))
        self.verifyCode = self._identifyCode(im)
        self.getCookieSuccess = True

  def _getGetHeaders(self):
    return 

  def _verifyAccount(self):
    postData = {
      "act": "add",
      "name": self.username,
      "password": self.password,
      "verify": self.verifyCode
    }
    data = urllib.urlencode(postData)
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
      'Host': '202.118.166.244:8080',
      'Referer': 'http://202.118.166.244:8080/selfservice/module/webcontent/web/index_self.jsf?',
      'Cookie': self.cookie
    }
    req = urllib2.Request(self.verifyUrl, data, headers)
    try:
      res = urllib2.urlopen(req)
    except:
      pass
    else:
      result = res.read()
      if ('&name=' in result) == False:
        reqindex = urllib2.Request(self.indexUrl, headers=headers)
        code = urllib2.urlopen(reqindex).getcode()
        self.loginSuccess = True
        return
      if '?errorMsg=' in result:
        self.accountError = True
        return

  def _identifyCode(self, im):
    ip = im.convert("L").load()
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
    return codeStr

  def _getCodeChar(self, ps, index):
    prefix = codeLocPrefix[index]
    chars = {}
    for charNum in range(10):
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
          return char

    maxHitRate = 0.0
    hitChar = ""
    for k, v in chars.items():
      if v > maxHitRate:
        maxHitRate = v
        hitChar = k
    return codeHash[hitChar]
