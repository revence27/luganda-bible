#!  /usr/bin/env python

import cherrypy
from ectomorph import orm
from datetime import datetime
from jinja2 import Environment, FileSystemLoader as FSL, Template
import os
import settings
import sys

env       = Environment(loader  = FSL('templates'))
pair      = [settings.v1, settings.v2]

class Passage:
  def __init__(self, btable, dbook = 44, dchap = 0, *args, **kw):
    self.args         = args
    self.kw           = kw
    self.btable       = btable
    self.dbook        = dbook
    self.dchap        = dchap

  def query(self):
    bk  = self.book
    cp  = self.chapter
    return self.book_chapter(bk, cp)

  def book_chapter(self, bk, cp):
    return orm.ORM.query(self.btable, {'chapter = %s':cp, 'book = %s':bk}, sort = ('position', 'ASC'), hooks = {
        'eng': lambda x, y: (x[pair[0]] or u'').decode('utf-8'),
        'lug': lambda x, y: (x[pair[1]] or u'').decode('utf-8')
      })

  @property
  def chapter(self):
    chp = self.kw.get('chapter')
    return self.dchap if chp is None else int(chp)

  def books(self, ver, pos):
    dem = []
    qry = orm.ORM.query('booknames', {'version = %s': ver}, sort = ('position', 'ASC'))
    for bkn in qry.list():
      dem.append((bkn['position'], bkn['name'], pos == bkn['position'], bkn['chapters']))
    return dem

  def chapters(self, ver, pos):
    return xrange(self.books(ver, pos)[pos][3])

  @property
  def book(self):
    bk  = self.kw.get('book')
    return self.dbook if bk is None else int(bk)

class Bible:
  def __init__(self, arg, nom):
    self.btable = arg
    self.bname  = nom
    self.tempt  = env.get_template('index.html')

  @cherrypy.expose
  def index(self, *args, **kw):
    psg = Passage(self.btable, dbook = 44, dchap = 0, *args, **kw)
    if os.getenv('BIBLE_DEBUG'):
      self.tempt  = env.get_template('index.html')
    return self.tempt.render({
      'passage'   : psg,
      'appname'   : self.bname,
      'q'         : kw.get('q', ''),
      'book'      : psg.book,
      'chapter'   : psg.chapter,
      'verses'    : psg.query(),
      'versions'  : pair
    })

def wmain(argv):
  apn = None
  if len(argv) < 3:
    try:
      apn = settings.appname
      if len(argv) < 2:
        sys.stderr.write('%s bibletable [appname]\n' % (argv[0], ))
        return 1
    except:
      sys.stderr.write('%s bibletable [appname]\n\nIf appname is not provided in settings.appname, then pass it in as an arg.' % (argv[0], ))
      return 2
  else:
    apn = argv[2]
  orm.ORM.connect(dbname = 'revence', user = 'revence')	#
  cherrypy.server.socket_host = '0.0.0.0'
  cherrypy.quickstart(Bible(argv[1], apn), '/', {
    '/' : {
      'tools.sessions.on' : True
    },
    '/static'  : {
      'tools.staticdir.on'  : True,
      'tools.staticdir.root': os.path.abspath(os.getcwd()),
      'tools.staticdir.dir' : 'static'
    }
  })
  return 0

if __name__ == '__main__':
  sys.exit(wmain(sys.argv))
