#
#  bible.py
#  Unbound Bible Python Edition
#

import os
import glob
import sqlite3

from lib import *

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
    filepath     = ""
    filename     = ""

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
    default      = False
    embtitles    = False

    def __init__(self, path: str):
        self.filepath = path
        self.filename = os.path.basename(path)
        self.openDatabase()

    def dict_factory(self, cursor, row) -> dict:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def tableExists(cursor, tablename) -> bool:
        query = f"PRAGMA table_info({tablename})" # case insensitive method
        cursor.execute(query)
        return cursor.fetchone() != None

    def openDatabase(self):
        try:
            self.database = sqlite3.connect(self.filepath)
            self.database.row_factory = self.dict_factory
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
        self.default   = row.get("Default",      "")

#       self.rightToLeft = getRightToLeft(self.language)
        self.connected = True
#       print(self.info)

class Bible(Module):

    class Book:
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
                book = self.Book()
                book.number = number
                book.title = row.get("Name", "")
                book.abbr = row.get("Abbreviation", "")
                self._books.append(book)
                self.loaded = True

    def firstVerse(self) -> Verse:
        v = Verse()
        v.book = self._books[0].number
        return v

    def bookByNum(self, number: int) -> Book:
        for book in self._books:
            if book.number == number:
                return book
        return None

    def bookByName(self, name: str) -> Book:
        for book in self._books:
            if book.title == name:
                return book
        return None

    def verseToStr(self, verse: Verse, full: bool) -> str:
        book = self.bookByNum(verse.book)
        if not book: return ''
        title = book.title if full else book.abbr
        space = '' if '.' in title else ' '
        result = f"{title}{space}{verse.chapter}:{verse.number}"
        if verse.count > 1:
            result += '-' + str(verse.number + verse.count - 1)
        return result

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

    def getRange(self, verse: Verse) -> [str]:
        query = f"SELECT * FROM Bible WHERE Book={verse.book} AND Chapter={verse.chapter} " + \
                f"AND Verse>={verse.number} AND Verse<{verse.number + verse.count}"
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
            print("getRange exception")
            return []

    def getSearch(self, target: str) -> [str]:
        query = f"SELECT * FROM Bible WHERE Scripture LIKE '%{target}%'"
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            result = []
            for row in rows:
                book    = row.get("Book",    0)
                chapter = row.get("Chapter", 0)
                verse   = row.get("Verse",   0)
                script  = row.get("Scripture", "")

                title = currBible().bookByNum(book).title
                text = f"{title} {chapter}:{verse} {script}"
                result.append(text)
            return result
        except:
            print("getSearch exception")
            return []

    def goodLink(self, verse: Verse) -> bool:
        return len(self.getRange(verse)) > 0

    def isNewTestament(self, n: int) -> bool:
        return n >= 40 and n < 77

class Bibles(list):
    currBible = None

    def __init__(self):
        self._load()
        self.sort(key=lambda item: item.name)

    def _load(self):
        files = glob.glob("modules/*.unbound")

        for file in files:
            item = Bible(file)
            self.append(item)

    def setCurrent(self, name: str):
        self.currBible = self[0]

        for bible in self:
            if bible.name == name:
                self.currBible = bible
                break

        self.currBible.loadDatabase()

        global currVerse
        if not self.currBible.goodLink(currVerse):
            currVerse = self.currBible.firstVerse()

    def isEmpty(self) -> bool:
        return False if self.items else True

    def getDefaultBible(self) -> str:
        result = ""
        for bible in self:
            if bible.default:
                if bible.language == languageCode() : return bible.name
                if bible.language == "en": result = bible.name
        return result

def currBible():
    return bibles.currBible

currVerse = Verse()
bibles = Bibles()
