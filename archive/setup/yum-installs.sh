#!/bin/bash

sudo yum install -y automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel
sudo yum install -y ftp
sudo yum install -y gsl gsl-devel cairo-devel python3 ImageMagick gcc-c++ gcc-gfortran python3-devel blas lapack atlas-devel libgfortran 
sudo yum install -y dos2unix
sudo amazon-linux-extras install -y R3.4
sudo amazon-linux-extras install -y ansible2
sudo amazon-linux-extras install -y python3.8
sudo amazon-linux-extras install -y epel
sudo yum install -y s3fs-fuse
sudo yum install -y python38-devel
sudo yum install -y python3-tkinter
sudo yum install -y amazon-efs-utils

mkdir -P data/RMSCorrelate/trajectories

python3 -m pip install --user virtualenv
virtualenv -p python3.8 ~/venvs/wmpl
source ~/venvs/wmpl/bin/activate
pip install pytz
pip install shapely --no-binary shapely

cd ~/src
git clone --recursive https://github.com/wmpg/WesternMeteorPyLib.git
cd WesternMeteorPyLib
pip install -r requirements.txt
python setup.py install

echo "now edit wmpl/__init__.py and add GUI to the list of things to be ignored"

