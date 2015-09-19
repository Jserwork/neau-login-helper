#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys

import re
import urllib2
import urlparse
import time
import hashlib
from db import engine, news_table
#import pylibmc as memcache
#mc = memcache.Client()
root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root, 'site-packages'))

def getEduNewsList(type, count):
  if type == 'edu':
    columnId = 252
  elif type == 'exam':
    columnId = 254
  else:
    return None
  eduNewsUrl = ('http://jwc.neau.edu.cn/homepage/infoArticleList.do'
    '?sortColumn=publicationDate&sortDirection=-1&columnId=' + str(columnId) +
    '&pagingNumberPer=' + str(count) + '&pagingPage=1')
  return parseEduNewsList(eduNewsUrl, type)

newsItemReg = re.compile(r'<li><div><a href="(\S*?)"  target="_blank" >(.*?)</a><span>(\S*?)</span></div></li>')
httpNewsItemReg = re.compile(r'<li><div><a href="(\S*?)" target="_blank">(.*?)</a><span>(\S*?)</span></div></li>')

def parseEduNewsList(url, type):
  try:
    html = urllib2.urlopen(url=url, timeout=3).read()
  except Exception, e:
    return None

  html = html.replace('\n', '').replace('\r', '').decode('UTF-8', 'ignore')
  newsItems = newsItemReg.findall(html)
  httpNewsItem = httpNewsItemReg.findall(html)

  newsItems = newsItems + httpNewsItem
  results = []
  for item in newsItems:
    news = {}
    news['type'] = type
    title = item[1].strip()
    if u'strong' in title:
      news['title'] = title.replace('<strong>', '').replace('</strong>', '').strip()
    else:
      news['title'] = title

    md5 = hashlib.md5()
    md5.update(news['title'])
    news['hash'] = md5.hexdigest()[0:16]
    news['date'] = int(time.mktime(time.strptime(item[2], '%Y-%m-%d')))
    path = item[0]
    if 'infoSingleArticle' in path:
      news['url'] = 'http://jwc.neau.edu.cn/homepage/' + path
    else:
      news['url'] = path
    results.append(news)
  return results

eduNewsCountRe = re.compile(r'共<b>(\d{1,5})</b>条')

def getEduNewsCount(type):
  if type is 'exam':
    url = 'http://jwc.neau.edu.cn/homepage/infoArticleList.do?columnId=254&pagingNumberPer=1'
  else:
    url = 'http://jwc.neau.edu.cn/homepage/infoArticleList.do?columnId=252&pagingNumberPer=1'
  try:
    html = urllib2.urlopen(url= url, timeout=3).read()
  except Exception, e:
    return None
  match = eduNewsCountRe.search(html)
  return int(match.group(1))

newsUrls = {
  'xxgl': 'http://www.neau.edu.cn/xxgl/publist.php', # 学校公告
  'xxyw': 'http://view.neau.edu.cn/xxyw.php', # 学校要闻
  'mtdn': 'http://view.neau.edu.cn/mtdn.php', # 媒体东农
  'jchd': 'http://view.neau.edu.cn/jchd.php', # 基层活动
  'xztd': 'http://view.neau.edu.cn/xztd.php', # 学子天地
  'zsjy': 'http://view.neau.edu.cn/zsjy.php', # 招生就业
  'jxky': 'http://view.neau.edu.cn/jxky.php', # 教学科研
  'hzgj': 'http://view.neau.edu.cn/hzgj.php', # 社会服务
  'ddsp': 'http://view.neau.edu.cn/ddsp.php', # 东农视频
  'rwfc': 'http://view.neau.edu.cn/rwfc.php', # 东农人
  'xxpt': 'http://view.neau.edu.cn/xxpt.php', # 学习平台
  'ddwy': 'http://view.neau.edu.cn/ddwy.php', # 东农文苑
  'jyxx': 'http://view.neau.edu.cn/jyxx.php', # 高教视点
  'tpxw': 'http://view.neau.edu.cn/tpxw.php', # 图片新闻
  'jzzjc': 'http://view.neau.edu.cn/jzzjc.php' # 记着在现场
}

def getSchoolNewsList(type, page):
  if type in newsUrls:
    url = newsUrls[type]
  else:
    return None
  url = url + '?pg=' + str(page)
  return parseSchoolNewsList(url, type)

schoolNewsRe1 = re.compile(r'<a  class="black" href="(\S*?)"  target="_blank">(.*?)</a></td><td height="22" width="20%"><div align="right"><span class="black">\[(\S*?)\]</span>')
schoolNewsReM1 = ['xxgl']
schoolNewsRe2 = re.compile(r'<a href=\'(\S*?)\' target=\'_blank\' class=\'black2\'>(.*?)</a></td><td height="22"><div align="right"><span class="time">\[(\S*?)\]</span>')
schoolNewsReM2 = ['xxyw', 'mtdn', 'jchd', 'xztd', 'zsjy', 'jxky', 'hzgj', 'jyxx', '']
schoolNewsRe3 = re.compile(r'<a class="black2" href="(\S*?)"  target="_blank">(.*?)</a></td><td height="22"><div align="right"><span class="time">\[(\S*?)\]</span>')
schoolNewReM3 = ['tpxw', 'ddwy', 'xxpt', 'rwfc', 'ddsp', 'jzzjc']
def parseSchoolNewsList(url, type):
  try:
    html = urllib2.urlopen(url=url, timeout=3).read()
  except Exception, e:
    return None
  newsReg = schoolNewsRe2
  rootUrl = 'http://view.neau.edu.cn/'
  if type in schoolNewsReM1:
    newsReg = schoolNewsRe1
    rootUrl = 'http://www.neau.edu.cn/'
  if type in schoolNewsReM2:
    newsReg = schoolNewsRe2
  if type in schoolNewReM3:
    newsReg = schoolNewsRe3
  newsItems = newsReg.findall(html)
  results = []
  for item in newsItems:
    news = {}
    path = item[0]
    params = urlparse.parse_qs(path.split('?')[-1], True)
    if 'id' in params:
      news['url'] = rootUrl + 'show.php?id=' + params['id'][0]
    else:
      news['url'] = 'http://'
    news['title'] = item[1].decode('gbk', 'ignore')
    md5 = hashlib.md5()
    md5.update(news['title'])
    news['hash'] = md5.hexdigest()[0:16]
    news['type'] = type
    news['date'] = int(time.mktime(time.strptime(item[2], '%Y-%m-%d')))
    results.append(news)
  return results

schoolNewsPageCountRe = re.compile(r'/<font color="red">(\d{1,4})</font>')
def getSchoolNewsPageCount(type):
  if type in newsUrls:
    url = newsUrls[type]
  else:
    return None
  try:
    html = urllib2.urlopen(url= url, timeout=3).read()
  except Exception, e:
    return None
  match = schoolNewsPageCountRe.search(html)
  return int(match.group(1))

def checkNewNews():
  result = {}
  eduNewsCountFromNet = getEduNewsCount('edu')
  examNewsCountFromNet = getEduNewsCount('exam')

def prepareData():
  eduNewsCount = getEduNewsCount('edu')
  examNewsCount = getEduNewsCount('exam')

  eduNewsList = getEduNewsList('edu', eduNewsCount)
  examNewsList = getEduNewsList('exam', examNewsCount)
  newsTotleList = []
  for k in newsUrls:
    count = getSchoolNewsPageCount(k)
    newsList = []
    for x in xrange(1, count + 1):
      listIn = getSchoolNewsList(k, x)
      if not listIn:
        print k, x
      else:
        newsList +=listIn
    newsTotleList += newsList
  newsTotleList += eduNewsList
  newsTotleList += examNewsList
  print len(newsTotleList)
  for news in newsTotleList:
    news_table.insert().execute(news)
if __name__ == '__main__':
  pass
  #eduNewsList = getEduNewsList('edu', 10)
  #schoolNewsList = getSchoolNewsList('xxyw', 1)
  #print len(schoolNewsList)
  #prepareData()
  #print len(schoolNewsList)
  #print getSchoolNewsPageCount('ddwy')
