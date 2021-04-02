#
# Create additional information from pickled Trajectory file
#

import glob
from wmpl.Trajectory.Trajectory import Trajectory
from wmpl.Utils.Pickling import loadPickle 

from ufoTrajSolver import createAdditionalOutput


def generateSummaryAndCSVs(outdir):

    picklefile = glob.glob1(outdir, '*.pickle')
    traj = loadPickle(outdir, picklefile)
    createAdditionalOutput(traj, outdir)

