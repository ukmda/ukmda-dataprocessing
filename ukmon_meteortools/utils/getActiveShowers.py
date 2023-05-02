# Copyright (C) 2018-2023 Mark McIntyre
#
# simple script to get the active shower list from the IMO working list

from ukmon_meteortools.fileformats import imoWorkingShowerList as iwsl
import datetime
import argparse


def getActiveShowers(targdate, retlist=False, inclMinor=False):
    """
    Return a list of showers active at the specified date  

    Arguments:  
        targdate:   [str] Date in YYYYMMDD format  

    Keyword Arguments:  
        retlist:    [bool] return a list, or print to console. Default False=print  
        inclMinor:  [bool] include minor showers or only return major showers  

    Returns:  
        If retlist is true, returns a python list of shower short-codes eg ['PER','LYR']  

    """
    sl = iwsl.IMOshowerList()
    listofshowers=sl.getActiveShowers(targdate,True, inclMinor=inclMinor)
    if retlist is False:
        for shwr in listofshowers:
            print(shwr)
    else:
        return listofshowers


def getActiveShowersStr(targdatestr):
    """
    Prints a comma-separated list of showers active at the specified date  

    Arguments:  
        targdate:   [str] Date in YYYYMMDD format  

    Returns:  
        nothing  

    """
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
