#
# simple script to get the active shower list from the IMO working list

from fileformats import imoWorkingShowerList as iwsl
import datetime
import sys

if len(sys.argv) > 1:
    imofile = sys.argv[1]

sl = iwsl.IMOshowerList()
p=sl.getActiveShowers(datetime.datetime.now(),True)
for shwr in p:
    print(shwr)
