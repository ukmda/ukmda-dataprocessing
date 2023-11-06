#!/bin/bash
# Copyright (C) 2018-2023 Mark McIntyre

# updateFireballImage: switch the headline image for a fireball

# Parameters
#   short orbitname eg 20220331_035554 
#   image name eg FF_UK002F_20221115_223857_178_0510976.jpg
# 
# Consumes
#   fireball md file
#
# Produces
#   updated md file
#

here="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# load the configuration
source $here/../config.ini >/dev/null 2>&1
conda activate $HOME/miniconda3/envs/${WMPL_ENV}

export PYTHONPATH=$PYLIB

orbin=$1
imgname=$2
orbname=${orbin:0:15}
yr=${orbname:0:4}

if [[ "$orbname" == "" || "$imgname" == "" ]] ; then 
    echo "usage: ./updateFireballImage.sh orbname imgname"
    echo " eg ./updateFireballImage.sh 20220331_035554 FF_UK002F_20221115_223857_178_0510976.jpg"
    exit
fi
tmp_dir=$(mktemp -d -t fb-XXXXXXXXXX)
scp ukmonhelper2:prod/data/reports/${yr}/fireballs/${orbname}.md ${tmp_dir}
imgurl=$(grep image ${tmp_dir}/${orbname}.md | awk '{print $2}')
oldimg=$(basename $(echo $imgurl) )
cat  ${tmp_dir}/${orbname}.md  | sed "s/${oldimg}/${imgname}/g" > ${tmp_dir}/new_${orbname}.md
mv ${tmp_dir}/new_${orbname}.md ${tmp_dir}/${orbname}.md
scp ${tmp_dir}/${orbname}.md ukmonhelper2:prod/data/reports/${yr}/fireballs/
aws s3 cp ${tmp_dir}/${orbname}.md $WEBSITEBUCKET/reports/${yr}/fireballs/
rm -Rf ${tmp_dir}
${SRC}/website/createFireballPage.sh ${yr} -3.99