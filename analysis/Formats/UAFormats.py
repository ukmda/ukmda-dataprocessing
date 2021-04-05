# create a data type for UFO Analyser style CSV files
import numpy
import sys

#defines the data content of a UFOAnalyser CSV file
UFOCSV = numpy.dtype([('Ver','U8'),('Group','U8'),('LocalTime','U16'),
    ('Mag','f8'),('Dur','f8'),('AV','f8'),('Loc_Cam','U16'),
    ('TZ','f8'),('Yr','i4'),('Mth','i4'),('Day','i4'),
    ('Hr','i4'),('Min','i4'),('Sec','f8'), ('Dir1','f8'), ('Alt1','f8'),
    ('Ra1','f8'), ('Dec1','f8'), ('Ra2','f8'), ('Dec2','f8'),('alpha','f8'),
    # the remaining values are derived using UA's approximations and are unreliable
    # note also that UA uses -1$ and sometimes -1.#IND0 to indicate maths errors
    # so although all these values are floats we have to read some in as unicode strings
    ('delta','f8'),('','f8'), ('','f8'),('','f8'),('','f8'),('','f8'),
    ('io','U8'),('err1','U8'),('err2','U8'),('G1','U8'),('dd','U8'),
    ('dr','U8'),('Vo','U8'),('dV','U8'),('ra_m','f8'),('dec_m','f8'),
    ('refs','f8'),('errm','f8'),
    ('rat','f8'),('dct','f8'),('voo','f8'),('vooerr','f8'),('tmerr','f8'),
    ('sps','i4'),('sN','i4'),('drop','f8')])

# format string for writing back out using numpy.savetxt
UFOCSVfmt = '%s,%s,%s,%.4f,%.4f,%.4f,%s\
    ,%d,%d,%d,%d,%d,%d,%.4f,%.6f,%.6f\
    ,%.6f,%.6f,%.6f,%.6f,%.6f\
    ,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\
    ,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\
    ,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%d,%.6f'
#-----------------------------------------------------------------------

# For testing.
# example: python UAdata.py 2019


def main():
    i=0
    yr = sys.argv[1]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_' + yr + '-unified.csv'
    print(fnam)
    mydata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=UFOCSV)

    print(mydata[i]) # print the ith row
    print(mydata['Mag']) # print all the magnitudes
    print(mydata[i]['Mag']) # print the mag on the ith row


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------
