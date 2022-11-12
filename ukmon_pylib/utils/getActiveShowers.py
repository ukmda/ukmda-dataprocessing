#
# simple script to get the active shower list from the IMO working list

from fileformats import imoWorkingShowerList as iwsl
import datetime
import sys

if len(sys.argv) > 1:
    targdate = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
else:
    targdate = datetime.datetime.now()

sl = iwsl.IMOshowerList()
p=sl.getActiveShowers(targdate,True)
for shwr in p:
    print(shwr)
