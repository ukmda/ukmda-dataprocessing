# powershell script to run docker container

if [ $# -lt 2 ] ; then
    echo "usage: ./run.sh path/to/rmsdata"
    exit 1
fi
configloc=$1
hostname=$(basename $configloc)-dc
portno=$(cat ${configloc}/config/portno)
cp configure_container.sh $configloc/config
contid=$(docker run -h $hostname -v $configloc:/root/RMS_data -d -t -p $portno:22 rms_ubuntu)
echo $contid > ${configloc}/containerid.txt