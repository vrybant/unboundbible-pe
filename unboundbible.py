"""

Unbound Bible Python Edition
Open Source Application

"""

import os
import sys
import re
import configparser
import glob
import sqlite3
import __future__
import locale

assert sys.version_info >= (3, 9), "Use Python 3.9 or newer"

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

############### LIB ##################

def languageCode() -> str:
    try:
        return locale.getdefaultlocale()[0][0:2]
    except:
        return "en"

############## MODEL #################

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
        try:
            self.database = sqlite3.connect(self.filepath)
            self.database.row_factory = self.dict_factory
            self.cursor = self.database.cursor()
        except:
            print("connect database exception")
            return
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

    def getTitles(self) -> list[str]:
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

    def getChapter(self, verse: Verse) -> list[str]:
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

    def getRange(self, verse: Verse) -> list[str]:
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

    def getSearch(self, target: str) -> list[str]:
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
        files = glob.glob("data/*.unbound")

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

############### GUI ##################

# Window

win = Tk()
win.withdraw()
win.title("Unbound Bible")
if os.name == 'nt': win.iconbitmap('icons/unboundbible.ico')
fontSize = 11

def popup(event):
    pmmenu.tk_popup(event.x_root, event.y_root, 0)

def theme(event=None):
    global bgc,fgc
    val = themechoice.get()
    clrs = clrschms.get(val)
    fgc, bgc = clrs.split('.')
    fgc, bgc = '#'+fgc, '#'+bgc
    bookBox.config(bg=bgc, fg=fgc)
    chapterBox.config(bg=bgc, fg=fgc)
    memo.config(bg=bgc, fg=fgc)

#   combostyle = ttk.Style()
#   settings = {'TCombobox':{'configure':{'selectbackground': 'red','fieldbackground': 'blue','background': 'green'}}}
#   combostyle.theme_create('combostyle', parent='alt', settings = settings)
#   combostyle.theme_use('combostyle')

#-------------------------------------------------------------------

def about():
    messagebox.showinfo("About","Unbound Bible Python Edition \n\n Open Source Application")

def help_box():
    pass

def find():
    entry.focus_set()

def compare():
    loadCompare()

def strong():
    loadStrong()

def copy():
    memo.event_generate("<<Copy>>")
#   s = win.clipboard_get()

def select_all():
        memo.focus_set()
        memo.tag_add('sel', '1.0', 'end')
        return

def on_exit(event=None):
    saveConfig()
    win.destroy()

#-------------------------------------------------------------------

# Menu

copyicon = PhotoImage(file='icons/copy.gif')
compricon = PhotoImage(file='icons/compare.gif')

menubar   = Menu(win)

toolsmenu = Menu(menubar, tearoff=0 )
toolsmenu.add_command(label="Find",underline= 0, accelerator='Ctrl+F', command=find)
toolsmenu.add_command(label="Compare",underline= 0, command=compare)

themesmenu = Menu(menubar, tearoff=0)
toolsmenu.add_cascade(label="Themes", menu=themesmenu)

clrschms = {
'1. Default White': '000000.FFFFFF',
'2. Greygarious Grey':'83406A.D1D4D1',
'3. Lovely Lavender':'202B4B.E1E1FF' ,
'4. Aquamarine': '5B8340.D1E7E0',
'5. Bold Beige': '4B4620.FFF0E1',
'6. Cobalt Blue':'ffffBB.3333aa',
'7. Olive Green': 'D1E7E0.5B8340',
}

themechoice= StringVar()
themechoice.set('1. Default White')
for k in sorted(clrschms):
    themesmenu.add_radiobutton(label=k, variable=themechoice, command=theme)

menubar.add_cascade(label="Tools", menu=toolsmenu)
toolsmenu.add_separator()
toolsmenu.add_command(label="Exit", accelerator='Alt+F4', command=on_exit)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Copy", compound=LEFT, image=copyicon,  accelerator='Ctrl+C', command=copy)
editmenu.add_command(label="Select All", underline=7, accelerator='Ctrl+A', command=select_all)
menubar.add_cascade(label="Edit", menu=editmenu)

aboutmenu = Menu(menubar, tearoff=0)
aboutmenu.add_command(label="About", command=about)
aboutmenu.add_cascade(label="Help", command=help_box)
menubar.add_cascade(label="About",  menu=aboutmenu)

win.config(menu=menubar) # Returning defined setting for widget

# Toolbar

toolbar = Frame(win,  height=25)

icons = ['compare', 'copy', 'about']
for i, icon in enumerate(icons):
    image = PhotoImage(file=f'icons/{icon}.gif')
    button = Button(toolbar, image=image, command=eval(icon))
    button.image = image
    button.grid(row=0,column=i)

# Entry

def return_entry(event=None):
    text = entry.get()
    loadSearch(text)

entryVar = StringVar()
entry = Entry(win, width=25, textvariable=entryVar)
entry.bind('<Return>', return_entry)

# Status Bar

status = Label(win, text="")

# Text & ScrollBar

def memo_on_click(event=None):
    pass

def memoLoad(text: str):
    memo.config(state=NORMAL)
    memo.delete(1.0, END)
    memo.insert(1.0, text)
#   memo.config(state=DISABLED)

memo = Text(win, wrap=WORD, undo=True, font=("TkTextFont", fontSize+1))
memo.bind('<ButtonRelease-1>', memo_on_click)

scroll=Scrollbar(win)
memo.configure(yscrollcommand=scroll.set)
scroll.config(command=memo.yview)

# Combobox

def loadCombobox() -> list[str]:
    combolist = []
    for bible in bibles:
        combolist.append(" " + bible.name)
    return combolist

def comboboxSelect(event=None):
    if event: # this works only with bind because `command=` doesn't send event
        value = combobox.get().strip()
        bibles.setCurrent(value)
        makeBookList()
        gotoVerse(currVerse)
        status['text'] = " " + currBible().filename + " | " + currBible().info

def comboboxSetCurrent(value: str):
    index = 0
    for item in combolist:
        if item.strip() == value: combobox.current(index)
        index += 1

combolist = loadCombobox()
combobox = Combobox(win, textvariable = StringVar(), values=combolist, font=("TkTextFont", fontSize-1))
combobox.bind("<<ComboboxSelected>>", comboboxSelect)

# BookBox

def makeBookList():
    bookBox.delete(0,END)
    for title in currBible().getTitles():
        bookBox.insert(END, " " + title)

def bookBoxSelect(event=None):
    if event:
        curselection = bookBox.curselection()
        if curselection:
            selection = curselection[0]
            titles = currBible().getTitles()
            sbook = titles[selection]
            book = currBible().bookByName(sbook).number
            if book:
                currVerse.reset()
                currVerse.book = book
                loadChapter()
                makeChapterList()

bookBox = Listbox(win, height=4,  activestyle="none", exportselection=False, font=("TkTextFont", fontSize))
bookBox.bind("<<ListboxSelect>>", bookBoxSelect)

# ChapterBox

def makeChapterList():
    chapterBox.delete(0,END)
    max = currBible().chaptersCount(currVerse)
    for n in range(1, max + 1):
        chapterBox.insert(END, " " + str(n))
#   if ChapterBox.Items.Count = n then Exit;

def chapterBoxSelect(event=None):
    if event:
        selection = chapterBox.curselection()
        if selection:
            chapter = selection[0] + 1
            currVerse.chapter = chapter;
            currVerse.number = 1;
            currVerse.count = 1;
            loadChapter()

chapterBox = Listbox(win, height=4, activestyle="none", exportselection=False, font=("TkTextFont", fontSize))
chapterBox.bind("<<ListboxSelect>>", chapterBoxSelect)

# Popup Menu

pmmenu = Menu(memo, tearoff=0)
cmd_copy = eval('copy')
pmmenu.add_command(label='Copy', compound=LEFT, command=cmd_copy)
pmmenu.add_command(label='Select All', underline=7, command=select_all)
memo.bind("<Button-3>", popup)

# Events

memo.bind('<Control-A>', select_all)
memo.bind('<Control-a>', select_all)
memo.bind('<Control-f>', find)
memo.bind('<Control-F>', find)
memo.bind('<KeyPress-F1>', help_box)

memo.tag_configure("active_line", background="ivory2")

# Frame 

win.rowconfigure(2, minsize=300, weight=1)
win.rowconfigure(3, minsize=8)
win.columnconfigure(2, weight=1)

toolbar.grid(row=0,column=0, columnspan=3, sticky=W)
entry.grid(row=0, column=2, columnspan=2, padx=2, sticky=E)
combobox.grid(row=1, column=0, columnspan=2, padx=2, sticky=E+W)
bookBox.grid(row=2, column=0, padx=2, pady=2, sticky=E+W+S+N)
chapterBox.grid(row=2, column=1, padx=2, pady=2, sticky=E+W+S+N)
memo.grid(row=1, column=2, rowspan=2, padx=2, sticky=NSEW)
scroll.grid(row=1, column=3, rowspan=2, sticky=NS)
status.grid(row=3, column=0, columnspan=3, sticky=W)

def gotoVerse(verse: Verse):
    if not currBible().goodLink(verse): return
    currVerse = verse
    makeChapterList()
    loadChapter()

def applyTags(s: str) -> str:
    s = re.sub( '<S>',' ', s)
    s = re.sub( '<i>','[', s)
    s = re.sub('</i>',']', s)
    s = re.sub(r'<.*?>','',s)
    return s

def loadChapter():
    strings = currBible().getChapter(currVerse)
    text = ""
    for i in range(len(strings)):
        s = applyTags(strings[i])
        text += f" {i+1} {s}\n"
    memoLoad(text)

def loadSearch(target: str):
    if len(target) < 3:  return
    strings = currBible().getSearch(target)
    text = ""
    for s in strings:
        s = applyTags(s)
        text += f"{s}\n\n"
    if not strings:
        text = f"You search for '{target}' produced no results."
    memoLoad(text)
    status['text'] = f" {len(strings)} verses found."

def loadCompare():
    num = memo.index(INSERT).split('.')[0] 
    currVerse.number = int(num)
    if not currBible().goodLink(currVerse):
        currVerse.number = 1

    text = currBible().verseToStr(currVerse, True) + '\n\n'
    for bible in bibles:
        value = bible.getRange(currVerse)
        if value:
            info = bible.name
            s = applyTags(value[0])
            text += f"{info}\n{s}\n\n"
    memoLoad(text)

def loadStrong():
    try:
        num = memo.selection_get()
        currVerse.number = int(num)
    except:
        messagebox.showwarning("Tooltip","Select the strong number!")
        return

    text = currBible().verseToStr(currVerse, True) + '\n\n'
    for bible in bibles:
        value = bible.getRange(currVerse)
        if value:
            info = bible.name
            s = applyTags(value[0])
            text += f"{info}\n{s}\n\n"
#   memoLoad(text)

# Config

def saveConfig():
    config = configparser.ConfigParser()
    config.read("config.ini", "utf8")

    if "Application" not in config.sections():
        config.add_section("Application")

    config.set('Application','CurrentBible', currBible().name)

    config.set('Application','left', f'{win.winfo_x()}')
    config.set('Application','top',  f'{win.winfo_y()}')
    config.set('Application','width',  f'{win.winfo_width()}')
    config.set('Application','height', f'{win.winfo_height()}')

    f = open('config.ini', 'w', encoding='utf8')
    config.write(f)
    f.close()

def readConfig():
    config = configparser.ConfigParser()
    config.read("config.ini", "utf8")

    try:
        currentBible = config.get('Application', 'CurrentBible')
    except:
        currentBible = bibles.getDefaultBible()

    bibles.setCurrent(currentBible)
    comboboxSetCurrent(currBible().name)

    try:
        left = config.get('Application', 'left')
        top  = config.get('Application', 'top')
        width  = config.get('Application', 'width')
        height = config.get('Application', 'height')
        win.geometry(f'{width}x{height}+{left}+{top}')
    except:
        win.geometry('640x480')

# Init

readConfig()
makeBookList()
makeChapterList()
loadChapter()
status['text'] = " " + currBible().filename + " | " + currBible().info

win.protocol("WM_DELETE_WINDOW", on_exit)
win.deiconify()
win.mainloop()
