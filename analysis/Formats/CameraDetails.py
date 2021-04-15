# Create a data type for the camera location details
import numpy
import sys
import os


# defines the data content of a UFOAnalyser CSV file
CameraDetails = numpy.dtype([('Site', 'S32'), ('CamID', 'S32'), ('LID', 'S16'),
    ('SID', 'S8'), ('Camera', 'S16'), ('Lens', 'S16'), ('xh', 'i4'),
    ('yh', 'i4'), ('Longi', 'f8'), ('Lati', 'f8'), ('Alti', 'f8'), 
    ('camtyp', 'i4'), ('dummycode','S6')])


class SiteInfo:
    def __init__(self, fname):
        self.camdets = numpy.loadtxt(fname, delimiter=',', skiprows=2, dtype=CameraDetails)
        #print(self.camdets)

    def GetSiteLocation(self, camname):
        eles = camname.split(b'_')
        lid = eles[0].strip()
        if len(eles) > 1:
            sid = camname.split(b'_')[1].strip()
            print(lid, sid)
            cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))
            if len(cam[0]) == 0:
                sid = sid.upper()
                lid = lid.upper()
                cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))

        else:
            cam = numpy.where((self.camdets['LID'] == lid))
        if len(cam[0]) == 0:
            return 0, 0, 0, 0, 'Unknown'
        c = cam[0][0]
        longi = self.camdets[c]['Longi']
        lati = self.camdets[c]['Lati']
        alti = self.camdets[c]['Alti']
        tz = 0  # camdets[c]['tz']
        site = self.camdets[c]['Site'].decode('utf-8').strip()
        camid = self.camdets[c]['CamID'].decode('utf-8').strip()
        if camid == '':
            return lati, longi, alti, tz, site
        else:
            return lati, longi, alti, tz, site + '/' + camid

    def getDummyCode(self, lid, sid):
        #print(lid, sid)
        lid = lid.encode('utf-8')
        sid = sid.encode('utf-8')
        cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))   
        if len(cam[0]) == 0:
            sid = sid.upper()
            lid = lid.upper()
            cam = numpy.where((self.camdets['LID'] == lid) & (self.camdets['SID'] == sid))
        if len(cam[0]) == 0:
            return 'Unknown'
        else:
            c = cam[0][0]
            return self.camdets[c]['dummycode'].decode('utf-8').strip()


def main(sitename, camfileloc):
    fnam = os.path.join(camfileloc,'camera-details.csv')
    #print(fnam)
    ci = SiteInfo(fnam)
    spls = sitename.split('_')
    sid = spls[0]
    if len(spls) ==1:
        lid = ''
    else:
        lid = spls[1]
    print(ci.getDummyCode(sid, lid))

    #lati, longi, alti, tz, site = ci.GetSiteLocation(site.encode('utf-8'))
    #print(site, lati, longi, alti, tz)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
