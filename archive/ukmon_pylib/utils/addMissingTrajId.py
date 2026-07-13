# Fix up the matches file to add missing traj_ids

# Copyright (C) 2018- Mark McIntyre

# This should be a one-off but its useful to hang onto the script in case i want
# to rerun it on other years data

import sys
import os
from wmpl.Utils.Pickling import loadPickle
import requests

def fixAYear(yr):
    datadir=os.getenv('DATADIR')
    srcf = os.path.join(datadir, 'matched', f'matches-full-{yr}.csv')
    if not os.path.isfile(srcf):
        print(f'source file {srcf} not found')
        return 
    outf = os.path.join(datadir, 'matched', f'matches-full-{yr}-mod.csv')
    with open(outf,'w') as targf:
        lis = open(srcf,'r').readlines()
        for li in lis:
            if '_Version' not in li:
                spls = li.split(',')
                traj_id = spls[-1].strip()
                if len(traj_id) < 1:
                    pickname = spls[113].replace('ground_track.png', 'trajectory.pickle')
                    res = requests.get(pickname)
                    if res.status_code == 200:
                        with open('/tmp/tmp.pickle', 'wb') as outf:
                            outf.write(res.content)
                        pick = loadPickle('/tmp', 'tmp.pickle')
                        if 'traj_id' in pick:
                            print(f'updating {spls[110]}')
                            li = li.replace('\n', pick.traj_id + '\n')
                        else:
                            print(f'traj_id not available for{spls[110]}')
                    else:
                        print(f'unable to find pickle for {spls[110]}')
                else:
                    # line already has traj_id
                    pass
            else:
                # header line, no need to change it
                pass
            targf.write(li)


if __name__ == '__main__':
    fixAYear(sys.argv[1])