# Copyright (C) 2018-2023 Mark McIntyre

# create a data type for UFO Analyser style CSV files
import numpy
import sys
import os
import datetime
import pandas as pd


# format string for writing back out using numpy.savetxt
#UFOCSVfmt = '%s,%s,%s,%.4f,%.4f,%.4f,%s\
#    ,%d,%d,%d,%d,%d,%d,%.4f,%.6f,%.6f\
#    ,%.6f,%.6f,%.6f,%.6f,%.6f\
#    ,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\
#    ,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\
#    ,%.6f,%.6f,%.6f,%.6f,%.6f,%d,%d,%.6f'


#-----------------------------------------------------------------------
class DetectedCsv:
    def __init__(self, fname):
        """Construct the object from a filename

        Arguments:
            fname string -- The full path and filename to the CSV file
        """
        # load from file
        # append field for timestamp
        if not os.path.isfile(fname):
            self.rawdata = None
            print('datafile missing!')
            return 
        
        self.rawdata = pd.read_csv(fname, delimiter=',')
        ts=[]
        for _,row in self.rawdata.iterrows():
            ts.append(datetime.datetime.strptime(row['LocalTime'],'%Y%m%d_%H%M%S').timestamp())
        self.rawdata['timestamp'] = ts

    def selectByMag(self, minMag=100, maxMag=-50, filterbadav=False):
        """ get data by magnitude
        """
        if self.rawdata is None:
            print('datafile missing!')
            return None
        tmpa1 = self.rawdata[self.rawdata['Mag'] <= minMag]
        tmpa2 = tmpa1[tmpa1['Mag'] >= maxMag]
        if filterbadav is True: 
            tmpa2 = tmpa2[tmpa2['AV(deg/s)']!=0]  # exclude events with no angular velocity
        return tmpa2

    def selectByStation(self, stationid):
        """ get data by station ID
        """
        if self.rawdata is None:
            print('datafile missing!')
            return None
        tmpa2 = self.rawdata[self.rawdata['Loc_Cam'] == stationid]
        return tmpa2

    def selectByShwr(self, shwr):
        """ Get data by shower ID eg LYR or spo 
        """
        if self.rawdata is None:
            print('datafile missing!')
            return None
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
        if self.rawdata is None:
            print('datafile missing!')
            return None

        f1 = self.rawdata[self.rawdata['timestamp'] >= sDate.timestamp()]
        f1 = f1[f1['timestamp'] <= eDate.timestamp()]
        return f1

    def getExchangeData(self, eDate=datetime.datetime.now(), daysreq=3):
        """ get minimal data for exchange with other networks
        """
        if self.rawdata is None:
            print('datafile missing!')
            return None

        sDate = eDate + datetime.timedelta(days = -daysreq)
        fltrset = self.selectByDateRange(sDate, eDate)
        outarr = []
        cams = fltrset['Loc_Cam']
        tss = fltrset['timestamp']
        if len(cams) > 0:
            for cam, ts in zip(cams,tss):
                outarr.append((cam, datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')))

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
    yr = sys.argv[1]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_' + yr + '-unified.csv'
    print(fnam)
    d = DetectedCsv(fnam)
    print(d.Mag)


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------
