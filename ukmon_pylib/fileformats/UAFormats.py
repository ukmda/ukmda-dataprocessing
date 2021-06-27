# create a data type for UFO Analyser style CSV files
import numpy
import sys
import datetime
import numpy.lib.recfunctions as rfn


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
class DetectedCsv:
    def __init__(self, fname):
        """Construct the object from a filename

        Arguments:
            fname string -- The full path and filename to the CSV file
        """
        # load from file
        rawdata = numpy.loadtxt(fname, delimiter=',',skiprows=1, dtype=UFOCSV)
        # append field for timestamp
        self.rawdata = rfn.append_fields(rawdata,'timestamp', numpy.zeros(rawdata.shape[0], dtype='f8'), dtypes='f8')
        # fill in timestamp field
        for i in range(0, len(rawdata)):
            li = rawdata[i]
            sec = li['Sec']
            intsec = int(sec)
            us = int((sec -intsec) * 1000000)
            dt = datetime.datetime(li['Yr'],li['Mth'], li['Day'], 
                li['Hr'], li['Min'], intsec, us)
            self.rawdata[i]['timestamp']=dt.timestamp()

    def selectByMag(self, minMag=100, maxMag=-50):
        """ get data by magnitude

        """
        tmpa1 = self.rawdata[self.rawdata['Mag'] >= minMag]
        tmpa2 = tmpa1[tmpa1['Mag'] <= maxMag]
        return tmpa2

    def selectByShwr(self, shwr):
        """ Get data by shower ID eg LYR or spo 
        """
        if shwr != 'spo':
            tmpshwr = ' J8_' + shwr
        else:
            tmpshwr = shwr
        return self.rawdata[self.rawdata['Group']==tmpshwr]

    def selectByDate(self, sDate=datetime.datetime.now()):
        """ Get data for a specific 24 hour period 
            starting at noon on the date provided
        """
        sDate.replace(hour = 12, minute = 0, second = 0, microsecond=0)
        eDate = sDate + datetime.timedelta(days=1)
        return self.selectByDateRange(sDate, eDate)

    def selectByDateRange(self, sDate=datetime.datetime.now(), eDate=datetime.datetime.now()):
        """ Get data for a specified time range. 
            Note that this uses the exact range supplied. 
        """
        f1 = self.rawdata[self.rawdata['timestamp'] >= sDate.timestamp()]
        return f1[f1['timestamp'] <= eDate.timestamp()]

    def getExchangeData(self, eDate=datetime.datetime.now(), daysreq=3):
        """ get minimal data for exchange with other networks
        """
        sDate = eDate + datetime.timedelta(days = -daysreq)
        fltrset = self.selectByDateRange(sDate, eDate)
        outarr = []
        cam = fltrset['Loc_Cam']
        ts = fltrset['timestamp']
        if len(cam) > 0:
            for i in range(0,len(cam)):
                outarr.append((cam[i],datetime.datetime.fromtimestamp(ts[i].round(0)).strftime('%Y-%m-%dT%H:%M:%S')))

            # make the data unique, sort it by timestamp, then reverse the sort order
            outarr = numpy.unique(outarr, axis=0)
            outarr = outarr[outarr[:,1].argsort()]
            outarr = outarr[::-1]

            return outarr
        else:
            return None

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
