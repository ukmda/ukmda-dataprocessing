#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre
#
# Create a report for the named shower and year or year+month
#
# Parameters
#   shower 3-letter code SSS
#   period to report on in yyyy or yyyymm format
#
# Consumes
#   All single-station and matched data from $DATADIR/single and $DATADIR/matched
#
# Produces
#   A report for the named shower, in $DATADIR/reports/yyyy/SSS
#   Which is then synced to the website

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
source $here/../config.ini >/dev/null 2>&1
source $HOME/venvs/${WMPL_ENV}/bin/activate

if [ $# -lt 2 ] ; then
	echo Usage: showerReport.sh GEM 2017
else
    logger -s -t showerReport "starting"
    shwr=$1
    dt=$2
    yr=${dt:0:4}
    mth=${dt:4:6}
    dy=${dt:6:8}
    logger -s -t showerReport "starting $shwr $dt"

    cd ${DATADIR}

    magval=999
    outdir=reports/$yr/$shwr
    if [ "$mth" != "" ] ; then
        outdir=$outdir/$mth
    fi 

    if [ "$dy" == "" ] ; then dy=01 ; fi
    
    if [ "$mth" == "" ] ; then 
        rmth=01 
        repdt=${yr}${rmth}${dy}
        python -m reports.reportActiveShowers -d $repdt -s $shwr
    else 
        rmth=$mth 
        repdt=${yr}${rmth}${dy}
        python -m reports.reportActiveShowers -d $repdt -s $shwr -t $mth
    fi

    cd $DATADIR/$outdir

    logger -s -t showerReport "copying files to website"
    aws s3 sync $DATADIR/$outdir $WEBSITEBUCKET/$outdir --quiet
    logger -s -t showerReport "all done"

    tstval=$(grep "$yr/$shwr" $DATADIR/reports/${yr}/reportindex.js)
    if [ "$tstval" == "" ] ; then 
        ${SRC}/website/createReportIndex.sh ${yr}
    fi
    logger -s -t showerReport "finished"    
fi 
