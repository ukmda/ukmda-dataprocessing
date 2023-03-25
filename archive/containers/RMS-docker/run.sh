# powershell script to run docker container

if [ "$1" ==  "" ] ; then
    echo "usage: ./run.sh path/to/rmsdata"
    exit 1
fi
configloc=$1
hostname=$(basename $configloc)-dc
portno=$(cat ${configloc}/config/portno)
cp configure_container.sh $configloc/config
contid=$(cat ${configloc}/containerid.txt)
contid=${contid:0:12} # linux container id is just the first 12 characters
if [ "$contid" != "" ] ; then 
    docker stop $contid
    docker rm $contid 
fi 
lastnight=$(ls $configloc/ArchivedFiles -1 | grep -v bz2 | tail -1)
if [ "$lastnight" != "" ] ; then
    cp -v $configloc/ArchivedFiles/$lastnight/platepar_cmn2010.cal $configloc/config
fi 

contid=$(docker run --name $hostname -h $hostname -v $configloc:/root/RMS_data -d -t -p $portno:22 rms_ubuntu)
echo $contid > ${configloc}/containerid.txt