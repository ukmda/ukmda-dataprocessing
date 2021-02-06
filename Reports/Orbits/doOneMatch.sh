#!/bin/bash
#
# Script to call reduceOrbit and then move the results as needed 
# for the archive website
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the helper functions
source $HOME/src/config/config.ini > /dev/null 2>&1

source $HOME/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$wmpl_loc

outdir=${REPORTDIR}/matches/$yr
indir=${MATCHDIR}/$yr/$ym/$pth
mkdir -p $here/logs >/dev/null 2>&1

pth=$1
yr=${pth:0:4}
ym=${pth:0:6}
mth=${pth:4:2}

${SRC}/orbits/reduceOrbit.sh $pth $2
res=$?

if [ $res -eq 0 ] ; then
    indir=${MATCHDIR}/$yr/$ym/$pth
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)

    python $here/findJPGs.py $indir $resultdir
    chmod 644 $resultdir/*.jpg

    ${SRC}/website/createPageIndex.sh $resultdir

    mkdir $outdir/csv/ >/dev/null 2>&1
    cp $resultdir/*orbit.csv $outdir/csv/
    mkdir $outdir/extracsv/ >/dev/null 2>&1
    cp $resultdir/*orbit_extras.csv $outdir/extracsv/    

    echo $(date +%Y%m%d-%H%M%S) $(basename $resultdir) >> $here/logs/success_list.txt
elif [ $res -eq 99 ] ; then
    echo "$1 skipped as already processed"
else
    echo "$1 was not solvable - probably not a true match"
    echo "not solvable" > $indir/notsolvable.txt
fi 

exit $res
