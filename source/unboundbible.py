"""

Unbound Bible Python Edition
Open Source Application

"""

import os
import bible

from tkinter import *
from tkinter import ttk
from tkinter.ttk import *
from tkinter import filedialog
from tkinter import messagebox

win = Tk()
win.title("Unbound Bible Python Edition")
win.geometry('640x480')
win.iconbitmap('icons/unboundbible.ico')

def popup(event):
    cmenu.tk_popup(event.x_win, event.y_win, 0)

def show_info_bar():
        val = showinbar.get()
        if val:
                infobar.pack(expand=NO, fill=None, side=RIGHT, anchor='se')
        elif not val:
                infobar.pack_forget()

def theme(event=None):
        global bgc,fgc
        val = themechoice.get()
        clrs = clrschms.get(val)
        fgc, bgc = clrs.split('.')
        fgc, bgc = '#'+fgc, '#'+bgc
        memo.config(bg=bgc, fg=fgc)

def highlight_line(interval=100):
        memo.tag_remove("active_line", 1.0, "end")
        memo.tag_add("active_line", "insert linestart", "insert lineend+1c")
        memo.after(interval, toggle_highlight)

def undo_highlight():
        memo.tag_remove("active_line", 1.0, "end")

def toggle_highlight(event=None):
    val = hltln.get()
    undo_highlight() if not val else highlight_line()

##########################################################

def about(event=None):
    messagebox.showinfo("About","Unbound Bible Python Edition \n\n Open Source Application")

def help_box(event=None):
	pass

def exit_editor(event=None):
#   if messagebox.askokcancel("Quit", "Do you really want to quit?"):
    win.destroy()

win.protocol('WM_DELETE_WINDOW', exit_editor) # override close button and redirect to exit_editor

#######################################################################

def new_file(event=None):
    win.title("Untitled")
    global filename
    filename = None
    memo.delete(1.0,END)
    update_line_number()

def open_file(event=None):
    global filename
    filename = filedialog.askopenfilename(defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
    if filename == "": # If no file chosen.
        filename = None # Absence of file.
    else:
        win.title(os.path.basename(filename))
        memo.delete(1.0,END)
        fh = open(filename,"r")
        memo.insert(1.0,fh.read())
        fh.close()
    update_line_number()

def save(event=None):
        global filename
        try:
            f = open(filename, 'w')
            letter = memo.get(1.0, 'end')
            f.write(letter)
            f.close()
        except:
            save_as(event=None)

def save_as(event=None):
    try:
        f = filedialog.asksaveasfilename(initialfile='Untitled.txt',defaultextension=".txt",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
        fh = open(f, 'w')
        textoutput = memo.get(0.0, END)
        fh.write(textoutput)
        fh.close()
        win.title(os.path.basename(f))
    except:
        pass

#########################################################################

def select_all(event=None):
        memo.tag_add('sel', '1.0', 'end')
        return

def on_find():
        t2 = Toplevel(win)
        t2.title('Find')
        t2.geometry('262x65+200+250')
        t2.transient(win)
        Label(t2, text="Find All:").grid(row=0, column=0, sticky='e')
        v=StringVar()
        e = Entry(t2, width=25, textvariable=v)
        e.grid(row=0, column=1, padx=2, pady=2, sticky='we')
        e.focus_set()
        c=IntVar()
        Checkbutton(t2, text='Ignore Case', variable=c).grid(row=1, column=1, sticky='e', padx=2, pady=2)
        Button(t2, text="Find All", underline=0,  command=lambda: search_for(v.get(),c.get(), memo, t2,e)).grid(row=0, column=2, sticky='e'+'w', padx=2, pady=2)
        def close_search():
                memo.tag_remove('match', '1.0', END)
                t2.destroy()
        t2.protocol('WM_DELETE_WINDOW', close_search) #override close button

def search_for(needle,cssnstv, memo, t2,e) :
        memo.tag_remove('match', '1.0', END)
        count =0
        if needle:
                pos = '1.0'
                while True:
                    pos = memo.search(needle, pos, nocase=cssnstv, stopindex=END)
                    if not pos: break
                    lastpos = '%s+%dc' % (pos, len(needle))
                    memo.tag_add('match', pos, lastpos)
                    count += 1
                    pos = lastpos
                memo.tag_config('match', foreground='red', background='yellow')
        e.focus_set()
        t2.title('%d matches found' %count)

########################################################################

def undo(event=None):
    memo.event_generate("<<Undo>>")
    update_line_number()


def redo(event=None):
    memo.event_generate("<<Redo>>")
    update_line_number()


def cut(event=None):
    memo.event_generate("<<Cut>>")
    update_line_number()

def copy(event=None):
    memo.event_generate("<<Copy>>")
    update_line_number()

def paste(event=None):
    memo.event_generate("<<Paste>>")
    update_line_number()

######################################################################

newicon   = PhotoImage(file='icons/new_file.gif')
openicon  = PhotoImage(file='icons/open_file.gif')
saveicon  = PhotoImage(file='icons/Save.gif')
cuticon   = PhotoImage(file='icons/Cut.gif')
copyicon  = PhotoImage(file='icons/Copy.gif')
pasteicon = PhotoImage(file='icons/Paste.gif')
undoicon  = PhotoImage(file='icons/Undo.gif')
redoicon  = PhotoImage(file='icons/Redo.gif')
menubar   = Menu(win)

filemenu = Menu(menubar, tearoff=0 )
filemenu.add_command(label="New", accelerator='Ctrl+N', compound=LEFT, image=newicon, underline=0, command=new_file  )
filemenu.add_command(label="Open", accelerator='Ctrl+O', compound=LEFT, image=openicon, underline =0, command=open_file)
filemenu.add_command(label="Save", accelerator='Ctrl+S',compound=LEFT, image=saveicon,underline=0, command=save)
filemenu.add_command(label="Save as",accelerator='Shift+Ctrl+S', command=save_as)
filemenu.add_separator()
filemenu.add_command(label="Exit", accelerator='Alt+F4', command=exit_editor)
menubar.add_cascade(label="File", menu=filemenu)

editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo",compound=LEFT,  image=undoicon, accelerator='Ctrl+Z', command=undo)
editmenu.add_command(label="Redo",compound=LEFT,  image=redoicon, accelerator='Ctrl+Y', command=redo)
editmenu.add_separator()
editmenu.add_command(label="Cut", compound=LEFT, image=cuticon, accelerator='Ctrl+X', command=cut)
editmenu.add_command(label="Copy", compound=LEFT, image=copyicon,  accelerator='Ctrl+C', command=copy)
editmenu.add_command(label="Paste",compound=LEFT, image=pasteicon, accelerator='Ctrl+V', command = paste)
editmenu.add_separator()
editmenu.add_command(label="Find",underline= 0, accelerator='Ctrl+F', command=on_find)
editmenu.add_separator()
editmenu.add_command(label="Select All", underline=7, accelerator='Ctrl+A', command=select_all)
menubar.add_cascade(label="Edit", menu=editmenu)

viewmenu = Menu(menubar, tearoff=0)
showln = IntVar()
showln.set(1)
viewmenu.add_checkbutton(label="Show Line Number", variable=showln)
showinbar = IntVar()
showinbar.set(1)
viewmenu.add_checkbutton(label="Show Info Bar at Bottom", variable=showinbar, command=show_info_bar)
hltln = IntVar()
viewmenu.add_checkbutton(label="Highlight Current Line", onvalue=1, offvalue=0, variable=hltln, command=toggle_highlight)
themesmenu = Menu(menubar, tearoff=0)
viewmenu.add_cascade(label="Themes", menu=themesmenu)

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
menubar.add_cascade(label="View", menu=viewmenu)

aboutmenu = Menu(menubar, tearoff=0)
aboutmenu.add_command(label="About", command=about)
aboutmenu.add_cascade(label="Help", command=help_box)
menubar.add_cascade(label="About",  menu=aboutmenu)

win.config(menu=menubar) # Returning defined setting for widget

# Shortcut Icon Toolbar

shortcutbar = Frame(win,  height=25)

icons = ['new_file' ,'open_file', 'save', 'cut', 'copy', 'paste', 'undo', 'redo','on_find', 'about']
for i, icon in enumerate(icons):
    tbicon = PhotoImage(file=f'icons/{icon}.gif')
    cmd = eval(icon)
    toolbar = Button(shortcutbar, image=tbicon, command=cmd)
    toolbar.image = tbicon
    toolbar.pack(side=LEFT)

shortcutbar.pack(expand=NO, fill=X)

# Text Widget & ScrollBar widget

memo = Text(win, wrap=WORD, undo=True)
memo.pack(side=RIGHT, expand=YES, fill=BOTH)

scroll=Scrollbar(memo)
memo.configure(yscrollcommand=scroll.set)
scroll.config(command=memo.yview)
scroll.pack(side=RIGHT, fill=Y)

# Combobox

str_var = StringVar()
combolist = []
for bible in module.shelf.bibles:
    combolist.append(bible.name)
combobox = Combobox(win, textvariable = str_var, values=combolist)
combobox.current(1)
combobox.pack(side=TOP, fill=X)

# ListBox

listBox = Listbox(win, height=4)
for title in module.shelf.bibles[3].getTitles():
    listBox.insert(END, title)
listBox.pack(side=LEFT, fill=BOTH)

# ListBox

listBox2 = Listbox(win, height=4)
nums = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
for n in nums:
    listBox2.insert(END, str(n))
listBox2.pack(side=LEFT, fill=BOTH)

# Info Bar

infobar = Label(memo, text='Line: 1 | Column: 0')
infobar.pack(expand=NO, fill=None, side=RIGHT, anchor='se')

# Popup Menu

cmenu = Menu(memo)
for i in ('cut', 'copy', 'paste', 'undo', 'redo'):
    cmd = eval(i)
    cmenu.add_command(label=i, compound=LEFT, command=cmd)
cmenu.add_separator()
cmenu.add_command(label='Select All', underline=7, command=select_all)
memo.bind("<Button-3>", popup)

# Events

memo.bind('<Control-N>', new_file)
memo.bind('<Control-n>', new_file)
memo.bind('<Control-O>', open_file)
memo.bind('<Control-o>', open_file)
memo.bind('<Control-S>', save)
memo.bind('<Control-s>', save)
memo.bind('<Control-A>', select_all)
memo.bind('<Control-a>', select_all)
memo.bind('<Control-f>', on_find)
memo.bind('<Control-F>', on_find)
memo.bind('<KeyPress-F1>', help_box)

memo.tag_configure("active_line", background="ivory2")

win.mainloop()
