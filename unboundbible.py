"""

Unbound Bible Python Edition
Open Source Application

"""

import os
import sys
import re
import configparser

assert sys.version_info >= (3, 9), "Use Python 3.9 or newer"

from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox
from bible import *

# Window

win = Tk()
win.withdraw()
win.title("Unbound Bible")
if os.name == 'nt': win.iconbitmap('icons/unboundbible.ico')

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

#######################################################################

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

######################################################################

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

memo = Text(win, wrap=WORD, undo=True)
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
combobox = Combobox(win, textvariable = StringVar(), values=combolist)
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

bookBox = Listbox(win, height=4)
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

chapterBox = Listbox(win, height=4)
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
