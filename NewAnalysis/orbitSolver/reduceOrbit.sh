#!/bin/bash
# bash script to reduce a folder of A.XML files using WMPL
#
here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the helper functions
source $here/orbitsolver.ini > /dev/null 2>&1
source ~/venvs/$WMPL_ENV/bin/activate
export PYTHONPATH=$wmpl_loc

pth=$1
yr=${pth:0:4}
ym=${pth:0:6}

outdir=$results/$yr/orbits/$ym
indir=$inputs/$yr/$ym/$pth
mkdir -p $here/logs >/dev/null 2>&1

cd $here
echo "converting $pth to RMS/CAMS format"
python UFOAtoFTPdetect.py $indir

numas=`ls -1 $indir/*A.XML $indir/data*.txt | wc -l`
if [ $numas -gt 1 ] ; then 
    # check if folder already processed, and if so skip recalculating
    force=0
    dontprocess=0
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)
    if [[ "$resultdir" != ""  &&  -d $resultdir ]] ; then
        # if there are the same number of input files as residual files then probably nothing changed
        s1=`ls -1 $resultdir/*spatial_resid* | egrep -v "all|total" | wc -l`
        s2=`ls -1 $indir/data*.txt $indir/*A.XML | wc -l`
        if [[ $s1 -eq $s2 && $force -eq 0 ]] ; then
            dontprocess=1
        fi
    fi
    if [ $dontprocess -eq 0 ] ; then
        echo "solving $1 to determine the path and the orbit"
        # arguments 
        #   -x save but don't display graphs, 
        #   -i image format eg jpg, png
        #   -l generate detailed plots of residuals
        #   -d disable monte carlo
        #   -r N execute N runs 
        #   -j show jaccia deceleration plots
        #   -t T max timing difference between stations
        #   -s solver (original or gural)

        python $here/ufoTrajSolver.py $indir/FTPdetectinfo_UFO.txt -x $plotallspatial -j -t $timing_offset $disablemc > $here/logs/$1.txt
        res=$?
        echo "done, result was $res"
    else
        echo 'Not reprocessing folder'
    fi 
    # check if the process generated any output
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)
    if [[ "$resultdir" != ""  &&  -d $resultdir ]] ; then
        targ=`basename "$resultdir"`
        fulltarg=$outdir/${targ}
        rm -f $fulltarg >/dev/null 2>&1
        mkdir -p $fulltarg >/dev/null 2>&1
        echo "copying output files from $resultdir to $fulltarg"
        cp -pr $resultdir/* $fulltarg

        ls -1 $indir/*.jpg > /dev/null 2>&1 
        if [ $? -eq 0 ] ; then 
            mv $indir/*.jpg $fulltarg  
            chmod 644 $fulltarg/*.jpg
        fi
        ls -1 $indir/*.mp4 > /dev/null 2>&1 
        if [ $? -eq 0 ] ; then 
            mv $indir/*.mp4 $fulltarg 
            chmod 644 $fulltarg/*.mp4
        fi
        cp $resultdir/*.csv $outdir/../csv/
        python $here/findJPGs.py $indir $fulltarg
        chmod 644 $fulltarg/*.jpg

        $here/createPageIndex.sh $targ
        $here/createMonthlyOrbitIndex.sh $ym
    else
        echo "$1 was not solvable - probably not a true match"
    fi
else
    echo "$1 contains only one A.XML file so not possible to solve"
fi 
