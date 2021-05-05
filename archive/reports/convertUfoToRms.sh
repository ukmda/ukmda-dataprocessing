#
# Convert a month's worth of UFO data to RMS format
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config/config.ini >/dev/null 2>&1

# get the date to operate for
if [ $# -eq 0 ]; then
    ym=$(date +%Y%m)
else
    ym=$1
fi
yr=${ym:0:4}

logger -s -t convertUfoToRms "starting"
cat $CAMINFO | while read li ; do 
    typ=$(echo $li | awk -F, '{printf("%s", $12)}') 

    if [ "${li:0:1}" != "#" ] ; then
        if [ ${typ:0:1} -eq 1 ] ; then 
            sitename=$(echo $li | awk -F, '{printf("%s", $1)}')
            camname=$(echo $li | awk -F, '{printf("%s", $2)}')
            dummyname=$(echo $li | awk -F, '{printf("%s", $13)}' | tr -d '\r')
            logger -s -t convertUfoToRms "processing $sitename $camname $dummyname"

            fpath="$ARCHDIR/$sitename/$camname/$yr/$ym"
            dest=$MATCHDIR/RMSCorrelate

            # if source month exists
            if compgen -G "$fpath/*" > /dev/null ; then 
                ls -1 "$fpath" | while read i
                do 
                    # if target folder exists, we already processed this day
                    if ! compgen -G "${dest}/${dummyname}/${dummyname}_${i}*" > /dev/null ; then 
                        # if the source is a folder, then process it
                        if [ -d "$fpath/$i" ] ; then 
                            logger -s -t convertUfoToRms "converting $i"
                            export PYTHONPATH=$PYLIB:$wmpl_loc
                            python $PYLIB/converters/UFOAtoFTPdetect.py "$fpath/$i" $dest 
                        fi
                    else   
                        logger -s -t convertUfoToRms "already processed $dest/$dummyname for $i"
                    fi 
                done
            fi
        fi
    fi
done
logger -s -t convertUfoToRms "finished"