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
    def __init__(self, fname=None):
        if fname is None:
            fname = os.getenv('CAMINFO')
            if len(fname) < 5:
                fname = '/home/ec2-user/ukmon-shared/consolidated/camera-details.csv'

        self.camdets = numpy.loadtxt(fname, delimiter=',', skiprows=2, dtype=CameraDetails)
        #print(self.camdets)

    def GetSiteLocation(self, camname):
        eles = camname.split(b'_')
        if len(eles) > 2:
            lid = eles[0].strip() + b'_' + eles[1].strip()
        else:
            lid = eles[0].strip()
        if len(eles) > 1:
            sid = camname.split(b'_')[len(eles)-1].strip()
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

    def getFolder(self, statid):
        statid = statid.encode('utf-8')
        cam = numpy.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            statid = statid.upper()
            cam = numpy.where(self.camdets['CamID'] == statid) 
        if len(cam[0]) == 0:
            return 'Unknown'
        else:
            c = cam[0][0]
            site = self.camdets[c]['Site'].decode('utf-8').strip()
            camid = self.camdets[c]['CamID'].decode('utf-8').strip()
            return site + '/' + camid

    def getAllCamsAndFolders(self):
        # fetch camera details from the CSV file
        fldrs = []
        cams = []

        for row in self.camdets:
            if row[0][:1] != '#':
                # print(row)
                if row[1] == '':
                    fldrs.append(row[0].decode('utf-8'))
                else:
                    fldrs.append(row[0].decode('utf-8') + '/' + row[1].decode('utf-8'))
                if int(row[11]) == 1:
                    cams.append(row[2].decode('utf-8') + '_' + row[3].decode('utf-8'))
                else:
                    cams.append(row[2].decode('utf-8') + '_')
        return cams, fldrs


def main(sitename):
    ci = SiteInfo()
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
    main(sys.argv[1])
