#
# Python script to report on active showers
#

import sys
import datetime

from utils.getActiveShowers import getActiveShowers
from analysis.showerAnalysis import showerAnalysis
from reports.findFireballs import findFireballs


def createShowerIndexPage(dt, shwr):
    return


def reportActiveShowers(ymd):
    shwrlist = getActiveShowers(ymd, retlist=True)
    print(shwrlist)
    dtstr = ymd.strftime('%Y')
    for shwr in shwrlist:
        showerAnalysis(shwr, int(dtstr))
        findFireballs(int(dtstr), shwr, 999)
        createShowerIndexPage(int(dtstr), shwr)
    return 


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ymd = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        ymd = datetime.datetime.now()
    reportActiveShowers(ymd)
