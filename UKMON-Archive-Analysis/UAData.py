# create a data type for UFO Analyser style CSV files
import numpy

UAData = numpy.dtype([('Ver','S8'),('Group','S8'),('LocalTime','S16'),
    ('Mag','f8'),('Dur','f8'),('AV','f8'),('Loc_Cam','S16'),
    ('TZ','f8'),('Yr','i4'),('Mth','i4'),('Day','i4'),
    ('Hr','i4'),('Min','i4'),('Sec','f8'), ('Dir1','f8'), ('Alt1','f8'),
    ('Ra1','f8'), ('Dec1','f8'), ('Ra2','f8'), ('Dec2','f8'),('alpha','f8'),
    ('delta','f8'),('','f8'), ('','f8'),('','f8'),('','f8') ,('','f8'),
    ('io','f8'),('err1','f8'),('err2','f8'),('G1','S8'),('dd','f8'),('dr','f8'),
    ('Vo','f8'),('dV','f8'),('ra_m','f8'),('dec_m','f8'),
    ('refs','f8'),('errm','f8'),
    ('rat','f8'),('dct','f8'),('voo','f8'),('vooerr','f8'),('tmerr','f8'),
    ('sps','i4'),('sN','i4'),('drop','f8')])

#-----------------------------------------------------------------------
import sys
import numpy

# For testing.
# example: python UAdata.py 2019

def main():
    i=0
    yr = sys.argv[1]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_' + yr + '-unified.csv'
    print(fnam)
    mydata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=UAData)

    print(mydata[i]) # print the ith row
    print(mydata['Mag']) # print all the magnitudes
    print(mydata[i]['Mag']) # print the mag on the ith row


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------


