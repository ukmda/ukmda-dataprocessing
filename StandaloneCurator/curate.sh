# bash script to curate large amounts of data
# should also work on MacOS but not tested

if [ $# -lt 1 ] ; then
    echo usage: ./curate.sh /path/to/files
    echo ""
    echo eg ./curate.sh ~/ufodata/2020
    echo will curate all UFO files under ~/ufodata/2020
    exit
fi 

# source ~/venvs/ufoCurator/bin/activate
if [ ! -d ./logs ] ; then
    mkdir ./logs 
fi
pip install -r ./requirements.txt
python ./CurateUFO.py ./curation.ini $1 | tee ./logs/curate-`date +%Y%m%m_%H%M%s`.log

