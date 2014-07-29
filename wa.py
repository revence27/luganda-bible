#!  /usr/bin/env python

import cherrypy
from ectomorph import orm
from jinja2 import Environment, FileSystemLoader as FSL, Template
import os
import sys

env       = Environment(loader  = FSL('templates'))
v1        = 'kjv21'
v2        = 'luganda'
pair      = [v1, v2]

class Passage:
  def __init__(self, btable, *args, **kw):
    self.args         = args
    self.kw           = kw
    self.btable       = btable
    self.default_book = 44

  def query(self):
    return orm.ORM.query(self.btable, {'book = %s':int(self.book or self.default_book)}, sort = ('position', 'ASC'), hooks = {
        'eng': lambda x, y: (x[pair[0]] or u'').decode('utf-8'),
        'lug': lambda x, y: (x[pair[1]] or u'').decode('utf-8')
      })

  @property
  def chapter(self):
    chp = self.kw.get('chapter')
    return int(chp) if chp else chp

  def books(self, ver, pos):
    dem = []
    qry = orm.ORM.query('booknames', {'version = %s': ver}, sort = ('position', 'ASC'))
    for bkn in qry.list():
      dem.append((bkn['position'] - 1, bkn['name'], pos == (bkn['position'] - 1)))
    return dem

  @property
  def book(self):
    bk  = self.kw.get('book', self.default_book)
    return int(bk) if bk else bk

  def describe(self):
    books = [
      'Genesis',
      'Exodus',
      'Leviticus',
      'Numbers',
      'Deuteronomy'
    ]
    return u'%s %s' % (books[int(self.book)] if self.book else '', self.chapter if self.chapter else '')

class Bible:
  def __init__(self, arg):
    self.btable = arg

  @cherrypy.expose
  def index(self, *args, **kw):
    psg = Passage(self.btable, *args, **kw)
    return env.get_template('index.html').render({
      'passage'   : psg,
      'book'      : psg.book,
      'verses'    : psg.query(),
      'books'     : pair
    })

def wmain(argv):
  if len(argv) < 2:
    sys.stderr.write('%s bibletable\n' % (argv[0], ))
    return 1
  orm.ORM.connect(dbname = 'revence', user = 'revence')	#
  cherrypy.server.socket_host = '0.0.0.0'
  cherrypy.quickstart(Bible(argv[1]), '/', {
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
