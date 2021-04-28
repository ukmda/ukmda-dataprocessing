#
# simple script to get the active shower list from the IMO working list

import fileformats.imoWorkingShowerList as iwsl
import datetime
import sys

imofile = '/home/ec2-user/prod/share/IMO_Working_Meteor_Shower_List.xml'
if len(sys.argv) > 1:
    imofile = sys.argv[1]

sl = iwsl.IMOshowerList(imofile)
p=sl.getActiveShowers(datetime.datetime.now(),True)
for shwr in p:
    print(shwr)
