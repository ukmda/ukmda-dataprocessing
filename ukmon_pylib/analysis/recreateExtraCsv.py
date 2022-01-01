#
# python script to update the additional data files 
#
import glob
import os
import sys
import shutil
from wmpl.Utils.Pickling import loadPickle 
from traj.ufoTrajSolver import createAdditionalOutput


def generateExtraFiles(outdir):
    outdir=outdir.strip()
    print(outdir)
    picklefile = glob.glob1(outdir, '*.pickle')[0]
    traj = loadPickle(outdir, picklefile)
    traj.save_results = True
    oldfiles = glob.glob1(outdir, '*.csv')
    for f in oldfiles:
        if 'track' in f or 'orbit' in f:
            os.remove(os.path.join(outdir, f))

    createAdditionalOutput(traj, outdir)

    oldfiles = glob.glob1(outdir, '*.csv')
    for f in oldfiles:
        if 'orbit_extras' in f:
            shutil.copy2(os.path.join(outdir, f), '/home/ec2-user/prod/data/orbits/2021/extracsv/')
        if 'orbit.csv' in f:
            shutil.copy2(os.path.join(outdir, f), '/home/ec2-user/prod/data/orbits/2021/csv/')

    return


if __name__ == '__main__':
    rootdir = sys.argv[1]
    with open('/tmp/dlist.txt') as inf:
        dirlist = inf.readlines()
    for fldr in dirlist:
        generateExtraFiles(fldr)

#    dirlist = os.listdir(rootdir)
#    for di in dirlist:
#        dayfs = os.listdir(os.path.join(rootdir, di))
#        for fldr in dayfs:
#            pth = os.path.join(os.path.join(rootdir, di, fldr))
#            print(pth)
#            generateExtraFiles(pth)
