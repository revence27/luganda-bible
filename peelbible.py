#!  /usr/bin/env python

from ectomorph import orm
from lxml import html
from lxml.builder import E
import re
import sys

BIBLE_TABLE = [
  ('book',      0),
  ('chapter',   0),
  ('verse',     0)
]

class ComfortableList(list):
  def __setitem__(self, ix, vl):
    mesize  = len(self)
    if ix >= mesize:
      gap = (ix - mesize) + 1
      self.extend([None for _ in range(gap)])
      self[ix] = vl
      return
    super(ComfortableList, self).__setitem__(ix, vl)

  def __getitem__(self, ix):
    if ix < len(self):
      return super(ComfortableList, self).__getitem__(ix)
    pass

class Chapter:
  def __init__(self):
    self.verses = ComfortableList()

  def __getitem__(self, ix):
    return self.verses[ix]

  def __setitem__(self, ix, vl):
    self.verses[ix] = vl

  def append(self, vs):
    self.verses.append(vs)

class Book:
  def __init__(self, name):
    self.name     = name
    self.chapters = ComfortableList()

  def __getitem__(self, ix):
    return self.chapters[ix]

  def __setitem__(self, ix, vl):
    self.chapters[ix] = vl

  def append(self, vs):
    self.chapters.append(vs)

class Bible:
  def __init__(self, btable, version, *args, **kw):
    orm.ORM.connect(*args, **kw)
    self.books    = ComfortableList()
    self.version  = version
    self.btable   = btable

  def __getitem__(self, ix):
    return self.books[ix]

  def __setitem__(self, ix, vl):
    self.books[ix] = vl

  def append(self, vs):
    self.books.append(vs)

  def load_names(self):
    dem = []
    for bn in orm.ORM.query('booknames', "SELECT * FROM booknames WHERE version = 'luganda' ORDER BY position ASC").list():
      dem.append(bn['name'])
    return dem

  def zefania(self):
    names = self.load_names()
    bible = E('XMLBIBLE', biblename = self.version)
    bix = 0
    for book in self.books:
      bix = bix + 1
      bk  = E('BIBLEBOOK', bname = names[bix - 1], bnumber = str(bix))
      cix = 0
      if not book:
        raise Exception, ('Missing book: %d\n' % (bix, ))
      for chapter in book.chapters:
        cix = cix + 1
        chp = E('CHAPTER', cnumber = str(cix))
        vix = 0
        if not chapter:
          raise Exception, ('Missing chapter: %d %d\n' % (bix, cix))
        for verse in chapter.verses:
          vix = vix = vix + 1
          chp.append(E('VERS', (verse or ' ' or ('<!--  Missing (%d %d:%d)  -->' % (bix, cix, vix))).strip(), vnumber = str(vix)))
        bk.append(chp)
      bible.append(bk)
    return bible

  def save(self):
    bk  = 0
    for book in self.books:
      bk  = bk + 1
      chp = 0
      for chapter in book.chapters:
        chp = chp + 1
        ver = 0
        for verse in chapter.verses:
          ver   = ver + 1
          verse = unicode((verse or '')).strip() #.decode('utf-8')
          sys.stderr.write(('%d %d:%d %s' % (bk, chp, ver, verse))[0:75] + '\r')
          sys.stderr.flush()
          gat   = orm.ORM.query(self.btable, {
            # 'book     = %s' : book.name,
            'book     = %s' : bk,
            'chapter  = %s' : chp,
            'verse    = %s' : ver
          }, cols = ['indexcol'], migrations = BIBLE_TABLE)
          dat = {
            # 'book_name'   : book.name,
            'book'        : bk,
            'chapter'     : chp,
            'verse'       : ver,
            self.version  : verse
          }
          if gat.count():
            it              = gat[0]
            dat['indexcol'] = it['indexcol']
            if it[self.version] == verse:
              continue
          orm.ORM.store(self.btable, dat, migrations = [(self.version, u'')])

def pmain(argv):
  if len(argv) < 4:
    sys.stderr.write('%s bibletable biblename html1 [html2 ...]\r\n' % (argv[0], ))
    return 1
  bible = Bible(argv[1], argv[2], dbname = 'revence', user = 'revence', host = 'localhost')
  for arg in argv[3:]:
    with file(arg) as fch:
      bk, chp = re.split(r'\s+', re.sub(r'\D+', ' ', arg).strip())
      bk, chp = int(bk) - 1, int(chp) - 1
      book    = bible[bk]
      content = html.fromstring(fch.read())
      title   = re.sub(r'\d+$', '', content.cssselect('TITLE')[0].text.split('/')[-1].strip()).strip()
      if not book:
        book      = Book(title)
        bible[bk] = book
      chapter = book[chp]
      if not chapter:
        chapter   = Chapter()
        book[chp] = chapter
      for verse in content.cssselect('#textBody .verse'):
        vpos          = int(verse.get('id')) - 1
        thetext       = verse.tail
        chapter[vpos] = thetext
  sys.stdout.write(html.tostring(bible.zefania(), pretty_print = True, method = 'xml'))
  bible.save()
  return 0

if __name__ == '__main__':
  sys.exit(pmain(sys.argv))
