from fileformats import UOFormat as uof
import datetime
import calendar
import sys
# import os


def getBestNMp4s(yr, mth, numtoget):
    matches = uof.MatchedCsv('./UKMON-all-matches.csv')

    sd = datetime.datetime(yr,mth,1)
    lastday = calendar.monthrange(yr, mth)[1]
    ed = datetime.datetime(yr,mth, lastday)
    sepdata = matches.selectByDateRange(sd, ed)

    sorteddata = sepdata.sort_values(by='_amag')[:numtoget]
    sortedlist = sorteddata['_localtime'].tolist()
    return sortedlist  


if __name__ == '__main__':
    lst = getBestNMp4s(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    for li in lst:
        print(li[1:])
