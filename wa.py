#!  /usr/bin/env python

import cherrypy
from ectomorph import orm
import sys

class Bible:
  @cherrypy.expose
  def index(self):
    return ':o)'

def wmain(argv):
  orm.ORM.connect(dbname = 'revence', user = 'revence', host = 'localhost')
  cherrypy.quickstart(Bible(), '/', {
    '/' : {
      'tools.sessions.on' : True
    }
  })
  return 0

if __name__ == '__main__':
  sys.exit(wmain(sys.argv))
