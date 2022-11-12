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
sudo yum install libtiff-devel

mkdir -P data/RMSCorrelate/trajectories

python3 -m pip install --user virtualenv
virtualenv -p python3.8 ~/venvs/wmpl
source ~/venvs/wmpl/bin/activate
pip install pytz
pip install shapely --no-binary shapely

# might need to create a softlink for qmake, which is needed to install PyQt5
sudo ln -s /usr/bin/qmake-qt5 /usr/bin/qmake
pip install PyQt5

cd ~/src
git clone --recursive https://github.com/wmpg/WesternMeteorPyLib.git
cd WesternMeteorPyLib
pip install -r requirements.txt
python setup.py install
#rm -Rf wmpl/MetSim
#rm -Rf wmpl/CAMO

echo "now edit wmpl/__init__.py and add GUI to the list of things to be ignored"

pip install boto3
mkdir ~/src/ukmon_pylib
cd ~/src/ukmon_pylib
git init
git remote add -f origin https://github.com/markmac99/UKmon-shared.git
git config core.sparseCheckout true
echo "ukmon_pylib" > .git/info/sparse-checkout
git pull origin master

