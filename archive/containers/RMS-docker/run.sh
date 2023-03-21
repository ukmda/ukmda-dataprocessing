# powershell script to run docker container

if [ $# -lt 2 ] ; then
    echo "usage: ./run.sh path/to/rmsdata"
    exit 1
fi
configloc=$1
contid=$(docker run -v ${configloc}:/root/RMS_data -d -t rms_ubuntu)
echo $contid > ${configloc}/containerid.txt