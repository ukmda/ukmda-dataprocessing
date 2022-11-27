from tksheet import Sheet
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Frame, Menu
from tkinter import simpledialog
import boto3
import shutil
import datetime
import os
import pandas
import paramiko
import json 
import time
from scp import SCPClient

import camTable as ct


class infoDialog(simpledialog.Dialog):
    def __init__(self, parent, title, location, lat, lon, ele, user, email, sshkey='', id=''):
        self.data = []
        self.data.append(id)
        self.data.append(lat)
        self.data.append(lon)
        self.data.append(ele)
        self.data.append(location)
        self.data.append('')
        self.data.append(user)
        self.data.append(email)
        self.data.append(sshkey)

        super().__init__(parent, title)    

    def body(self, frame):
        # print(type(frame)) # tkinter.Frame
        self.camid_label = tk.Label(frame, width=25, text="RMS ID")
        self.camid_label.pack()
        self.camid_box = tk.Entry(frame, width=25)
        self.camid_box.insert(tk.END, self.data[0])
        self.camid_box.pack()

        self.lat_label = tk.Label(frame, width=25, text="Latitude (+N)")
        self.lat_label.pack()
        self.lat_box = tk.Entry(frame, width=25)
        self.lat_box.insert(tk.END, self.data[1])
        self.lat_box.pack()

        self.lon_label = tk.Label(frame, width=25, text="Longitude (-W)")
        self.lon_label.pack()
        self.lon_box = tk.Entry(frame, width=25)
        self.lon_box.insert(tk.END, self.data[2])
        self.lon_box.pack()

        self.ele_label = tk.Label(frame, width=25, text="Elevation (m)")
        self.ele_label.pack()
        self.ele_box = tk.Entry(frame, width=25)
        self.ele_box.insert(tk.END, self.data[3])
        self.ele_box.pack()

        self.location_label = tk.Label(frame, width=25, text="Location")
        self.location_label.pack()
        self.location_box = tk.Entry(frame, width=25)
        self.location_box.insert(tk.END, self.data[4])
        self.location_box.pack()

        self.direction_label = tk.Label(frame, width=25, text="direction")
        self.direction_label.pack()
        self.direction_box = tk.Entry(frame, width=25)
        self.direction_box.pack()

        self.ownername_label = tk.Label(frame, width=25, text="owner name")
        self.ownername_label.pack()
        self.ownername_box = tk.Entry(frame, width=25)
        self.ownername_box.insert(tk.END, self.data[6])
        self.ownername_box.pack()

        self.email_label = tk.Label(frame, width=25, text="email address")
        self.email_label.pack()
        self.email_box = tk.Entry(frame, width=25)
        self.email_box.insert(tk.END, self.data[7])
        self.email_box.pack()

        self.sshkey_label = tk.Label(frame, width=25, text="SSH key")
        self.sshkey_label.pack()
        self.sshkey_box = tk.Entry(frame, width=50)
        self.sshkey_box.insert(tk.END, self.data[8])
        self.sshkey_box.pack()

    def ok_pressed(self):
        self.data[0] = self.camid_box.get().strip()
        self.data[1] = self.lat_box.get().strip()
        self.data[2] = self.lon_box.get().strip()
        self.data[3] = self.ele_box.get().strip()
        self.data[4] = self.location_box.get().strip()
        self.data[5] = self.direction_box.get().strip()
        self.data[6] = self.ownername_box.get().strip()
        self.data[7] = self.email_box.get().strip()
        self.data[8] = self.sshkey_box.get().strip()
        self.destroy()

    def cancel_pressed(self):
        # print("cancel")
        self.data[0] = ''
        self.destroy()


    def buttonbox(self):
        self.ok_button = tk.Button(self, text='OK', width=5, command=self.ok_pressed)
        self.ok_button.pack(side="left")
        cancel_button = tk.Button(self, text='Cancel', width=5, command=self.cancel_pressed)
        cancel_button.pack(side="right")
        self.bind("<Return>", lambda event: self.ok_pressed())
        self.bind("<Escape>", lambda event: self.cancel_pressed())


class statOwnerDialog(simpledialog.Dialog):
    def __init__(self, parent, statfile):
        self.statfile = statfile
        self.parent = parent
        super().__init__(parent, 'Owner Info')    
    
    def body(self, frame):
        columns = ('#1','#2','#3','#4')
        print(columns)
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading('#1', text='camid')
        tree.heading('#2', text='site')
        tree.heading('#3', text='humanName')
        tree.heading('#4', text='email')
        contacts = []
        with open(os.path.join('caminfo', self.statfile),'r') as inf:
            _ = inf.readline() # skip header
            lis=inf.readlines()
            for li in lis:
                spls = li.split(',')
                contacts.append((spls[0], spls[1], spls[2], spls[3]))
        for contact in contacts:
            tree.insert('', tk.END, values=contact)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        return 


class demo(Frame):

    def __init__(self, parent):
        self.parent = parent
        Frame.__init__(self, parent)

        s3 = boto3.client('s3')
        self.bucket_name = 'ukmon-shared'

        self.camfile = 'camera-details.csv'
        self.fullname = 'consolidated/{}'.format(self.camfile)
        self.localfile = os.path.join('caminfo', self.camfile)
        self.statfile='stationdetails.csv'
        self.fullstat = 'admin/'+self.statfile
        self.locstatfile = os.path.join('caminfo', self.statfile)
        try: 
            s3.download_file(Bucket=self.bucket_name, Key=self.fullname, Filename=self.localfile)
            s3.download_file(Bucket=self.bucket_name, Key=self.fullstat, Filename=self.locstatfile)
            pass
        except:
            print('unable to get data files, using last good files')

        self.caminfo = pandas.read_csv('caminfo/camera-details.csv')
        self.caminfo = self.caminfo.sort_values(by=['active','camtype','camid'],ascending=[True,False,True])
        self.data = self.caminfo.values.tolist()
        self.hdrs = self.caminfo.columns.tolist()
        self.datachanged = False
     
        #self.parent = tk.Tk.__init__(self)
        self.parent.title('Station Maintenance')

        # Make menu
        self.menuBar = Menu(self.parent)
        self.parent.config(menu=self.menuBar)

        # File menu
        fileMenu = Menu(self.menuBar, tearoff=0)
        fileMenu.add_command(label="Exit", command=self.on_closing)

        camMenu = Menu(self.menuBar, tearoff=0)
        camMenu.add_command(label = "Add Camera", command = self.addCamera)
        camMenu.add_command(label = "Relocate Camera", command = self.moveCamera)
        camMenu.add_command(label = "Remove Camera", command = self.delCamera)
        camMenu.add_separator()
        camMenu.add_command(label = "Remove Location", command = self.delOperator)

        ownMenu = Menu(self.menuBar, tearoff=0)
        ownMenu.add_command(label = "View Owner Data", command = self.viewOwnerData)

        self.menuBar.add_cascade(label="File", underline=0, menu=fileMenu)
        self.menuBar.add_cascade(label="Camera", underline=0, menu=camMenu)
        self.menuBar.add_cascade(label="Owners", underline=0, menu=ownMenu)

        parent.grid_columnconfigure(0, weight = 1)
        parent.grid_rowconfigure(0, weight = 1)
        self.frame = tk.Frame(self)

        self.frame.grid_columnconfigure(0, weight = 1)
        self.frame.grid_rowconfigure(0, weight = 1)
        self.sheet = Sheet(self.parent,
            page_up_down_select_row = True,
            expand_sheet_if_paste_too_big = True,
            #empty_vertical = 0,
            column_width = 120,
            startup_select = (0,1,"rows"),
            #row_height = "4",
            #default_row_index = "numbers",
            #default_header = "both",
            #empty_horizontal = 0,
            #show_vertical_grid = False,
            #show_horizontal_grid = False,
            #auto_resize_default_row_index = False,
            #header_height = "3",
            #row_index_width = 100,
            #align = "e",
            #header_align = "w",
            #row_index_align = "w",
            data = self.data, # [[f"Row {r}, Column {c}\nnewline1\nnewline2" for c in range(50)] for r in range(500)], #to set sheet data at startup
            headers = self.hdrs, # [h for h in self.hdrs.split(',')],
            #row_index = [f"Row {r}\nnewline1\nnewline2" for r in range(2000)],
            #set_all_heights_and_widths = True, #to fit all cell sizes to text at start up
            #headers = 0, #to set headers as first row at startup
            #headers = [f"Column {c}\nnewline1\nnewline2" for c in range(30)],
            #theme = "light green",
            #row_index = 0, #to set row_index as first column at startup
            #total_rows = 5, #if you want to set empty sheet dimensions at startup
            #total_columns = 5, #if you want to set empty sheet dimensions at startup
            height = 500, #height and width arguments are optional
            width = 1200) #For full startup arguments see DOCUMENTATION.md

        #self.sheet.hide("row_index")
        #self.sheet.hide("header")
        #self.sheet.hide("top_left")
        self.sheet.enable_bindings(("single_select", #"single_select" or "toggle_select"
                                         "drag_select",   #enables shift click selection as well
                                    "select_all",
                                         #"column_drag_and_drop",
                                         #"row_drag_and_drop",
                                         #"column_select",
                                         #"row_select",
                                         "column_width_resize",
                                         "double_click_column_resize",
                                         "row_width_resize",
                                         "column_height_resize",
                                         "arrowkeys",
                                         "row_height_resize",
                                         "double_click_row_resize",
                                         "right_click_popup_menu",
                                         #"rc_select",
                                         #"rc_insert_column",
                                         #"rc_delete_column",
                                         #"rc_insert_row",
                                         "rc_delete_row",
                                         "copy",
                                         "cut",
                                         "paste",
                                         "delete",
                                         "undo",
                                         "edit_cell"
                                    ))
        #self.sheet.disable_bindings() #uses the same strings
        #self.sheet.enable_bindings()

        self.frame.grid(row = 1, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")
        
        """_________________________ EXAMPLES _________________________ """
        """_____________________________________________________________"""

        # __________ CHANGING THEME __________

        
        self.sheet.change_theme("light green")

        # __________ DISPLAY SUBSET OF COLUMNS __________

        #self.sheet.display_subset_of_columns(indexes = [0, 1, 2, 3, 4, 5], enable = True)
        #self.sheet.display_columns(enable = False)
        #self.sheet.insert_column(idx = 2)
        #self.sheet.insert_columns(columns = 5, idx = 10, mod_column_positions = False)

        # __________ HIGHLIGHT / DEHIGHLIGHT CELLS __________
        
        #self.sheet.highlight_cells(row = 5, column = 5, fg = "red")
        #self.sheet.highlight_cells(row = 5, column = 1, fg = "red")
        #self.sheet.highlight_cells(row = 5, bg = "#ed4337", fg = "white", canvas = "row_index")
        #self.sheet.highlight_cells(column = 0, bg = "#ed4337", fg = "white", canvas = "header")
        
        #self.sheet.highlight_columns([7, 8, 9], bg = "light blue", fg = "purple")
        #self.sheet.insert_columns(columns = [[1, 2, 3], [4, 5, 6], [7, 8, 9]], idx = 8)
        #self.sheet.delete_column(idx = 2)
        #self.sheet.highlight_rows([7, 8, 9], bg = "light blue", fg = "purple")
        #self.sheet.insert_rows(rows = 5, idx = 8)
        #self.sheet.insert_row(idx = 10, values = ["hi"])
        #self.sheet.move_row(7, 0)
        #self.sheet.move_column(6, 0)
        #self.sheet.delete_row(idx = 2)
        #self.sheet.dehighlight_rows(8)
        
        #self.sheet.highlight_columns(4, fg = "yellow")

        # __________ CELL / ROW / COLUMN ALIGNMENTS __________

        #self.sheet.align_cells(row = 1, column = 1, align = "e")
        #self.sheet.align_rows(rows = 3, align = "e", align_index = True)
        #self.sheet.align_columns(columns = 4, align = "e", align_header = True)
        #self.sheet.align_index(rows = 1, align = "e")
        #self.sheet.align_header(columns = 4, align = "e")
        #self.sheet.align_index(rows = 1) # reset row index 1 to global alignment

        # __________ DATA AND DISPLAY DIMENSIONS __________

        #self.sheet.total_rows(4) #will delete rows if set to less than current data rows
        #self.sheet.total_columns(2) #will delete columns if set to less than current data columns
        #self.sheet.sheet_data_dimensions(total_rows = 4, total_columns = 2)
        #self.sheet.sheet_display_dimensions(total_rows = 4, total_columns = 6) #currently resets widths and heights
        #self.sheet.set_sheet_data_and_display_dimensions(total_rows = 4, total_columns = 2) #currently resets widths and heights

        # __________ SETTING OR RESETTING TABLE DATA __________

        #.set_sheet_data() function returns the object you use as argument
        #verify checks if your data is a list of lists, raises error if not
        #self.data = self.sheet.set_sheet_data([[f"Row {r} Column {c}" for c in range(30)] for r in range(2000)], verify = False)

        # __________ SETTING ROW HEIGHTS AND COLUMN WIDTHS __________

        #self.sheet.set_cell_data(0, 0, "\n".join([f"Line {x}" for x in range(500)]))
        #self.sheet.set_column_data(1, ("" for i in range(2000)))
        #self.sheet.row_index((f"Row {r}" for r in range(2000))) #any iterable works
        #self.sheet.row_index("\n".join([f"Line {x}" for x in range(500)]), 2)
        #self.sheet.column_width(column = 0, width = 300)
        #self.sheet.row_height(row = 0, height = 60)
        #self.sheet.set_column_widths([120 for c in range(30)])
        #self.sheet.set_row_heights([30 for r in range(2000)])
        self.sheet.set_all_column_widths()
        #self.sheet.set_all_row_heights()
        #self.sheet.set_all_cell_sizes_to_text()
        
        # __________ BINDING A FUNCTIONS TO USER ACTIONS __________

        #self.sheet.extra_bindings([("cell_select", self.cell_select),
        #                            ("begin_edit_cell", self.begin_edit_cell),
        #                           ("end_edit_cell", self.end_edit_cell),
        #                            ("shift_cell_select", self.shift_select_cells),
        #                            ("drag_select_cells", self.drag_select_cells),
        #                            ("ctrl_a", self.ctrl_a),
        #                            ("row_select", self.row_select),
        #                            ("shift_row_select", self.shift_select_rows),
        #                            ("drag_select_rows", self.drag_select_rows),
        #                            ("column_select", self.column_select)
        #                            ("shift_column_select", self.shift_select_columns),
        #                            ("drag_select_columns", self.drag_select_columns),
        #                            ("deselect", self.deselect)
        #                            ])
        #self.sheet.extra_bindings("bind_all", self.all_extra_bindings)
        self.sheet.extra_bindings("begin_edit_cell", self.begin_edit_cell)
        self.sheet.extra_bindings("end_edit_cell", self.end_edit_cell)
        self.sheet.extra_bindings("end_delete_rows", self.end_delete_rows)
        self.sheet.extra_bindings("column_select", self.column_select)
        self.sheet.extra_bindings([("all_select_events", self.all_extra_bindings)])

        #self.sheet.extra_bindings("unbind_all") #remove all functions set by extra_bindings()

        # __________ BINDING NEW RIGHT CLICK FUNCTION __________
    
        #self.sheet.bind("<3>", self.rc)

        # __________ SETTING HEADERS __________

        #self.sheet.headers((f"Header {c}" for c in range(30))) #any iterable works
        #self.sheet.headers("Change header example", 2)
        #print (self.sheet.headers())
        #print (self.sheet.headers(index = 2))

        # __________ SETTING ROW INDEX __________

        #self.sheet.row_index((f"Row {r}" for r in range(2000))) #any iterable works
        #self.sheet.row_index("Change index example", 2)
        #print (self.sheet.row_index())
        #print (self.sheet.row_index(index = 2))

        # __________ INSERTING A ROW __________

        #self.sheet.insert_row(values = (f"my new row here {c}" for c in range(30)), idx = 0) # a filled row at the start
        #self.sheet.insert_row() # an empty row at the end

        # __________ INSERTING A COLUMN __________

        #self.sheet.insert_column(values = (f"my new col here {r}" for r in range(2050)), idx = 0) # a filled column at the start
        #self.sheet.insert_column() # an empty column at the end

        # __________ DELETING A ROW __________

        #self.sheet.delete_row() # first row

        # __________ SETTING A COLUMNS DATA __________

        # any iterable works
        #self.sheet.set_column_data(0, values = (0 for i in range(2050)))

        # __________ SETTING A ROWS DATA __________

        # any iterable works
        #self.sheet.set_row_data(0, values = (0 for i in range(35)))

        # __________ SETTING A CELLS DATA __________

        #self.sheet.set_cell_data(1, 2, "NEW VALUE")

        # __________ GETTING FULL SHEET DATA __________

        #self.all_data = self.sheet.get_sheet_data()

        # __________ GETTING CELL DATA __________

        #print (self.sheet.get_cell_data(0, 0))

        # __________ GETTING ROW DATA __________

        #print (self.sheet.get_row_data(0)) # only accessible by index

        # __________ GETTING COLUMN DATA __________

        #print (self.sheet.get_column_data(0)) # only accessible by index

        # __________ GETTING SELECTED __________

        #print (self.sheet.get_currently_selected())
        #print (self.sheet.get_selected_cells())
        #print (self.sheet.get_selected_rows())
        #print (self.sheet.get_selected_columns())
        #print (self.sheet.get_selection_boxes())
        #print (self.sheet.get_selection_boxes_with_types())

        # __________ SETTING SELECTED __________

        #self.sheet.deselect("all")
        #self.sheet.create_selection_box(0, 0, 2, 2, type_ = "cells") #type here is "cells", "cols" or "rows"
        #self.sheet.set_currently_selected(0, 0)
        #self.sheet.set_currently_selected("row", 0)
        #self.sheet.set_currently_selected("column", 0)

        # __________ CHECKING SELECTED __________

        #print (self.sheet.cell_selected(0, 0))
        #print (self.sheet.row_selected(0))
        #print (self.sheet.column_selected(0))
        #print (self.sheet.anything_selected())
        #print (self.sheet.all_selected())

        # __________ HIDING THE ROW INDEX AND HEADERS __________

        #self.sheet.hide("row_index")
        #self.sheet.hide("top_left")
        #self.sheet.hide("header")

        # __________ ADDITIONAL BINDINGS __________

        #self.sheet.bind("<Motion>", self.mouse_motion)

        # __________ ADDITIONAL BINDINGS __________

        #self.sheet.popup_menu_add_command("Hide columns", self.hide_columns_right_click, table_menu = False, index_menu = False)
        self.sheet.popup_menu_add_command('Sort', self.columns_sort, table_menu = False, index_menu = False)

    def hide_columns_right_click(self, event = None):
        currently_displayed = self.sheet.display_columns()
        exclude = set(currently_displayed[c] for c in self.sheet.get_selected_columns())
        indexes = [c for c in currently_displayed if c not in exclude]
        self.sheet.display_columns(indexes = indexes, enable = True, refresh = True)

    def all_extra_bindings(self, event):
        #print(event)
        pass

    def begin_edit_cell(self, event):
        self.oldval = self.data[event[0]][event[1]]
        # print(event)   # event[2] is keystroke
        #return event[2] # return value is the text to be put into cell edit window
        return self.oldval

    def end_edit_cell(self, event):
        self.newval = self.data[event[0]][event[1]]
        if self.newval != self.oldval and self.datachanged is False: 
            self.datachanged = True
        # print(event, self.data[event[0]][event[1]], self.datachanged)

    def end_delete_rows(self, event):
        self.datachanged = True

    def window_resized(self, event):
        pass
        #print(event)

    def mouse_motion(self, event):
        #region = self.sheet.identify_region(event)
        #row = self.sheet.identify_row(event, allow_end = False)
        #column = self.sheet.identify_column(event, allow_end = False)
        # print(region, row, column)
        pass

    def deselect(self, event):
        print(event, self.sheet.get_selected_cells())

    def rc(self, event):
        print(event)
        
    def cell_select(self, response):
        #print(response)
        pass

    def shift_select_cells(self, response):
        #print(response)
        pass

    def drag_select_cells(self, response):
        #print (response)
        pass

    def ctrl_a(self, response):
        #print(response)
        pass

    def row_select(self, response):
        #print(response)
        pass

    def shift_select_rows(self, response):
        print(response)

    def drag_select_rows(self, response):
        pass
        #print(response)

    def columns_sort(self):
        col = self.sheet.get_selected_columns()
        print(col)
        pass
        
    def column_select(self, response):
        #print(response)
        #for i in range(50):
        #    self.sheet.create_dropdown(i, response[1], values=[f"{i}" for i in range(200)], set_value="100",
        #                               destroy_on_select = False, destroy_on_leave = False, see = False)
        #print(self.sheet.get_cell_data(0, 0))
        #self.sheet.refresh()
        pass

    def shift_select_columns(self, response):
        #print(response)
        pass 

    def drag_select_columns(self, response):
        #print(response)
        pass
    
    def doSaveChanges(self):
        bkpfile = '{}.{}'.format(self.camfile, datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        shutil.copy(self.localfile, os.path.join('caminfo', bkpfile))

        newdf = pandas.DataFrame(self.data, columns=self.hdrs)
        newdf = newdf.sort_values(by=['active','camtype','camid'],ascending=[True,False,True])
        newdf.to_csv(self.localfile, index=False)

        s3 = boto3.client('s3')
        s3.upload_file(Bucket=self.bucket_name, Key=self.fullname, Filename=self.localfile)
        s3.upload_file(Bucket=self.bucket_name, Key=self.fullstat, Filename=self.locstatfile)

        return 

    def on_closing(self):
        if self.datachanged is True:
            if messagebox.askyesno("Quit", "Do you want to save changes?"):
                self.doSaveChanges()
        self.destroy()
        self.parent.quit()
        self.parent.destroy()

    def delCamera(self):
        # TODO : when active marked zero, find and deactivate corresponding row in stationdetails. 
        #        needs an active flag in that file
        tk.messagebox.showinfo(title="Information", message='To remove a camera, set Active=current date yyyymmdd')
        return

    def delOperator(self):
        tk.messagebox.showinfo(title="Information", message='Not implemented yet')
        return

    def viewOwnerData(self):
        statOwnerDialog(self, self.statfile)
        return

    def moveCamera(self):
        self.addCopyCamera(move=True)
        return

    def addCamera(self):
        self.addCopyCamera(move=False)
        return 

    def addCopyCamera(self, move=False):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        user,email = self.getUserDetails(curdata[1])
        if move is True:
            sshkey = self.getSSHkey(curdata[0], curdata[3])
            id = curdata[1]
            title = 'Move Camera'
            oldloc = curdata[0].lower() + '_' + curdata[3].lower()
        else:
            sshkey = ''
            id = ''
            title = 'Add Camera'
            oldloc = ''
        answer = infoDialog(self, title,curdata[0],curdata[9],curdata[8],curdata[10], 
            user, email, sshkey, id)
        if answer.data[0].strip() != '': 
            d = answer.data
            cameraname = d[4].lower() + '_' + d[5].lower()
            with open(os.path.join('sshkeys', cameraname + '.pub'), 'w') as outf:
                outf.write(d[8])
            rowdata=[d[4],d[0],d[0],d[5],'IMX291','Computar_4mm','1280','720',d[2],d[1],d[3],'2',d[0],'1']
            self.sheet.insert_row(values=rowdata, idx=0)
            self.addNewAwsUser(d[4])
            self.addNewUnixUser(d[4], d[5], oldloc)
            self.addNewOwner(d[0],d[4],d[6],d[7])
            self.datachanged = True
        return 
    
    def addNewOwner(self, rmsid, location, user, email):
        caminfo = pandas.read_csv(self.locstatfile)
        newdata = {'camid': [rmsid], 'site': [location], 'humanName':[user], 'eMail': [email]}
        newdf = pandas.DataFrame(newdata)
        caminfo = caminfo.append(newdf).sort_values(by=['camid'])
        caminfo.to_csv(self.locstatfile, index=False)

        ct.addRow(rmsid, location)

        return

    def addNewAwsUser(self, location):
        acct = '822069317839'  # empireelments account
        policyarn = 'arn:aws:iam::' + acct + ':policy/UkmonLive'
        group = 'ukmon'
        keyf = 'jsonkeys/' + location + '.key'
        userdets = 'users/' + location + '.txt'
        os.makedirs('jsonkeys', exist_ok=True)
        os.makedirs('csvkeys', exist_ok=True)
        os.makedirs('users', exist_ok=True)
        os.makedirs('inifs', exist_ok=True)
        iamc = boto3.client('iam')
        try: 
            _ = iamc.get_user(UserName=location)
            print('location exists, not adding it')
        except Exception:
            print('new location')
            usr = iamc.create_user(UserName=location)
            with open(userdets, 'w') as outf:
                outf.write(str(usr))
            key = iamc.create_access_key(UserName=location)
            with open(keyf, 'w') as outf:
                outf.write(json.dumps(key, indent=4, sort_keys=True, default=str))
            with open(os.path.join('csvkeys', location + '.csv'),'w') as outf:
                outf.write('Access key ID,Secret access key\n')
                outf.write('{},{}\n'.format(key['AccessKey']['AccessKeyId'], key['AccessKey']['SecretAccessKey']))
            _ = iamc.attach_user_policy(UserName=location, PolicyArn=policyarn)
            _ = iamc.add_user_to_group(UserName=location, GroupName=group)
        return 


    def addNewUnixUser(self, location, direction, oldcamname=''):
        server='ukmonhelper'
        user='ec2-user'
        cameraname = location.lower() + '_' + direction.lower()
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/ukmonhelper'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        scpcli.put(os.path.join('jsonkeys', location + '.key'), 'keymgmt/rawkeys/live/')
        scpcli.put(os.path.join('sshkeys', cameraname + '.pub'), 'keymgmt/sshkeys/')
        command = f'/home/{user}/keymgmt/addSftpUser.sh {cameraname} {location} {oldcamname}'
        stdin, stdout, stderr = c.exec_command(command)

        infname = os.path.join('keymgmt/inifs/',cameraname + '.ini')
        outfname = os.path.join('./inifs', cameraname + '.ini')
        while os.path.isfile(outfname) is False:
            try:
                time.sleep(3)
                scpcli.get(infname, outfname)
            except Exception:
                continue
        return

    def getSSHkey(self, loc, dir):
        server='ukmonhelper'
        user='ec2-user'
        tmpdir=os.getenv('TEMP', default='c:/temp')
        cameraname = (loc + '_' + dir).lower()
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/ukmonhelper'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        tmpfil = os.path.join(tmpdir,'./tmp.txt')
        # dont use os.path.join - source is on unix we are on windows!
        scpcli.get(f'keymgmt/sshkeys/{cameraname}.pub', tmpfil)

        with open(tmpfil, 'r') as inf:
            lis = inf.readlines()
        #os.remove('./tmp.txt')
        return lis[0].strip()

    def getUserDetails(self, camid):
        with open(os.path.join('caminfo', self.statfile),'r') as inf:
            lis = inf.readlines()
        print(camid)
        for li in lis:
            if li[:6] == camid:
                spls = li.split(',')
                print(li)
                return spls[2],spls[3]
        return '',''


if __name__ == '__main__':
    # Initialize main window
    root = tk.Tk()
    app = demo(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
