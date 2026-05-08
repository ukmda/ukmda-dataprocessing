# Copyright (C) 2018-2023 Mark McIntyre
#
# Get list of orbits attempted with their status
#  
import sys


def parseDistriblog(logname):
    lis = open(logname,'r').readlines()
    dta = [x for x in lis if ('added to fails' in x or ('saved' in x and 'to' in x)) and ('CorrelateEngine' in x or 'CorrelateRMS' in x)]
    offset = 49 if 'match' in logname else 76
    for dd in dta:
        print(dd[offset:].strip())


if __name__ == '__main__':
    fname = sys.argv[1]
    parseDistriblog(fname)
