from bottle import *

from JwcLoginHelper import JwcLoginHelper
from RuijieHelper import RuijieHelper

@get("/jwc")
def JwcLoginHander():
  stuid = request.params.get('stuid')
  pswd = request.params.get('pswd')
  host = request.params.get('host')

  if stuid == None or pswd == None or host == None:
    return "Invalid params"

  result = JwcLoginHelper(stuid, pswd, host).login()
  while(result['errcode'] == 3):
    result = JwcLoginHelper(stuid, pswd, host).login()

  return result

@get("/rj")
def RuijieLoginHandler():
  stuid = request.params.get('stuid')
  pswd = request.params.get('pswd')

  if stuid == None or pswd == None:
    return "Invalid params"

  return RuijieHelper(stuid, pswd).login()

if __name__ == '__main__':
  debug(True)
  run(host='localhost', port=80, reloader=True)
else:
  app = default_app()
  import sae
  application = sae.create_wsgi_app(app)
  # from bae.core.wsgi import WSGIApplication
  # application = WSGIApplication(app)
