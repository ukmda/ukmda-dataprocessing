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

force=0
if [ $# -gt 1 ] ; then
    if [ "$2" == "-f" ] ; then 
        force=1
    fi
fi

outdir=$results/$yr/orbits/$ym
indir=$inputs/$yr/$ym/$pth
mkdir -p $here/logs >/dev/null 2>&1

cd $here

echo "checking $pth"
echo "-----------------------------------------------------"
numas=`ls -1 $indir/*A.XML $indir/data*.txt | wc -l`
if [ $numas -gt 1 ] ; then 

    # initial assumption is to reprocess every folder
    issumm=0
    nsolv=0
    dtachg=0
    if [ -f $indir/notsolvable.txt ] ; then
        # if already marked not solvable, avoid redoing it unless something changed
        echo "marked not solvable"
        nsolv=1
    fi
    # check if new data 
    resultdir=$(ls -1trd $indir/${yr}* | grep -v .txt | tail -1)
    if [[ "$resultdir" != ""  &&  -d $resultdir ]] ; then
        # if there's summary file, it has already been processed
        sfil=$(ls -1 $indir/${yr}*/summary.html )
        if [[ -f $sfil ]] ; then 
            echo "already solved"
            issumm=1
        else
            echo "not solved yet"
        fi 
        # if there are the same number of input files as residual files then probably nothing changed
        s1=$(ls -1 $resultdir/*spatial_resid* | egrep -v "all|total" | wc -l)
        s2=$(ls -1 $indir/data*.txt $indir/*A.XML | wc -l)
        if [ $s1 -ne $s2 ] ; then
            echo "input data changed"
            dtachg=1
        else
            echo "data unchanged"
        fi
    fi
    echo $nsolv $dtachg $issumm
    dontprocess=1
    if [ $nsolv -eq 1 ] ; then
        if [ $dtachg -eq 1 ] ; then
            dontprocess=0
        fi
    else
        if [ $dtachg -eq 1 ] ; then
            dontprocess=0
        else
            if [ $issumm -eq 0 ] ; then
                dontprocess=0
            fi 
        fi
    fi
    if [ $force -eq 1 ] ; then
        echo "forcing recalc"
    fi 
    if [[ $dontprocess -eq 0 || $force -eq 1 ]] ; then
        if [[ $resultdir != "" &&  -d $resultdir ]] ; then 
            echo "removing previous results"
            if [ -f $resultdir/*orbit.csv ] ; then 
                orbfile=$(basename $(ls -1 $resultdir/*orbit.csv))
                orbextras=$(basename $(ls -1 $resultdir/*orbit_extras.csv))
                rm -f $outdir/../csv/${orbfile}
                rm -f $outdir/../extracsv/${orbextras}
            fi 
            outbase=$(basename $resultdir)
            rm -Rf $resultdir 
            rm -Rf $outdir/$outbase
        fi

        echo "converting $pth to RMS/CAMS format"
        python $here/UFOAtoFTPdetect.py $indir

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

#        python $here/ufoTrajSolver.py $indir/FTPdetectinfo_UFO.txt -x $plotallspatial -j -t $timing_offset $disablemc | tee $here/logs/$1.txt
        python $here/ufoTrajSolver.py $indir/FTPdetectinfo_UFO.txt -x -l -j -t 5 -d 2>&1 | tee $here/logs/$1.txt
        res=$?
        echo "done, result was $res"
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
            mkdir $outdir/../csv/ >/dev/null 2>&1
            cp $resultdir/*orbit.csv $outdir/../csv/
            mkdir $outdir/../extracsv/ >/dev/null 2>&1
            cp $resultdir/*orbit_extras.csv $outdir/../extracsv/
            
            python $here/findJPGs.py $indir $fulltarg
            chmod 644 $fulltarg/*.jpg

            $here/createPageIndex.sh $targ
            $here/createMonthlyOrbitIndex.sh $ym
        else
            echo "$1 was not solvable - probably not a true match"
            echo "not solvable" > $indir/notsolvable.txt
        fi
    else
        echo 'Not reprocessing folder'
    fi 
else
    echo "$1 contains only one source file so not possible to solve"
fi 
