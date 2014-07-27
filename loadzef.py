#!  /usr/bin/env python

from lxml import html
from ectomorph import orm
import sys

BIBLE_TABLE = [
  ('book',      0),
  ('chapter',   0),
  ('verse',     0)
]

orm.ORM.connect(dbname = 'revence', user = 'revence', host = 'localhost')

def lmain(argv):
  if len(argv) < 3:
    sys.stderr.write('%s bibletable zef1.xml [zef2.xml ...] \n' % (argv[0], ))
    return 1
  for arg in argv[2:]:
    with file(arg) as fch:
      doc = html.fromstring(fch.read())
      for bible in doc.cssselect('XMLBIBLE'):
        bname = bible.get('biblename')
        for book in bible.cssselect('BIBLEBOOK'):
          for chapter in book.cssselect('CHAPTER'):
            for verse in chapter.cssselect('VERS'):
              vnm = int(verse.get('vnumber')) - 1
              cnm = int(chapter.get('cnumber')) - 1
              bnm = int(book.get('bnumber')) - 1
              gat = orm.ORM.query(argv[1], {
                'verse    = %s' : vnm,
                'chapter  = %s' : cnm,
                'book     = %s' : bnm,
              }, cols = ['indexcol', bname], migrations = BIBLE_TABLE + [(bname, u'')])
              thetext = unicode(verse.text)
              dat = {
                'verse'   : vnm,
                'chapter' : cnm,
                'book'    : bnm,
                bname     : thetext
              }
              sys.stderr.write(('\r%2d %3d:%3d %s' % (bnm, cnm, vnm, thetext) + (' ' * 80))[0:75])
              sys.stderr.flush()
              if gat.count():
                it  = gat[0]
                if it[bname] == thetext:
                  continue
                dat['indexcol'] = it['indexcol']
              orm.ORM.store(argv[1], dat, migrations = [(bname, u'')])

if __name__ == '__main__':
  sys.exit(lmain(sys.argv))
