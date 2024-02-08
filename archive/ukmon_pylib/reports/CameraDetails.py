# Create a data type for the camera location details
# Copyright (C) 2018-2023 Mark McIntyre
import os
import numpy as np
import glob 
import json
import pandas as pd 
import boto3


# defines the data content of a UFOAnalyser CSV file
CameraDetails = np.dtype([('Site', 'S32'), ('CamID', 'S32'), ('LID', 'S16'),
    ('SID', 'S8'), ('camtyp', 'i4'), ('dummycode','S6'),('active','i4')])


class SiteInfo:
    """
    Class to read and manage camera site information

    Note that this class 
    """
    def __init__(self, fname=None):
        if fname is None:
            datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
            fname = os.path.join(datadir, 'consolidated', 'camera-details.csv')
        self.camdets = pd.read_csv(fname)

    def getCameraOffset(self, statid, activeonly=True):
        cam = self.camdets[self.camdets.camid == statid.upper()]
        if activeonly is True:
            cam = cam[cam.active == 1]
        if len(cam) == 0:
            # cant find a match
            return None
        else:
            return cam

    def GetSiteLocation(self, camname, activeonly=True):
        c = self.getCameraOffset(camname, activeonly)
        if c is None:
            return 'unknown'
        site = c.iloc[0].site
        camid = c.iloc[0].camid
        if camid is None:
            return site
        else:
            return site + '/' + camid

    def getDummyCode(self, lid, sid):
        df = self.camdets[self.camdets.lid == lid.upper()]
        cam = df[df.sid == sid.upper()]
        if len(cam) == 0:
            return 'Unknown'
        else:
            return cam.iloc[0].dummycode

    def getFolder(self, statid):
        cam = self.getCameraOffset(statid)
        if cam is None:
            return 'Unknown'
        else:
            return cam.iloc[0].site + '/' + cam.iloc[0].camid

    def checkCameraActive(self, statid):
        cam = self.getCameraOffset(statid)
        if cam is None:
            return False
        else:
            if cam.iloc[0].active != 1: 
                return False
            return True

    def getActiveCameras(self):
        return self.camdets[self.camdets.active==1]

    def getCameraType(self, statid):
        cam = self.getCameraOffset(statid)
        if cam is None:
            return None
        else:
            return cam.iloc[0].camtype

    def getAllCamsAndFolders(self, isactive=False):
        # fetch camera details from the CSV file
        fldrs = []
        cams = []
        for _, row in self.camdets.iterrows():
            if isactive is True and row.active != 1: 
                continue
            if row.camid == '':
                fldrs.append(row.site)
            else:
                fldrs.append(row.site + '/' + row.camid)
            if row.camtype == 1:
                cams.append(row.lid + '_' + str(row.sid))
            else:
                cams.append(row.lid)
        return cams, fldrs

    def getAllCamsStr(self, onlyActive=False):
        cams, _ = self.getAllCamsAndFolders(isactive=onlyActive)
        cams.sort()
        return ','.join(cams)

    def getAllLocsStr(self, onlyActive=False):
        _, locs = self.getAllCamsAndFolders(isactive=onlyActive)
        locs.sort()
        return ','.join(locs)

    def getStationsAtSite(self, sitename, onlyactive=False):
        idlist = []
        fltred = self.camdets[self.camdets.site == sitename]
        if onlyactive is True:
            fltred = fltred[fltred.active==1]
        for _,rw in fltred.iterrows():
            if rw.camtype == 1:
                idlist.append(rw.lid + '_' + rw.sid)
            else:
                idlist.append(rw.lid)
        return idlist

    def getSites(self, onlyactive=True):
        sites=[]
        silist=self.camdets.site
        silist = np.unique(silist)
        sites = [si for si in silist]
        return sites

    def getUFOCameras(self, onlyactive=False):
        camlist=[]
        ufo=self.camdets[self.camdets.camtype==1]
        if onlyactive is True:
            ufo = ufo[ufo.active == 1]
        for _,rw in ufo.iterrows():
            ufoname = rw.lid + '_' + str(rw.sid)
            camlist.append({'Site':rw.site, 'CamID':rw.camid, 'dummycode':rw.dummycode, 'ufoid':ufoname})
        return camlist

    def getCameraLocAndDir(self, camid, activeonly=True):
        cam = self.getCameraOffset(camid, activeonly=activeonly)
        if cam is None:
            return ''
        else:
            return cam.iloc[0].site + '_' + cam.iloc[0].sid


'''
creating and managing the more-accurate camera location info
'''


def getCamLocDirFov(camid, datadir=None):
    if datadir is None:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    camdb = json.load(open(os.path.join(datadir, 'admin', 'cameraLocs.json')))
    if camid not in camdb.keys():
        return False
    return camdb[camid]


def updateCamLocDirFovDB(datadir=None):
    if datadir is None:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    camdb = {}
    ppfiles = glob.glob(os.path.join(datadir, 'consolidated','platepars', '*.json'))
    for ppf in ppfiles:
        try:
            pp = json.load(open(ppf))
            camid = pp['station_code']
            camdb.update({camid: {'lat': pp['lat'], 'lon': pp['lon'], 'ele': pp['elev'],
                'az': pp['az_centre'], 'alt': pp['alt_centre'], 'fov_h': pp['fov_h'], 'fov_v': pp['fov_v'], 
                'rot': pp['rotation_from_horiz']}})
        except:
            # platepar was malformed
            continue
    with open(os.path.join(datadir, 'admin', 'cameraLocs.json'), 'w') as outf:
        json.dump(camdb, outf, indent=4)


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


def createCDCsv(targetloc):
    sess = boto3.Session(profile_name='ukmonshared')
    ddb = sess.resource('dynamodb', region_name='eu-west-2')
    camdets = loadLocationDetails(ddb=ddb)
    cd4csv = camdets[['site','stationid','oldcode','direction','camtype','active']]
    pd.options.mode.chained_assignment = None
    cd4csv['dummycode'] = camdets.stationid
    pd.options.mode.chained_assignment = 'warn'
    cd4csv = cd4csv[['site','stationid','oldcode','direction','camtype','dummycode','active']]
    cd4csv = cd4csv.rename(columns={'stationid':'camid', 'oldcode':'lid', 'direction':'sid'})
    cd4csv.sort_values(by=['active','camid'], inplace=True)
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    outfname = os.path.join(datadir, targetloc, 'camera-details.csv')
    cd4csv.to_csv(outfname, index=False)
    with open(os.path.join(datadir, 'activecamcount.txt'), 'w') as outf:
        outf.write(str(len(cd4csv[cd4csv.active==1])))
    createStatOptsHtml(camdets, datadir)
    createStatOptsHtml(camdets, datadir, True)
    createStatOptsHtml(camdets, datadir, True, True)
    return


def createStatOptsHtml(sitedets, datadir, active=False, locs=False):
    """
    Create an HTML file containing a list of stations or locations
    These files are used by the website search functions
    """
    if active:
        if locs:
            siteidx = os.path.join(datadir, 'activestatlocs.html')  
            sitedets = sitedets.sort_values(by=['site', 'stationid'])
        else:
            siteidx = os.path.join(datadir, 'activestatopts.html')  
        sitedets = sitedets[sitedets.active==1]
    else:
        siteidx = os.path.join(datadir, 'statopts.html')  
    with open(siteidx, 'w') as outf:
        if not active:
            outf.write('<label for="statselect">Station</label>\n')
            outf.write('<select class="bootstrap-select" id="statselect">\n')
        outf.write('<option value="1" selected="selected">All</option>\n')
        rowid = 2
        for _, rw in sitedets.iterrows():
            if locs:
                cam = f'{str(rw.site)}/{str(rw.stationid)}'
            else:
                cam = str(rw.stationid)
            outf.write(f'<option value="{rowid}">{cam}</option>\n')
            rowid += 1
        if not active:
            outf.write('</select>\n')
    return 


def findSite(stationid, camdets=None, ddb=None):
    if camdets is None:
        camdets = loadLocationDetails(ddb=ddb) 
    cc = camdets[camdets.stationid==stationid]
    if len(cc) > 0:
        res = cc.iloc[0]['site']
    else:
        res = 'Unknown'
    return res


def findEmail(stationid, camdets=None, ddb=None):
    if camdets is None:
        camdets = loadLocationDetails(ddb=ddb) 
    cc = camdets[camdets.stationid==stationid]
    if len(cc) > 0:
        res = cc.iloc[0]['eMail']
    else:
        res = 'Unknown'
    return res
