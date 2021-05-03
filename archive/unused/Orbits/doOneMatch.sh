#!/bin/bash
#
# Script to call reduceOrbit and then move the results as needed 
# for the archive website
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

source $here/../config/config.ini >/dev/null 2>&1

source $HOME/venvs/${WMPL_ENV}/bin/activate
export PYTHONPATH=$wmpl_loc:$PYLIB

pth=$1
yr=${pth:0:4}
ym=${pth:0:6}
mth=${pth:4:2}

mkdir -p ${SRC}/logs >/dev/null 2>&1

${SRC}/orbits/reduceOrbit.sh $pth $2
res=$?
indir=${MATCHDIR}/$yr/$ym/$pth

if [[ "$2" == "recopy" && $res -eq 99  && ! -f $indir/notsolvable.txt ]] ; then
    res=0
fi 
if [ $res -eq 0 ] ; then
    outdir=${DATADIR}/orbits/$yr
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)

    echo "copying jpgs, videos and raw data"
    python $here/findJPGs.py $indir $resultdir
    cp $indir/*.txt $resultdir > /dev/null 2>&1
    cp $indir/*.jpg $resultdir > /dev/null 2>&1
    cp $indir/*.XML $resultdir > /dev/null 2>&1
    cp $indir/*.mp4 $resultdir > /dev/null 2>&1
    chmod 644 $resultdir/*.jpg

    ${SRC}/website/createPageIndex.sh ${MATCHDIR}/$yr/$ym/$pth/$(basename $resultdir)

    echo "copying the orbit CSV files"
    mkdir -p $outdir/csv/ >/dev/null 2>&1
    cp $resultdir/*orbit.csv $outdir/csv/
    mkdir -p $outdir/extracsv/ >/dev/null 2>&1
    cp $resultdir/*orbit_extras.csv $outdir/extracsv/    

    echo $(date +%Y%m%d-%H%M%S) $(basename $resultdir) >> ${SRC}/logs/success_list.txt
elif [ $res -eq 99 ] ; then
    echo "$1 skipped as already processed"
else
    echo "$1 was not solvable - probably not a true match"
    echo "not solvable" > $indir/notsolvable.txt
fi 

exit $res
