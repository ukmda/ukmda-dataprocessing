# Create a data type for the camera location details
import numpy

#defines the data content of a UFOAnalyser CSV file
CameraDetails = numpy.dtype([('Site','S32'),('CamID','S32'),('LID','S16'),
    ('SID','S8'),('Camera','S16'), ('Lens','S16'),('xh','i4'),
    ('yh','i4'),('Longi','f8'),('Lati','f8'),('Alti','f8')])

UKmIdx = numpy.dtype([('Shwr','S8'),('Yr','i4'),('Mth','i4'),('Day','i4'),
    ('Hr','i4'),('Min','i4'),('Sec','f8'), ('Mag','f8'),('Dur','f8'),
    ('Dir1','f8'), ('Alt1','f8'), ('Dir2','f8'), ('Alt2','f8'),
    ('Loc_Cam','S16'), ('Longi','f8'), ('Lati','f8'), ('Alti','f8'), ('TZ','f8'),('FileLoc', 'S128')])

#-----------------------------------------------------------------------

import sys
import numpy

def GetCamDetails(camname, camdets):
        eles=camname.split(b'_')
        lid=eles[0].strip()
        if len(eles) > 1:
            sid=camname.split(b'_')[1].strip()
            cam=numpy.where((camdets['LID']==lid) & (camdets['SID']==sid))
        else:
            cam=numpy.where((camdets['LID']==lid))
        if len(cam[0]) ==0 :
            return 0,0,0,0,'Unknown'
        c=cam[0][0]
        longi=camdets[c]['Longi']
        lati=camdets[c]['Lati']
        alti=camdets[c]['Alti']
        tz=0 # camdets[c]['tz']
        site=camdets[c]['Site'].decode('utf-8').strip()
        camid=camdets[c]['CamID'].decode('utf-8').strip()
        if camid == '' :
            return lati, longi, alti, tz, site
        else:
            return lati, longi, alti, tz, site+'/'+camid

# For testing.
# example: python UAFormats.py 2019

def main():
    i=4
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/camera-details.csv'
    print(fnam)
    mydata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=CameraDetails)

    print(mydata[i]) # print the ith row
    print(mydata['LID']) # print all the magnitudes
    print(mydata[i]['Site']) # print the mag on the ith row
    tac=numpy.where(mydata['Site']==b'Tackley')
    print(len(tac[0]))
    print(mydata[tac[0][0]]['Lati'])


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------


