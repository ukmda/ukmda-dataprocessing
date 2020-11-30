# create a data type for RMS R90-style CSV files
import numpy

#defines the data content 
R90CSV = numpy.dtype([('Ver','S8'),('Yr','i4'),('Mth','i4'),('Day','i4'),
    ('Hr','i4'),('Min','i4'),('Sec','f8'), ('Mag','f8'),('Dur','f8'),
    ('Dir1','f8'), ('Alt1','f8'), ('Dir2','f8'), ('Alt2','f8'),
    ('Ra1','f8'), ('Dec1','f8'), ('Ra2','f8'), ('Dec2','f8'),
    ('Loc_Cam','S16'), ('Longi','f8'), ('Lati','f8'), ('Alti','f8'), ('TZ','f8')])

#-----------------------------------------------------------------------
import sys
import numpy

# For testing.
# example: python UAdata.py 2019

def main():
    i=0
    yr = sys.argv[1]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/p_' + yr + '-unified.csv'
    print(fnam)
    mydata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=R90CSV)

    print(mydata[i]) # print the ith row
    print(mydata['Mag']) # print all the magnitudes
    print(mydata[i]['Mag']) # print the mag on the ith row


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------


