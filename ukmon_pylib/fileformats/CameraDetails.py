# Create a data type for the camera location details
# Copyright (C) 2018-2023 Mark McIntyre
import sys
import os
import numpy as np
import glob 
import json


# defines the data content of a UFOAnalyser CSV file
CameraDetails = np.dtype([('Site', 'S32'), ('CamID', 'S32'), ('LID', 'S16'),
    ('SID', 'S8'), ('camtyp', 'i4'), ('dummycode','S6'),('active','i4')])


class SiteInfo:
    def __init__(self, fname=None):
        if fname is None:
            datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
            fname = os.path.join(datadir, 'consolidated', 'camera-details.csv')

        self.camdets = np.loadtxt(fname, delimiter=',', skiprows=1, dtype=CameraDetails)
        #print(self.camdets)

    def getCameraOffset(self, statid, activeonly=True):
        spls=statid.split('_')
        statid = statid.encode('utf-8')
        #if statid not in self.camdets['CamID']:
        #    return -1
        cam = np.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            statid = statid.upper()
            cam = np.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            cam = np.where(self.camdets['dummycode'] == statid) 
        if len(cam[0]) == 0:
            try:
                cam = np.where(np.logical_and(self.camdets['LID']==spls[0].encode('utf-8'), self.camdets['SID']==spls[1].encode('utf-8')))
            except: 
                pass

        # if we can't find the camera, assume its inactive
        if len(cam[0]) == 0:
            return -1
        else:
            c = cam[0][0]
            if activeonly is True and self.camdets[c]['active'] != 1:
                return -1
            return c

    def GetSiteLocation(self, camname, activeonly=True):
        c = self.getCameraOffset(camname, activeonly)
        if c == -1:
            return 'unknown'

        site = self.camdets[c]['Site'].decode('utf-8').strip()
        camid = self.camdets[c]['CamID'].decode('utf-8').strip()
        if camid == '':
            return site
        else:
            return site + '/' + camid

    def getDummyCode(self, lid, sid):
        lid = lid.encode('utf-8')
        sid = sid.encode('utf-8')
        cam = np.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))   
        if len(cam[0]) == 0:
            sid = sid.upper()
            lid = lid.upper()
            cam = np.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))
        if len(cam[0]) == 0:
            return 'Unknown'
        else:
            c = cam[0][0]
            return self.camdets[c]['dummycode'].decode('utf-8').strip()

    def getFolder(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return 'Unknown'
        else:
            site = self.camdets[c]['Site'].decode('utf-8').strip()
            camid = self.camdets[c]['CamID'].decode('utf-8').strip()
            return site + '/' + camid

    def checkCameraActive(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return False
        else:
            if self.camdets[c]['active'] != 1: 
                return False
            return True

    def getActiveCameras(self):
        return self.camdets[self.camdets['active']==1]

    def getCameraType(self, statid):
        c = self.getCameraOffset(statid)
        if c < 0:
            return -1
        else:
            return self.camdets[c]['camtyp'] 

    def getAllCamsAndFolders(self, isactive=False):
        # fetch camera details from the CSV file
        fldrs = []
        cams = []

        for row in self.camdets:
            if isactive is True and row['active'] != 1: 
                continue
            if row['Site'][:1] != '#':
                # print(row)
                if row['CamID'] == '':
                    fldrs.append(row['Site'].decode('utf-8'))
                else:
                    fldrs.append(row['Site'].decode('utf-8') + '/' + row['CamID'].decode('utf-8'))
                if int(row['camtyp']) == 1:
                    cams.append(row['LID'].decode('utf-8') + '_' + row['SID'].decode('utf-8'))
                else:
                    cams.append(row['LID'].decode('utf-8'))
        return cams, fldrs

    def getAllCamsStr(self, onlyActive=False):
        if onlyActive is False:
            cams, _ = self.getAllCamsAndFolders()
            cams.sort()
            tmpcams = ''
            for cam in cams:
                tmpcams = tmpcams + cam + ' ' 
            return tmpcams.strip()
        else:
            cams = self.getActiveCameras()
            tmpcams = ''
            for cam in cams:
                cname = cam['CamID'].decode('utf-8')
                if ' ' not in cname:
                    tmpcams = tmpcams + cname + ' ' 
            #tcc = tmpcams.split()
            #tcc.sort()
            #tmpcams = ''
            #for cname in tcc:
            #    tmpcams = tmpcams + cname + ' ' 
            return tmpcams.strip()

    def getAllLocsStr(self, onlyActive=False):
        if onlyActive is False:
            _, locs = self.getAllCamsAndFolders()
            locs.sort()
            tmpcams = ''
            for loc in locs:
                loc = loc.split('/')
                tmpcams = tmpcams + loc + ' ' 
            return tmpcams.strip()
        else:
            cams = self.getActiveCameras()
            tmpcams = ''
            for cam in cams:
                if cam['active']==1:
                    cname = cam['Site'].decode('utf-8')
                    if ' ' not in cname:
                        tmpcams = tmpcams + cname + ' ' 
            return tmpcams.strip()

    def getStationsAtSite(self, sitename, onlyactive=False):
        idlist = []
        bsite = sitename.encode('utf-8')
        fltred = self.camdets[self.camdets['Site'] == bsite]
        if onlyactive is True:
            fltred = fltred[fltred['active']==1]
        for rw in fltred:
            if int(rw['camtyp']) == 1:
                idlist.append(rw['LID'].decode('utf-8') + '_' + rw['SID'].decode('utf-8'))
            else:
                idlist.append(rw['LID'].decode('utf-8'))
        return idlist

    def getSites(self, onlyactive=True):
        sites=[]
        silist=self.camdets['Site']
        silist = np.unique(silist)
        sites = [si.decode('utf-8') for si in silist]
        return sites

    def getUFOCameras(self, onlyactive=False):
        camlist=[]
        ufo=self.camdets[self.camdets['camtyp']==1]
        if onlyactive is True:
            ufo = ufo[ufo['active'] == 1]
        for rw in ufo:
            ufoname = rw['LID'].decode('utf-8') + '_' + rw['SID'].decode('utf-8') 
            camlist.append({'Site':rw['Site'].decode('utf-8'), 'CamID':rw['CamID'].decode('utf-8'), 'dummycode':rw['dummycode'].decode('utf-8'), 'ufoid':ufoname})
        return camlist

    def getCameraLocAndDir(self, camid, activeonly=True):
        c = self.getCameraOffset(camid, activeonly=activeonly)
        if c < 0:
            return ''
        else:
            return self.camdets[c]['Site'].decode('utf_8') + '_' + self.camdets[c]['SID'].decode('utf_8')


'''
creating and managing the more-accurate camera location info
'''


def getCamLocDirFov(camid):
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    camdb = json.load(open(os.path.join(datadir, 'admin', 'cameraLocs.json')))
    return camdb[camid]


def updateCamLocDirFovDB():
    camdb = {}
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data/')
    ppfiles = glob.glob(os.path.join(datadir, 'consolidated','platepars', '*.json'))
    for ppf in ppfiles:
        try:
            pp = json.load(open(ppf))
            camid = pp['station_code']
            camdb.update({camid: {'lat': pp['lat'], 'lon': pp['lon'], 'ele': pp['elev'],
                'az': pp['az_centre'], 'alt': pp['alt_centre'], 'fov_h': pp['fov_h'], 'fov_v': pp['fov_v']}})
        except:
            # platepar was malformed
            continue
    with open(os.path.join(datadir, 'admin', 'cameraLocs.json'), 'w') as outf:
        json.dump(camdb, outf, indent=4)


def test_caminfo(sitename):
    ci = SiteInfo()
    spls = sitename.split('_')
    sid = spls[0]
    if len(spls) ==1:
        lid = ''
    else:
        lid = spls[1]
    print(ci.getDummyCode(sid, lid))

    #tz, site = ci.GetSiteLocation(site.encode('utf-8'))
    #print(site, tz)


if __name__ == '__main__':
    test_caminfo(sys.argv[1])
