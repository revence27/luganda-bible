#!  /usr/bin/env python

from lxml import html
from ectomorph import orm
import sys
import settings

BIBLE_TABLE = [
  ('book',      0),
  ('chapter',   0),
  ('verse',     0),
  ('searchdoc', {'type':'TSVECTOR', 'null':True})
]

BOOK_NAME_TABLE = [
  ('version', u''),
  ('position', 0),
  ('name', u'')
]

orm.ORM.connect(dbname = 'revence', user = 'revence')

def lmain(argv):
  if len(argv) < 3:
    sys.stderr.write('%s bibletable zef1.xml [zef2.xml ...] \n' % (argv[0], ))
    return 1
  for arg in argv[2:]:
    with file(arg) as fch:
      doc = html.fromstring(fch.read())
      for bible in doc.cssselect('XMLBIBLE'):
        pos   = 0
        bps   = 0
        bname = unicode(bible.get('biblename')).strip()
        for book in bible.cssselect('BIBLEBOOK'):
          bps = bps + 1
          bkn = unicode(book.get('bname')).strip()
          ftc = orm.ORM.query('booknames', {'version = %s':bname, 'position = %s': bps - 1}, migrations = BOOK_NAME_TABLE)
          chs = 0
          bki = None
          if not ftc.count():
            bki = orm.ORM.store('booknames', {'name':bkn, 'version':bname, 'position':bps - 1})
          else:
            bki = ftc[0]['indexcol']
            if ftc[0]['name'] != bkn:
              orm.ORM.store('booknames', {'name':bkn, 'indexcol':bki})
          for chapter in book.cssselect('CHAPTER'):
            chs = chs + 1
            for verse in chapter.cssselect('VERS'):
              pos = pos + 1
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
                'verse'     : vnm,
                'searchdoc' : lambda c: c.mogrify(u'TO_TSVECTOR(%s)', (thetext, )),
                'chapter'   : cnm,
                'book'      : bnm,
                'position'  : long(pos),
                bname       : thetext
              }
              sys.stderr.write(('\r%2d %3d:%3d %s' % (bnm, cnm, vnm, thetext) + (' ' * 80))[0:75])
              sys.stderr.flush()
              if gat.count():
                it  = gat[0]
                if it[bname] == thetext:
                  continue
                # sys.stderr.write(('\r' + gat.query))
                dat['indexcol'] = it['indexcol']
              ix  = orm.ORM.store(argv[1], dat, migrations = [(bname, u'')])
              # orm.ORM.store(argv[1], {'indexcol':ix, 'searchdoc':lambda _: 'TO_TSVECTOR(verse)'})
          orm.ORM.store('booknames', {'indexcol':bki, 'chapters':chs})

if __name__ == '__main__':
  sys.exit(lmain(sys.argv))
