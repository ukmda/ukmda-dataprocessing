#
# simple script to get the active shower list from the IMO working list

from fileformats import imoWorkingShowerList as iwsl
import datetime
import sys
import argparse


def getActiveShowers(targdate, retlist=False, inclMinor=False):
    sl = iwsl.IMOshowerList()
    listofshowers=sl.getActiveShowers(targdate,True, inclMinor=inclMinor)
    if retlist is False:
        for shwr in listofshowers:
            print(shwr)
    else:
        return listofshowers


def getActiveShowersStr(targdatestr):
    targdate = datetime.datetime.strptime(targdatestr, '%Y%m%d')
    shwrs = getActiveShowers(targdate, retlist=True)
    shwrs.append('spo')
    for s in shwrs:
        print(s)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='get list of active showers',
        formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('-d', '--targdate', metavar='TARGDATE', type=str,
        help='Date to run for (default is today)')
    arg_parser.add_argument('-m', '--includeminor', action="store_true",
        help='include minor showers')

    cml_args = arg_parser.parse_args()
    if cml_args.targdate is not None:
        targdate = datetime.datetime.strptime(cml_args.targdate, '%Y%m%d')
    else:
        targdate = datetime.datetime.now()
    getActiveShowers(targdate, inclMinor=cml_args.includeminor)
