# Copyright (C) 2018-2023 Mark McIntyre

from tksheet import Sheet
import tkinter as tk
from tkinter import ttk
from tkinter import Frame, Menu
from tkinter import simpledialog
import tkinter.messagebox as tkMessageBox
from tkinter.filedialog import askopenfilename
import boto3
import os
import paramiko
import json 
import time
import datetime
from scp import SCPClient
from boto3.dynamodb.conditions import Key
import pandas as pd
from configparser import ConfigParser


def loadConfig(cfgdir):
    cfgfile = os.path.join(cfgdir, 'stationmaint.cfg')
    cfg = ConfigParser()
    if not os.path.isfile(cfgfile):
        tkMessageBox.showinfo('Warning', f'config file {cfgfile} not found')
        exit(0)
    cfg.read(cfgfile)
    return cfg


def addRow(newdata=None, stationid=None, site=None, user=None, email=None, ddb=None, 
           direction=None, camtype=None, active=None, createdate=None, tblname='camdetails'):
    '''
    add a row to the CamTimings table
    '''
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    if not newdata:
        newdata = {'stationid': stationid, 'site': site, 'humanName':user, 'eMail': email, 
                   'direction': direction, 'camtype': camtype, 'active': active, 'created': createdate,
                   'oldcode': stationid}
    table = ddb.Table(tblname)
    response = table.put_item(Item=newdata)
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        print(response)
    return 


def loadLocationDetails(table='camdetails', ddb=None, loadall=False):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table(table)
    res = table.scan()
    # strictly, should check for LastEvaluatedKey here, in case there was more than 1MB of data,
    # however that equates to around 30,000 users which i hope we never have... 
    values = res.get('Items', [])
    camdets = pd.DataFrame(values)
    camdets.sort_values(by=['stationid'], inplace=True)
    if not loadall:
        camdets.dropna(inplace=True, subset=['eMail','humanName','site'])
    camdets['camtype'] = camdets['camtype'].astype(int)
    camdets['active'] = camdets['active'].astype(int)
    return camdets


def findLocationInfo(srchstring, ddb=None, statdets=None):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    s1 = statdets[statdets.stationid.str.contains(srchstring)]
    s2 = statdets[statdets.eMail.str.contains(srchstring)]
    s3 = statdets[statdets.humanName.str.contains(srchstring)]
    s4 = statdets[statdets.site.str.contains(srchstring)]
    srchres = pd.concat([s1, s2, s3, s4])
    srchres.drop(columns=['oldcode','active','camtype'], inplace=True)
    return srchres


def cameraExists(stationid=None, location=None, direction=None, ddb=None, statdets=None):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    if stationid:
        if len(statdets[statdets.stationid == stationid]) > 0:
            return True
    if location and direction:
        s1 = statdets[statdets.site == location]
        if len(s1) > 0:
            if len(s1[s1.direction == direction]) > 0:
                return True
    return False


def dumpCamTable(outdir, statdets=None, ddb=None, exportmindets=False):
    if statdets is None:
        statdets = loadLocationDetails(ddb=ddb) 
        statdets = statdets[statdets.active==1]
    if exportmindets:
        statdets = statdets[['stationid', 'eMail']]
    statdets.to_csv(os.path.join(outdir,'camtable.csv'), index=False)


def getCamUpdateDate(camid, ddb=None):
    if not ddb:
        ddb = boto3.resource('dynamodb', region_name='eu-west-2')
    table = ddb.Table('LiveBrightness')
    resp = table.query(KeyConditionExpression=Key('camid').eq(camid),
                       IndexName = 'camid-CaptureNight-index',
                       ScanIndexForward=False,
                       Limit=1,
                       Select='SPECIFIC_ATTRIBUTES',
                       ProjectionExpression='CaptureNight')
    if len(resp['Items']) > 0:
        return int(resp['Items'][0]['CaptureNight'])
    else:
        return 0


class srcResBox(tk.Toplevel):
    '''
    A class for the search dialog
    '''
    def __init__(self, title, message):
        tk.Toplevel.__init__(self)
        self.details_expanded = False
        self.title(title)
        self.geometry('600x250')
        self.minsize(700, 250)
        self.maxsize(700, 550)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky='nsew')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        text_frame = tk.Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(7, 7), sticky='nsew')
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.textbox = tk.Text(text_frame, height=6)
        self.textbox.insert('1.0', message)
        self.textbox.grid(row=0, column=0, sticky='nsew')
        self.geometry('700x550')
        self.details_expanded = True


class infoDialog(simpledialog.Dialog):
    '''
    A class to gather or display info on a camera
    '''
    def __init__(self, parent, title, location, user, email, sshkey='', id=''):
        self.data = []
        self.data.append(id)
        self.data.append(location)
        self.data.append('')
        self.data.append(user)
        self.data.append(email)
        self.data.append(sshkey)
        self.parent = parent

        super().__init__(parent, title)    

    def body(self, frame):
        self.camid_label = tk.Label(frame, width=25, text="RMS ID")
        self.camid_label.pack()
        self.camid_box = tk.Entry(frame, width=25)
        self.camid_box.insert(tk.END, self.data[0])
        self.camid_box.pack()

        self.location_label = tk.Label(frame, width=25, text="Location")
        self.location_label.pack()
        self.location_box = tk.Entry(frame, width=25)
        self.location_box.insert(tk.END, self.data[1])
        self.location_box.pack()

        self.direction_label = tk.Label(frame, width=25, text="direction")
        self.direction_label.pack()
        self.direction_box = tk.Entry(frame, width=25)
        self.direction_box.pack()

        self.ownername_label = tk.Label(frame, width=25, text="owner name")
        self.ownername_label.pack()
        self.ownername_box = tk.Entry(frame, width=25)
        self.ownername_box.insert(tk.END, self.data[3])
        self.ownername_box.pack()

        self.email_label = tk.Label(frame, width=25, text="email address")
        self.email_label.pack()
        self.email_box = tk.Entry(frame, width=25)
        self.email_box.insert(tk.END, self.data[4])
        self.email_box.pack()

        self.sshkey_label = tk.Label(frame, width=25, text="SSH key")
        self.sshkey_label.pack()
        self.sshkey_box = tk.Entry(frame, width=50)
        self.sshkey_box.insert(tk.END, self.data[5])
        self.sshkey_box.pack()

    def ok_pressed(self):
        self.data[0] = self.camid_box.get().strip()
        self.data[1] = self.location_box.get().strip().capitalize()
        self.data[2] = self.direction_box.get().strip().upper()
        self.data[3] = self.ownername_box.get().strip()
        self.data[4] = self.email_box.get().strip()
        self.data[5] = self.sshkey_box.get().strip()
        if cameraExists(location=self.data[1],direction=self.data[2], statdets=self.parent.stationdetails):
            msg = f'{self.data[1]}_{self.data[2]} already exists'
            tk.messagebox.showinfo(title="Information", message=msg)
        else:
            self.destroy()

    def cancel_pressed(self):
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
    '''
    A class to display station ownership data
    '''
    def __init__(self, parent):
        self.stationdetails = parent.stationdetails
        self.parent = parent
        super().__init__(parent, 'Owner Info')    
    
    def body(self, frame):
        columns = ('#1','#2','#3','#4')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading('#1', text='camid')
        tree.heading('#2', text='site')
        tree.heading('#3', text='email')
        tree.heading('#4', text='humanName')
        contacts = []
        for _, li in self.stationdetails.iterrows():
            contacts.append((li['stationid'], li['site'], li['eMail'], li['humanName']))
        for contact in contacts:
            tree.insert('', tk.END, values=contact)
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        return 


class CamMaintenance(Frame):
    '''
    The main camera maintenance window class
    '''
    def __init__(self, parent, cfgdir):
        self.parent = parent
        Frame.__init__(self, parent)

        self.cfg = loadConfig(cfgdir)

        self.archprof = self.cfg['store']['awsprofile'] 
        self.conn = boto3.Session(profile_name=self.archprof)
        self.bucket_name = self.cfg['store']['srcbucket'] 

        os.makedirs('jsonkeys', exist_ok=True)
        os.makedirs('csvkeys', exist_ok=True)
        os.makedirs('users', exist_ok=True)
        os.makedirs('inifs', exist_ok=True)
        os.makedirs('sshkeys', exist_ok=True)

        self.ddb = self.conn.resource('dynamodb', region_name='eu-west-2')
        try:
            self.stationdetails = loadLocationDetails(ddb=self.ddb)
        except Exception:
            print('unable to get operator details - probably wrong AWS profile')
            exit(1)
        tmpdf = self.stationdetails[['site','stationid','direction','camtype','active','humanName','eMail','oldcode','created']]
        tmpdf = tmpdf.sort_values(by=['active','site','stationid'], ascending=[True,True,True])
        self.data = tmpdf.values.tolist()
        self.hdrs = tmpdf.columns.tolist()
     
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
        camMenu.add_command(label = "Deactivate Camera", command = self.delCamera)
        camMenu.add_separator()
        camMenu.add_command(label = "Remove Location", command = self.delOperator)
        camMenu.add_separator()
        camMenu.add_command(label = "Download Platepar", command = self.getPlate)
        camMenu.add_command(label = "Update platepar", command = self.newPlate)
        camMenu.add_separator()
        camMenu.add_command(label = "Update SSH Key", command = self.newSSHKey)
        camMenu.add_command(label = "Update AWS Key", command = self.newAWSKey)
        camMenu.add_separator()
        camMenu.add_command(label = "Check Camera", command = self.checkLastUpdate)

        ownMenu = Menu(self.menuBar, tearoff=0)
        ownMenu.add_command(label = "View Owner Data", command = self.viewOwnerData)
        ownMenu.add_command(label = "Search Data", command = self.searchOwnerData)

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
            data = self.data, 
            headers = self.hdrs, 
            height = 700, 
            width = 700) 

        self.sheet.enable_bindings(("single_select", 
                                    "drag_select", 
                                    "select_all",
                                    "column_width_resize",
                                    "double_click_column_resize",
                                    "row_width_resize",
                                    "column_height_resize",
                                    "arrowkeys",
                                    "row_height_resize",
                                    "double_click_row_resize",
                                    "right_click_popup_menu",
                                    "rc_delete_row",
                                    "copy",
                                    "cut",
                                    "paste",
                                    "delete",
                                    "undo",
                                    "edit_cell"
                                    ))
        self.sheet.popup_menu_add_command("Sort by this Column", self.columns_sort)

        self.frame.grid(row = 1, column = 0, sticky = "nswe")
        self.sheet.grid(row = 0, column = 0, sticky = "nswe")
        
        self.sheet.change_theme("light green")

        self.sheet.set_all_column_widths()

        #self.sheet.extra_bindings("end_delete_rows", self.end_delete_rows)
        #self.sheet.extra_bindings("column_select", self.column_select)
        self.sheet.extra_bindings([("all_select_events", self.all_extra_bindings),
                                   ("begin_edit_cell", self.begin_edit_cell),
                                   ("end_edit_cell", self.end_edit_cell)])

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
        return self.oldval

    def end_edit_cell(self, event):
        #print(event)
        if event[3] != self.oldval: 
            data = self.data[event[0]]
            data[event[1]] = event[3]
            newdata = {'stationid': data[1], 'site': data[0], 'humanName':data[5], 'eMail': data[6], 
                    'direction': data[2], 'camtype': str(data[3]), 'active': int(data[4]), 'oldcode': data[1],
                    'created': data[8]}
            addRow(newdata, ddb=self.ddb)
        return event[3]
    
    def end_delete_rows(self, event):
        #print(event)
        pass

    def window_resized(self, event):
        #print(event)
        pass

    def mouse_motion(self, event):
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
        cursel = self.sheet.get_selected_cells()
        col = list(cursel)[0][1]
        print(self.hdrs[col])
        pass
        
    def column_select(self, response):
        pass

    def shift_select_columns(self, response):
        #print(response)
        pass 

    def drag_select_columns(self, response):
        #print(response)
        pass
    
    def on_closing(self):
        outdir = 'stationdetails'
        os.makedirs(outdir, exist_ok=True)
        dumpCamTable(outdir=outdir, statdets=self.stationdetails, exportmindets=False)
        self.destroy()
        self.parent.quit()
        self.parent.destroy()

    def delCamera(self):
        tk.messagebox.showinfo(title="Information", message='To remove a camera, set Active=current date yyyymmdd')
        return

    def delOperator(self):
        tk.messagebox.showinfo(title="Information", message='Not implemented yet')
        return
    
    def viewOwnerData(self):
        statOwnerDialog(self)
        return

    def searchOwnerData(self):
        srchstring = simpledialog.askstring("Some_Name", "Search String",parent=root) 
        srchres = findLocationInfo(srchstring, statdets=self.stationdetails)
        msgtext = ''
        for _, li in srchres.iterrows():
            msgtext = msgtext + f'{li.stationid:10s}{li.site:20s}{li.eMail:30s}{li.humanName:20s}\n'
        srcResBox(title="Results", message=msgtext)
        return

    def moveCamera(self):
        self.addCopyCamera(move=True)
        return
    
    def checkLastUpdate(self):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        camid = curdata[1]
        lastupd = getCamUpdateDate(camid, ddb=self.ddb)
        msg = f'{camid} last sent a live image on {lastupd}'
        tk.messagebox.showinfo(title="Information", message=msg)
        return 

    def addCamera(self):
        self.addCopyCamera(move=False)
        return 

    def addCopyCamera(self, move=False):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        user = curdata[5]
        email = curdata[6]
        if move is True:
            sshkey = self.getSSHkey(curdata[0], curdata[2])
            id = curdata[1]
            title = 'Move Camera'
            oldloc = curdata[0].lower() + '_' + curdata[2].lower()
            created = curdata[7]
        else:
            sshkey = ''
            id = ''
            title = 'Add Camera'
            oldloc = ''
            created = datetime.datetime.now().strftime('%Y%m%d')
        answer = infoDialog(self, title, curdata[0], user, email, sshkey, id)
        if answer.data[0].strip() != '': 
            d = answer.data
            rmsid = str(d[0]).upper()
            location = str(d[1]).capitalize()
            cameraname = d[1].lower() + '_' + d[2].lower()
            with open(os.path.join('sshkeys', cameraname + '.pub'), 'w') as outf:
                outf.write(d[5])
            rowdata=[d[1],d[0],d[2],'2','1',d[3],d[4],d[0]]
            self.sheet.insert_row(values=rowdata, idx=0)
            self.addNewAwsUser(location)
            self.createIniFile(cameraname)
            self.addNewUnixUser(location, cameraname, oldloc)
            self.addNewOwner(rmsid, location, str(d[3]), str(d[4]), str(d[2]), '2','1', created)
        return 

    def newSSHKey(self):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        user,email = self.getUserDetails(self.stationdetails, curdata[1])
        sshkey = ''
        id = ''
        title = 'Update SSH Key'
        answer = infoDialog(self, title, curdata[0], user, email, sshkey, id)
        if answer.data[0].strip() != '': 
            d = answer.data
            location = str(d[1]).capitalize()
            cameraname = d[1].lower() + '_' + d[2].lower()
            with open(os.path.join('sshkeys', cameraname + '.pub'), 'w') as outf:
                outf.write(d[5])
            self.addNewUnixUser(location, cameraname, updatemode=2)
            self.datachanged = True
        return 
    
    def getPlate(self):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        ppdir = self.cfg['helper']['platepardir'] 
        ppdir = os.path.join(ppdir, curdata[1])
        os.makedirs(ppdir, exist_ok=True)
        ppfile = 'platepar_cmn2010.cal'
        site = curdata[0].capitalize()
        camid = curdata[1].upper()

        server = self.cfg['helper']['helperip'] 
        user='ec2-user'
        keyfile = self.cfg['helper']['sshkey']
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        remotedir = self.cfg['helper']['remotedir'] 
        remotef=f'{remotedir}/consolidated/platepars/{camid}.json'
        localf = os.path.join(ppdir, ppfile)
        scpcli.get(remotef, localf)

        s3 = boto3.client('s3')
        res = s3.list_objects_v2(Bucket=self.bucket_name, Prefix=f'archive/{site}/{camid}/2023/202312/')
        if res['KeyCount'] > 0:
            keys=res['Contents']
            fitsfiles = [x['Key'] for x in keys if 'fits' in x['Key']]
            fitsfiles.sort()
            fitsfiles = fitsfiles[-10:]
            for ff in fitsfiles:
                _, ffname = os.path.split(ff)
                dlf = os.path.join(ppdir, ffname)
                s3.download_file(self.bucket_name, ff, dlf)
            cfgfiles = [x['Key'] for x in keys if '.config' in x['Key']]
            cfgfiles.sort()
            dlf = os.path.join(ppdir,'.config')
            s3.download_file(self.bucket_name, cfgfiles[-1], dlf)
        return 
    
    def newPlate(self):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        ppdir =self.cfg['helper']['platepardir'] 
        ppdir = os.path.join(ppdir, curdata[1])
        ppfile = 'platepar_cmn2010.cal'
        plate = ''
        title = 'Select New Platepar File'
        plate = askopenfilename(title=title, defaultextension='*.cal',initialdir=ppdir, initialfile=ppfile)
        if plate:
            self.uploadPlatepar(curdata, plate)
        print(plate)
        return 

    def newAWSKey(self):
        cursel = self.sheet.get_selected_cells()
        cr = list(cursel)[0][0]
        curdata = self.data[cr]
        location = curdata[0]
        self.createNewAwsKey(location, self.stationdetails)

    def uploadPlatepar(self, camdets, plateparfile):
        server = self.cfg['helper']['helperip'] 
        user='ec2-user'
        uplfile = f'/tmp/platepar_cmn2010_{camdets[1]}.cal'
        camname = f'{camdets[0]}_{camdets[3]}'.lower()
        keyfile = self.cfg['helper']['sshkey'] 
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        scpcli.put(plateparfile, uplfile)
        command = f'sudo mkdir -p /var/sftp/{camname}/platepar/ && sudo chown {camname}:{camname} /var/sftp/{camname}/platepar'
        print(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=10)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        command = f'sudo mv {uplfile} /var/sftp/{camname}/platepar/platepar_cmn2010.cal'
        print(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=10)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        command = f'sudo chown {camname}:{camname} /var/sftp/{camname}/platepar/platepar_cmn2010.cal'
        print(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=10)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        return
    
    def addNewOwner(self, rmsid, location, user, email, direction, camtype, active, created):
        print(f'adding new owner {user} with {email} for {rmsid} at {location}')
        newdata = {'stationid': rmsid, 'site': location, 'humanName':user, 'eMail': email, 
                   'direction': direction, 'camtype': camtype, 'active': int(active), 'oldcode': rmsid, 
                   'created': created}
        addRow(newdata=newdata, ddb=self.ddb)
        return

    def addNewAwsUser(self, location):
        print(f'adding new location {location} to AWS')
        archkeyf = 'jsonkeys/' + location + '_arch.key'
        archuserdets = 'users/' + location + '_arch.txt'
        archcsvf = os.path.join('csvkeys', location.lower() + '_arch.csv')
        os.makedirs('jsonkeys', exist_ok=True)
        os.makedirs('csvkeys', exist_ok=True)
        os.makedirs('users', exist_ok=True)

        iamc = self.conn.client('iam')
        try: 
            _ = iamc.get_user(UserName=location)
            print('location exists, not adding it')
            archkey = None
        except Exception:
            print('new location')
            usr = iamc.create_user(UserName=location)
            with open(archuserdets, 'w') as outf:
                outf.write(str(usr))
            archkey = iamc.create_access_key(UserName=location)
            with open(archkeyf, 'w') as outf:
                outf.write(json.dumps(archkey, indent=4, sort_keys=True, default=str))
            with open(archcsvf,'w') as outf:
                outf.write('Access key ID,Secret access key\n')
                outf.write('{},{}\n'.format(archkey['AccessKey']['AccessKeyId'], archkey['AccessKey']['SecretAccessKey']))
        _ = iamc.add_user_to_group(GroupName='cameras', UserName=location)
        if archkey is not None: 
            self.createKeyFile(location)
        return 

    def createNewAwsKey(self, location, caminfo):
        server = self.cfg['helper']['helperip'] 
        user='ec2-user'
        keyfile = self.cfg['helper']['sshkey'] 
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        command = f'/home/{user}/keymgmt/updateAwsKey.sh {location} force'
        print(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=10)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")
        print('done')
        c.close()
        return 


    def updateKeyfile(self, caminfo, location):
        server = self.cfg['helper']['platepardir']
        user='ec2-user'
        keyf = os.path.join('jsonkeys', location + '.key')
        currkey = json.load(open(keyf, 'r'))
        archcsvf = os.path.join('csvkeys', location.lower() + '_arch.csv')
        with open(archcsvf,'w') as outf:
            outf.write('Access key ID,Secret access key\n')
            outf.write('{},{}\n'.format(currkey['AccessKey']['AccessKeyId'], currkey['AccessKey']['SecretAccessKey']))

        affectedcamlist = caminfo[caminfo.site==location]
        keyfile = self.cfg['helper']['sshkey']
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        c.connect(hostname = server, username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        # push the raw keyfile
        scpcli.put(keyf, 'keymgmt/rawkeys/live/')
        scpcli.put(archcsvf, 'keymgmt/rawkeys/csvkeys/')
        scpcli.close()
        for _, cam in affectedcamlist.iterrows():
            cameraname = cam.site.lower() + '_' + cam.site.lower()
            keyfile = os.path.join('sshkeys', cameraname + '.pub')
            k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(keyfile))
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(hostname = server, username = cameraname, pkey = k)
            scpcli = SCPClient(c.get_transport())
            scpcli.put(archcsvf, '.')


    def getSSHkey(self, loc, dir):
        server= self.cfg['helper']['helperip'] 
        user='ec2-user'
        tmpdir=os.getenv('TEMP', default='c:/temp')
        cameraname = (loc + '_' + dir).lower()
        keyfile = self.cfg['helper']['sshkey']
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
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


    def getUserDetails(self, stationdetails, camid):
        reqdf = stationdetails[stationdetails.stationid == camid]
        if len(reqdf) == 0:
            return '',''
        return reqdf.eMail.iloc[0], reqdf.humanName.iloc[0]


    def addNewUnixUser(self, location, cameraname, oldcamname='', updatemode=0):
        server = self.cfg['helper']['helperip'] 
        user='ec2-user'
        print(f'adding new Unix user {cameraname}')
        keyfile = self.cfg['helper']['sshkey'] 
        k = paramiko.RSAKey.from_private_key_file(os.path.expanduser(f'~/.ssh/{keyfile}'))
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            c.connect(hostname = server, username = user, pkey = k)
        except Exception:
            c.connect(hostname = server+'.', username = user, pkey = k)
        scpcli = SCPClient(c.get_transport())
        scpcli.put(os.path.join('sshkeys', cameraname + '.pub'), 'keymgmt/sshkeys/')
        scpcli.put(os.path.join('keys', location.lower() + '.key'), 'keymgmt/keys/')
        scpcli.put(os.path.join('csvkeys', location.lower() + '_arch.csv'), 'keymgmt/csvkeys/')
        scpcli.put(os.path.join('inifs', cameraname + '.ini'), 'keymgmt/inifs/')
        command = f'/home/{user}/keymgmt/addSftpUser.sh {cameraname} {location} {updatemode} {oldcamname}'
        print(f'running {command}')
        _, stdout, stderr = c.exec_command(command, timeout=10)
        for line in iter(stdout.readline, ""):
            print(line, end="")
        for line in iter(stderr.readline, ""):
            print(line, end="")

        print('done, collecting output')
        infname = os.path.join('keymgmt/inifs/',cameraname + '.ini')
        outfname = os.path.join('./inifs', cameraname + '.ini')
        while os.path.isfile(outfname) is False:
            try:
                time.sleep(3)
                scpcli.get(infname, outfname)
            except Exception:
                continue
        return


    def createKeyFile(self, location):
        archbucket = self.cfg['store']['srcbucket'] 
        livebucket = self.cfg['store']['livebucket'] 
        webbucket = self.cfg['store']['websitebucket'] 

        os.makedirs('keys', exist_ok=True)
        outf = 'keys/' + location.lower() + '.key'
        with open(outf, 'w') as ouf:
            ouf.write('export AWS_DEFAULT_REGION=eu-west-1\n')
            ouf.write(f'export CAMLOC="{location}"\n')
            ouf.write(f'export S3FOLDER="archive/{location}/"\n')
            ouf.write(f'export ARCHBUCKET={archbucket}\n')
            ouf.write(f'export LIVEBUCKET={livebucket}\n')
            ouf.write(f'export WEBBUCKET={webbucket}\n')
            ouf.write('export ARCHREGION=eu-west-2\n')
            ouf.write('export LIVEREGION=eu-west-1\n')
            ouf.write('export MATCHDIR=matches/RMSCorrelate\n')
        return 


    def createIniFile(self, cameraname):
        helperip = self.cfg['helper']['helperip'] 
        os.makedirs('inifs', exist_ok=True)
        outf = 'inifs/' + cameraname + '.ini'
        with open(outf, 'w') as outf:
            outf.write('# config data for this station\n')
            outf.write(f'export LOCATION={cameraname}\n')
            outf.write(f'export UKMONHELPER={helperip}\n')
            outf.write('export UKMONKEY=~/.ssh/ukmon\n')
            outf.write('export RMSCFG=~/source/RMS/.config\n')
        return 


if __name__ == '__main__':
    # Initialize main window
    dir_ = os.getcwd() #os.path.dirname(os.path.realpath(__file__))
    root = tk.Tk()
    app = CamMaintenance(root, dir_)
    root.iconbitmap(os.path.join(dir_,'camera.ico'))
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
