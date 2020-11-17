#!/bin/bash
# bash script to reduce a folder of A.XML files using WMPL
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the helper functions
source $here/orbitsolver.ini > /dev/null 2>&1

source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$wmpl_loc
pth=$1
if [ $# -lt 3 ] ; then 
    yr=${pth:0:4}
    ym=${pth:0:6}
else
    yr=$2
    ym=$3
fi 
outdir=$results/$yr/orbits/$ym
mkdir -p $outdir >/dev/null 2>&1

cd $here
python ufoTrajSolver.py $outdir $1