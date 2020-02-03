#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import cStringIO
from PIL import Image
from jwcfonts import code, codeCount, codeWidth, codePrefix, codeHash, codeLocPrefix

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

def handler(environ, start_response):
   # get request_body
  try:
    request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  except (ValueError):
    request_body_size = 0
  request_body = environ['wsgi.input'].read(request_body_size)
  body = json.loads(request_body)
  # if 'base64' not in req['queryParameters']:
  #   return {
  #     'isBase64Encoded': False,
  #     'statusCode': 200,
  #     'headers': {},
  #     'body': 'missing params'
  #   }

  # base64 = req['queryParameters']['base64']

  base64 = body['body']

  file_like = cStringIO.StringIO(base64.decode('base64'))
  img = Image.open(file_like)
  result = _identifyCode(img)

  start_response('200 OK', [('Content-type', 'application/json')])
  return [json.dumps({ 'code': result })]
