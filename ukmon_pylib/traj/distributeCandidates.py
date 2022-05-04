#
# Used when running the correlator in 'distributed' mode. 
# Pick up new groups of candidate trajectories and distribute them.
#

import json
import os
import shutil
import glob
import math
import datetime


def createTaskTemplate(rundate, buckname, spandays=3):
    d1 = (rundate + datetime.timedelta(days = -(spandays-1))).strftime('%Y%m%d')
    d2 = (rundate + datetime.timedelta(days = 1)).strftime('%Y%m%d')

    templdir,_ = os.path.split(__file__)
    templatefile = os.path.join(templdir, 'taskrunner.json')
    clusdetails = os.path.join(templdir, 'clusdetails.txt')
    with open(clusdetails) as inf:
        lis = inf.readlines()
    clusname = [x for x in lis if x[:4] == 'clus'][0].split(' ')[2].strip()[1:-1]
    subnet = [x for x in lis if x[:6] == 'subnet'][0].split(' ')[2].strip()[1:-1]
    secgrp = [x for x in lis if x[:6] == 'secgrp'][0].split(' ')[2].strip()[1:-1]
    exrolearn = [x for x in lis if x[:6] == 'taskro'][0].split(' ')[2].strip()[1:-1]

    targdir, buckname = os.path.split(buckname)
    with open(templatefile) as inf:
        templ = json.load(inf)
        templ['cluster'] = clusname
        templ['networkConfiguration']['awsvpcConfiguration']['subnets'] = [f'{subnet}']
        templ['networkConfiguration']['awsvpcConfiguration']['securityGroups'] = [f'{secgrp}']
        templ['overrides']['executionRoleArn'] = exrolearn
        templ['overrides']['containerOverrides'][0]['command'] = [f'{buckname}', f'{d1}', f'{d2}']

    with open(os.path.join(targdir, buckname + '.json'), 'w') as outf:
        json.dump(templ, outf, indent=4)


def distributeCandidates(rundate, srcdir, targdir, maxcount=20):

    print(srcdir)
    # obtain a list of picklefiles and sort by name
    flist = glob.glob1(srcdir, '*.pickle')
    flist.sort()

    # work out how many buckets i need
    numcands = len(flist)
    numbucks = int(math.ceil(numcands/maxcount))

    # create buckets
    buckroot = os.path.join(targdir, rundate.strftime('%Y%m%d_'))
    for i in range(0, numbucks):
        buckname = buckroot + f'{i:02d}'
        os.makedirs(buckname, exist_ok=True)
        bucklist = flist[i::numbucks]
        with open(os.path.join(buckname, f'files_{i:02d}.txt'),'w') as outf:
            for fli in bucklist:
                src = os.path.join(srcdir, fli)
                dst = os.path.join(buckname, fli)
                shutil.copy2(src, dst)
                outf.write(f'{fli}\n')

        createTaskTemplate(rundate, buckname)


if __name__ == '__main__':
    rundt = datetime.datetime(2022,4,21)
    srcdir = 'f:/videos/meteorcam/ukmondata/disttest/RMSCorrelate/candidates'
    targdir = 'f:/videos/meteorcam/ukmondata/disttest/RMSCorrelate/distribs'
    distributeCandidates(rundt, srcdir, targdir)
