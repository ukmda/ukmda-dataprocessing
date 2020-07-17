# Python class to parse a UFOCapture XML files
import os, sys
import xmltodict 
import numpy

class UCXml: 
    def __init__(self, fname):
        with open(fname) as fd:
            self.ucxml=xmltodict.parse(fd.read())    
    def getDate(self):
        ur=self.ucxml['ufocapture_record']
        return int(ur['@y'])*10000 + int(ur['@mo'])*100 +int(ur['@d'])
    def getDateYMD(self):
        yr= int(self.ucxml['ufocapture_record']['@y'])
        mo = int(self.ucxml['ufocapture_record']['@mo'])
        dy = int(self.ucxml['ufocapture_record']['@d'])
        return yr,mo,dy
    def getDateStr(self):
        ur=self.ucxml['ufocapture_record']
        return ur['@y']+"-"+ur['@mo']+"-"+ur['@d']

    def getTime(self):
        ur=self.ucxml['ufocapture_record']
        return int(ur['@h'])*3600 + int(ur['@m'])*60 +float(ur['@s'])
    def getTimeStr(self):
        ur=self.ucxml['ufocapture_record']
        return ur['@h'] +":"+ ur['@m']+":" +ur['@s']
    def getTimeHMS(self):
        h = int(self.ucxml['ufocapture_record']['@h'])
        m = int(self.ucxml['ufocapture_record']['@m'])
        s =  float(self.ucxml['ufocapture_record']['@s'])
        return h,m,s

    def getCameraDetails(self):
        fps = float(self.ucxml['ufocapture_record']['@fps'])
        cx  = float(self.ucxml['ufocapture_record']['@cx'])
        cy  = float(self.ucxml['ufocapture_record']['@cy'])
        return fps,cx,cy

    def getStationDetails(self):
        sta = self.ucxml['ufocapture_record']['@lid'] + "_"+self.ucxml['ufocapture_record']['@sid']
        lid = self.ucxml['ufocapture_record']['@lid']
        sid =  self.ucxml['ufocapture_record']['@sid']
        lat = float(self.ucxml['ufocapture_record']['@lat'])
        lng = float(self.ucxml['ufocapture_record']['@lng'])
        alt = float(self.ucxml['ufocapture_record']['@alt'])
        return sta, lid, sid, lat, lng, alt

    def getHits(self):
        uc=self.ucxml['ufocapture_record']['ufocapture_paths']
        return int(uc['@hit'])

    def getPath(self):
        try:
            uc=self.ucxml['ufocapture_record']['ufocapture_paths']
        except:
            print('xml file not valid - no ufocapture_paths')
            pathx=numpy.empty(1)
            pathy=numpy.empty(1)
            bri=numpy.empty(1)
            return pathx, pathy, bri
        nhits=int(uc['@hit'])
        pathx=numpy.empty(nhits)
        pathy=numpy.empty(nhits)
        bri=numpy.empty(nhits)
        if nhits < 2 :
            return pathx, pathy, bri
            
        for i in range(nhits):
           p=uc['uc_path'][i]
           pathx[i]=p['@x']
           pathy[i]=p['@y']
           bri[i]=p['@bmax']
        return pathx, pathy, bri

    def getPathElement(self, fno):
        uc=self.ucxml['ufocapture_record']['ufocapture_paths']
        pth=uc['uc_path'][fno]
        return pth['@fno'],pth['@ono'], pth['@pixel'],pth['@bmax'],pth['@x'],pth['@y']

if __name__ == '__main__':
    dd=UCXml('test_data/M20200427_201548_TACKLEY_NE.XML')

    y,m,d = dd.getDateYMD()
    h,mi,s = dd.getTimeHMS()
    print ('date and time', y,m,d,h,mi,s)

    station, lid, sid, lat, lng,alti=dd.getStationDetails()
    fps, cx, cy = dd.getCameraDetails()
    print('location', station, lat, lng, alti)
    print('camera', fps, cx, cy)

    nhits = dd.getHits()
    for i in range(nhits):
        fno,ono,pixel,bmax,x,y = dd.getPathElement(i)
        print(fno,pixel,bmax,x,y)
 