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
indir=$inputs/$yr/$ym/$1

cd $here
echo "converting $1 to RMS/CAMS format"
python UFOAtoFTPdetect.py $indir
numas=`ls -1 $indir/*A.XML | wc -l`
if [ $numas -gt 1 ] ; then 
    echo "solving $1 for the orbit"
    # arguments 
    #   -x save but don't display graphs, 
    #   -i image format eg jpg, png
    #   -l generate detailed plots of residuals
    #   -d disable monte carlo
    #   -r N execute N runs 
    #   -t T max timing difference between stations
    #   -s solver (original or gural)

    python ../WesternMeteorPyLib/wmpl/Formats/CAMS.py $indir/FTPdetectinfo_UFO.txt -x -l -t $timing_offset $disablemc > $indir/results.txt
    res=$?
    echo "done, result was $res"
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)

    if [[ "$resultdir" != ""  &&  -d $resultdir ]] ; then
        targ=`basename "$resultdir"`
        fulltarg=$outdir/${targ}
        rm -f $fulltarg >/dev/null 2>&1
        mkdir -p $fulltarg >/dev/null 2>&1
        echo "copying output files from $resultdir to $fulltarg"
        cp -pr $resultdir/* $fulltarg
        cp $indir/results.txt $fulltarg

        $here/createPageIndex.sh $targ
    else
        echo "$1 was not solvable - probably not a true match"
    fi
else
    echo "$1 contains only one A.XML file so not possible to solve"
fi 
