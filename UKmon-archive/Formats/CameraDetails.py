# Create a data type for the camera location details
import numpy

#defines the data content of a UFOAnalyser CSV file
CameraDetails = numpy.dtype([('Site','S32'),('CamID','S32'),('LID','S16'),
    ('SID','S8'),('Camera','S16'), ('Lens','S16'),('xh','i4'),
    ('yh','i4'),('Lati','f8'),('Longi','f8'),('Alti','f8')])

#-----------------------------------------------------------------------
import sys
import numpy

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


