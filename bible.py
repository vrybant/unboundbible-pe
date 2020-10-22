#
#  module.py
#  Unbound Bible Python Edition
#

import os
import glob
import sqlite3

def dict_factory(cursor, row) -> dict:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Verse:
    book    = 1
    chapter = 1
    number  = 1
    count   = 1

    def reset(self):
        self.book    = 1
        self.chapter = 1
        self.number  = 1
        self.count   = 1

class Module:
    database     = None
    cursor       = None
    filePath     = ""
    fileName     = ""

    name         = ""
    abbr         = ""
    copyright    = ""
    info         = ""
    filetype     = ""

    language     = "en"
    rightToLeft  = True

    connected    = False
    loaded       = False
    strong       = False
    embedded     = False
    footnotes    = False
    interlinear  = False
    embtitles    = False

    def __init__(self, atPath: str):
        self.filePath = atPath
        self.fileName = atPath#.lastPathComponent
        self.openDatabase()

    def tableExists(cursor, tablename) -> bool:
        query = f"PRAGMA table_info({tablename})" # case insensitive method
        cursor.execute(query)
        return cursor.fetchone() != None

    def openDatabase(self):
        try:
            self.database = sqlite3.connect(self.filePath)
            self.database.row_factory = dict_factory
            self.cursor = self.database.cursor()
        except:
            print("connect database exception")
            return

        query = "select * from Details"
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
        except:
            print("open database exception")
            return

        self.info      = row.get("Information",  "")
        self.info      = row.get("Description", self.info)
        self.name      = row.get("Title",       self.info)
        self.abbr      = row.get("Abbreviation", "")
        self.copyright = row.get("Copyright",    "")
        self.language  = row.get("Language",     "")
        self.strong    = row.get("Strong",       "")

#       self.rightToLeft = getRightToLeft(self.language)
        self.connected = True
#       print(self.info)

class Bible(Module):

    class _Book:
        title   = ""
        abbr    = ""
        number  = 0
        sorting = 0

    def __init__(self, atPath: str):
        super().__init__(atPath)
        self._books = []
        self.loadDatabase() # temp

    def loadDatabase(self):
        if self.loaded: return
        query = "SELECT * FROM Books"

        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except:
            print("loadDatabase exception")
            return

        for row in rows:
            number = row.get("Number", 0)
            if number > 0:
                book = self._Book()
                book.number = number
                book.title = row.get("Name", "")
                book.abbr = row.get("Abbreviation", "")
                self._books.append(book)
                self.loaded = True

    def firstVerse(self) -> Verse:
        v = Verse()
        v.book = self._books[0].number
        return v

    def bookByName(self, name: str) -> int:
        for book in self._books:
            if book.title == name:
                return book.number
        return None

    def getTitles(self) -> [str]:
        result = []
        for book in self._books:
            result.append(book.title)
        return result

    def chaptersCount(self, verse: Verse) -> int:
        query = f"SELECT MAX(Chapter) AS Count FROM Bible WHERE Book = {verse.book}"
        try:
            self.cursor.execute(query)
            row = self.cursor.fetchone()
            return row.get("Count", 0)
        except:
            print("chaptersCount exception")
            return 0

    def getChapter(self, verse: Verse) -> [str]:
        query = f"SELECT * FROM Bible WHERE Book={verse.book} AND Chapter={verse.chapter}"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                text = row.get("Scripture", "")
#               nt = self.isNewTestament(verse.book)
#               text = preparation(text, nt, purge: false)
                result.append(text)
            return result
        except:
            print("getChapter exception")
            return []

    def goodLink(self, verse: Verse) -> bool:
#       result = length(self.getRange(verse)) > 0;
        return True

    def isNewTestament(self, n: int) -> bool:
        return n >= 40 and n < 77

class Shelf():
    current = 3

    def __init__(self):
        self.bibles = []
        self._load()
#       bibles.sort(by: {$0.name < $1.name} )

    def _load(self):
        files = glob.glob("bibles/*.unbound")

        for file in files:
            item = Bible(file)
            self.bibles.append(item)

    def setCurrent(self, index: int):
        if index >= len(self.bibles): return
        self.current = index
        self.bibles[self.current].loadDatabase()

#       if not self.bibles[self.current].goodLink(activeVerse):
#           activeVerse = bibles[current].firstVerse

    def isEmpty(self) -> bool:
        return False if self.bibles else True

currVerse = Verse()
shelf = Shelf()

def currBible():
    return shelf.bibles[shelf.current]
