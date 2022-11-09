#
# simple script to get the active shower list from the IMO working list

from fileformats import imoWorkingShowerList as iwsl
import datetime
import sys


def getActiveShowers(targdate, retlist=False):
    sl = iwsl.IMOshowerList()
    listofshowers=sl.getActiveShowers(targdate,True)
    if retlist is False:
        for shwr in listofshowers:
            print(shwr)
    else:
        return listofshowers


if __name__ == '__main__':
    if len(sys.argv) > 1:
        targdate = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        targdate = datetime.datetime.now()
    getActiveShowers(targdate)
