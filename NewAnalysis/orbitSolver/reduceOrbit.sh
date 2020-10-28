#!/bin/bash
# bash script to reduce a folder of A.XML files using WMPL
#

# load the helper functions
dos2unix ./orbitsolver.ini > /dev/null 2>&1
source ./orbitsolver.ini > /dev/null 2>&1

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$wmpl_loc
outdir=$results

python ufoTrajSolver.py $outdir $1