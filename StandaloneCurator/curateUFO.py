import sys
import os
import datetime
import glob
import shutil
from CameraCurator import curateFolder

import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tkinter.messagebox as tkMessageBox
from tkinter import Frame, Listbox, Menu, PhotoImage, END, Button
from tkinter.ttk import Label, Style, LabelFrame, Scrollbar
from PIL import ImageTk

import logging
import logging.handlers
import traceback

global_bg = "Black"
global_fg = "Gray"

version = 1.0
log_directory = 'ufoCurator'


def log_timestamp():
    """ Returns timestamp for logging.
    """
    return datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


class Catcher:
    """ Used for catching unhandled exceptions.
    """
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                # args = apply(self.subst, args)
                args = self.subst(*args)  # python3
            # return apply(self.func, args)
            return self.func(*args)
        except SystemExit as msg:
            raise SystemExit(msg)
        except:
            log.critical(traceback.format_exc())
            tkMessageBox.showerror("Unhandled exception", "An unhandled exception has occured!\nPlease see the last logfile in the " + log_directory + " for more information!")
            sys.exit(0)


class StyledButton(Button):
    """ Button with style. 
    """
    def __init__(self, *args, **kwargs):
        Button.__init__(self, *args, **kwargs)

        self.configure(foreground = global_fg, background = global_bg, borderwidth = 3)


class ufoCuratorGui(Frame):
    def __init__(self, parent, dir_path=None):
        Frame.__init__(self, parent, bg = global_bg)
        parent.configure(bg = global_bg)  # Set backgound color
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        self.grid(sticky="NSEW")  # Expand frame to all directions
        # self.grid_propagate(0)

        self.parent = parent
        self.dir_path = dir_path
        # Initilize GUI
        self.initUI()

        # If the directory path was given, open it
        if dir_path is not None:
            self.askdirectory(dir_path=dir_path)
    
    def get_jpg_list(self):
        flist = []
        for root, subdirs, files in os.walk(self.dir_path):
            for fn in files:
                if 'P.jpg' in fn:
                    flist.append(os.path.join(root, fn))
        return flist

    def askdirectory(self, dir_path=''):

        if self.dir_path == '':
            old_dir_path = os.getcwd()
        else:
            old_dir_path = self.dir_path
    
        self.dir_path = dir_path
        if self.dir_path == '':
            self.dir_path = tkFileDialog.askdirectory(title='Select Folder', initialdir=old_dir_path)

        if self.dir_path == '':
            self.dir_path = old_dir_path
        else:
            self.imagelist = self.get_jpg_list()
            self.update_listbox(self.imagelist)

            # Update dir label
            self.parent.wm_title("ufoCurator: " + self.dir_path)
            if len(self.imagelist) > 0:
                self.move_top(0)  # Move listbox cursor to the top

    def move_top(self, event):
        if self.listbox is not self.parent.focus_get():
            self.listbox.focus()
        self.listbox.activate(0)
        self.listbox.selection_clear(0, END)
        self.listbox.selection_set(0)
        self.listbox.see(0)
        self.update_image(0)

    def update_listbox(self, bin_list):
        """ Updates the listbox with the current entries.
        """
        self.listbox.delete(0, END)
        for line in sorted(bin_list):
            self.listbox.insert(END, line)
            
    def update_image(self, status):
        if self.dir_path is not None:
            if len(self.imagelist) > 0:
                self.current_image = self.listbox.get(self.listbox.curselection()[0])
                img_path = self.current_image # os.path.join(self.dir_path, self.current_image)
                imgdata = ImageTk.PhotoImage(file = img_path)
                self.imagelabel = Label(self, image = imgdata)
                self.imagelabel.image = imgdata
                self.imagelabel.grid(row=3, column=3, rowspan = 4, columnspan = 3)

    def show_about(self):
        tkMessageBox.showinfo("About",
            """ufoCurator version: """ + str(version) + """
        Simple tool to clean out bad data from a UFO dataset.\n
        Usage: select a folder from the File menu, click Clean.\n
        Bad data will be moved to a folder 'bad',\n
        You can also manually move files to 'bad' or back again\n
    """)


    def initUI(self):
        self.parent.title("UFO Curator")

        # Configure the style of each element
        s = Style()
        s.configure("TButton", padding=(0, 5, 0, 5), font='serif 10', background = global_bg)
        s.configure('TLabelframe.Label', foreground =global_fg, background=global_bg)
        s.configure('TLabelframe', foreground =global_fg, background=global_bg, padding=(3, 3, 3, 3))
        s.configure("TRadiobutton", foreground = global_fg, background = global_bg)
        s.configure("TLabel", foreground = global_fg, background = global_bg)
        s.configure("TCheckbutton", foreground = global_fg, background = global_bg)
        s.configure("Vertical.TScrollbar", background=global_bg, troughcolor = global_bg)

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)

        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)

        # Make menu
        self.menuBar = Menu(self.parent)
        self.parent.config(menu=self.menuBar)

        # File menu
        fileMenu = Menu(self.menuBar, tearoff=0)
        fileMenu.add_command(label = "Open folder", command = self.askdirectory)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.quitApplication)
        self.menuBar.add_cascade(label="File", underline=0, menu=fileMenu)
        self.menuBar.entryconfig("File", state = "normal")

        # Help Menu
        helpMenu = Menu(self.menuBar, tearoff=0)
        helpMenu.add_command(label = "About", command = self.show_about)
        self.menuBar.add_cascade(label = "Help", underline=0, menu=helpMenu)

        # actions panel
        self.action_panel = LabelFrame(self, text=' Actions')
        self.action_panel.grid(row = 0, column = 0, sticky = "W", padx=2, pady=5, ipadx=5, ipady=5)
        curate_button = StyledButton(self.action_panel, text ="Clean", width=5, command = lambda: self.curateData())
        curate_button.grid(row = 2, column = 7, rowspan = 2)
        moveone_button = StyledButton(self.action_panel, text ="Clean One", width=9, command = lambda: self.moveone())
        moveone_button.grid(row = 2, column = 8, rowspan = 2)
        moveback_button = StyledButton(self.action_panel, text ="Move Back", width=9, command = lambda: self.moveback())
        moveback_button.grid(row = 2, column = 9, rowspan = 2)

        # Listbox
        self.scrollbar = Scrollbar(self)
        self.listbox = Listbox(self, width = 47, yscrollcommand=self.scrollbar.set, exportselection=0, activestyle = "none", bg = global_bg, fg = global_fg)
        self.listbox.config(height = 37)  # Listbox size
        self.listbox.grid(row = 4, column = 0, rowspan = 7, columnspan = 2, sticky = "NS")  # Listbox position
        self.scrollbar.grid(row = 4, column = 2, rowspan = 7, sticky = "NS")  # Scrollbar size
        self.listbox.bind('<<ListboxSelect>>', self.update_image)
        self.scrollbar.config(command = self.listbox.yview)

        # IMAGE
        if getattr(sys, 'frozen', False) is True:
            # frozen
            dir_ = os.path.dirname(sys.executable)
        else:
            # unfrozen
            dir_ = os.path.dirname(os.path.realpath(__file__))
        try:
            # Show the TV test card image on program start
            noimage_data = open(os.path.join(dir_,'noimage.bin'), 'rb').read()
            noimage = PhotoImage(data = noimage_data)
        except:
            noimage = None

        self.imagelabel = Label(self, image = noimage)
        self.imagelabel.image = noimage
        self.imagelabel.grid(row=3, column=3, rowspan = 4, columnspan = 3)

    def quitApplication(self):
        print('quitting')
        quitApp()

    def curateData(self):
        if self.dir_path is not None:
            log.info(self.dir_path)
            doCuration(self.dir_path)
            self.imagelist = self.get_jpg_list()
            self.update_listbox(self.imagelist)

    def moveone(self):
        if self.dir_path is not None:
            self.current_image = self.listbox.get(self.listbox.curselection()[0])
            img_path = self.current_image
            moveOne(self.dir_path, img_path, False)
            self.imagelist = self.get_jpg_list()
            self.update_listbox(self.imagelist)

    def moveback(self):
        if self.dir_path is not None:
            self.current_image = self.listbox.get(self.listbox.curselection()[0])
            img_path = self.current_image
            moveOne(self.dir_path, img_path, True)
            self.imagelist = self.get_jpg_list()
            self.update_listbox(self.imagelist)


def quitApp():
    """ Cleanly exits """
    root.quit()
    root.destroy()


def moveOne(path, img_path, moveback):
    if moveback is False:
        badfolder=os.path.join(path, 'bad')
        os.makedirs(badfolder, exist_ok=True)
        if 'bad' in img_path:
            log.info('cant curate something already curated')
            return  # can't move clean something thats already been curated out
    else:
        if 'bad' not in img_path:
            log.info('cant restore something not curated')
            return  # can't move something back that hasn't been curated out

    rootpth = path
    curpth, imgname = os.path.split(img_path)
    log.info(curpth + ', ' + imgname)
    srcpth = curpth
    if moveback is False:
        targpth = badfolder
    else:
        targyr = imgname[1:5]
        targym = imgname[1:7]
        targymd = imgname[1:9]
        if targyr not in rootpth:
            rootpth = os.path.join(rootpth, targyr)
        if targym not in rootpth:
            rootpth = os.path.join(path, targym)
        if targymd not in rootpth:
            rootpth = os.path.join(rootpth, targymd)
        targpth = rootpth
        os.makedirs(targpth, exist_ok=True)
    fbase = imgname[:-5]+'*'
    fils = glob.glob1(srcpth, fbase)
    for f in fils:
        shutil.move(os.path.join(srcpth, f), targpth)
    return

def doCuration(path):
    if getattr(sys, 'frozen', False) is True:
        # frozen
        dir_ = os.path.dirname(sys.executable)
    else:
        # unfrozen
        dir_ = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(dir_, 'curation.ini')
    if os.path.isdir(path):
        badfolder=os.path.join(path, 'bad')
        for root, subdirs, files in os.walk(path):
            for subdir in subdirs:
                if subdir[:2] == '20': 
                    fn = os.path.join(root, subdir)
                    log.info(fn)
                    curateFolder.main(config_file, fn, badfolder, log)
                    log.info('---')
    else:
        print('invalid arguments')


if __name__ == '__main__':
    print('running curation process')
    if len(sys.argv) < 2:
        # Catch unhandled exceptions in Tkinter
        tk.CallWrapper = Catcher

        # Initialize logging, store logfile in AppData
        # For Windows
        if sys.platform == 'win32':
            log_directory = os.path.join(os.getenv('APPDATA'), log_directory)
        else:
            # For Unix
            log_directory = os.path.expanduser(os.path.join("~", "." + log_directory))

        os.makedirs(log_directory, exist_ok=True)
        log = logging.getLogger(__name__)
        log.setLevel(logging.INFO)

        log_file = os.path.join(log_directory, log_timestamp() + '.log')
        handler = logging.handlers.TimedRotatingFileHandler(log_file, when='D', interval=1)  # Log to a different file each day
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s-%(module)s-line:%(lineno)d - %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
        handler.setFormatter(formatter)
        log.addHandler(handler)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(fmt='%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
        ch.setFormatter(formatter)
        log.addHandler(ch)

        # Log program start
        log.info("Program start")
        log.info("Version: " + str(version))

        # Initialize main window
        root = tk.Tk()
        # Set window position and size

        if sys.platform == 'win32':
            root.geometry('+0+0')
            #root.wm_state('zoomed')
        else:
            root.geometry('+0+0')

        # Set window icon
        try:
            root.iconbitmap(os.path.join('.', 'icon.ico'))
        except:
            pass

        # Init the BinViewer UI
        app = ufoCuratorGui(root)

        # Add a special function which controls what happens when when the close button is pressed
        root.protocol('WM_DELETE_WINDOW', app.quitApplication)

        root.mainloop()
    else:
        doCuration(sys.argv[1])
