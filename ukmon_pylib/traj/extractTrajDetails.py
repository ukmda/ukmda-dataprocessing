#
# Python script to find details of a solved orbit in the processed_trajectories file 
# and save the jSON so it can be added to server-side data. 
#

import sys
import os
import json


def patchTrajDB(dbfile, targpath, oldstr='/home/ec2-user/data/RMSCorrelate'):

    with open(dbfile, 'r') as inf:
        with open(os.path.join(targpath, 'processed_trajectories.json'), 'w') as outf:
            for lin in inf:
                outf.write(lin.replace(oldstr, targpath))            
    return 


def findMatchingDetails(orbname, trajfile):
    with open(trajfile) as inf:
        js = json.load(inf)
    for tr in js['trajectories']:
        thistr = js['trajectories'][tr]
        if orbname in thistr['traj_file_path']:
            break
    
    return '{\"'+ tr + '\": ' + json.dumps(thistr) + '}'


if __name__ =='__main__':
    if len(sys.argv) < 3: 
        print('usage: python extractTrajDetails.py orbitname trajfile')
        print('where orbitname is something like 20211121_015234.456_UK')
        exit(0)

    orbname = os.path.basename(sys.argv[1])
    orbjson = findMatchingDetails(orbname, sys.argv[2])
    with open(orbname + '.json','w') as outf:
        outf.write(orbjson)
