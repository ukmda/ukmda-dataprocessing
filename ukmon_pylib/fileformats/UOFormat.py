# create a data type for UFO Orbit style CSV files
import sys
import datetime
import pandas as pd
from wmpl.Utils.TrajConversions import date2JD


#-----------------------------------------------------------------------
class MatchedCsv:
    def __init__(self, fname):
        """Construct the object from a filename

        Arguments:
            fname string -- The full path and filename to the CSV file
        """
        # load from file
        self.rawdata = pd.read_csv(fname, delimiter=',')

    def selectByMag(self, minMag=100, maxMag=-50):
        """ get data by magnitude

        """
        tmpa1 = self.rawdata[self.rawdata['_amag'] <= minMag]
        tmpa2 = tmpa1[tmpa1['_amag'] >= maxMag]
        return tmpa2

    def selectByShwr(self, shwr):
        """ Get data by shower ID eg LYR or spo 
        """
        tmpshwr = ' ' + shwr
        return self.rawdata[self.rawdata['_stream']==tmpshwr]

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
        sjd = date2JD(sDate.year, sDate.month, sDate.day, 12,0,0) - 2400000.5
        ejd = date2JD(eDate.year, eDate.month, eDate.day, 12,0,0) - 2400000.5
        f1 = self.rawdata[self.rawdata['_mjd'] >= sjd]
        return f1[f1['_mjd'] <= ejd]

#-----------------------------------------------------------------------
# For testing.
# example: python UOFormat.py 


def main():
    fnam = sys.argv[1]
    mydata = MatchedCsv(fnam)
    shwdata = mydata.selectByShwr('LYR')
    print(shwdata)


if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------
