#!/bin/bash

# NB to change the hostname
# 1) add preserve_hostname: true to the end of /etc/cloud/cloud.cfg
# 2) sudo hostnamectl set-hostname ukmonhelper2


# basic requirements for building / running WMPL and RMS and stuff
sudo yum install -y automake fuse fuse-devel gcc-c++ git libcurl-devel libxml2-devel make openssl-devel
sudo yum install -y ftp
sudo yum install -y gsl gsl-devel cairo-devel python3 ImageMagick gcc-c++ gcc-gfortran python3-devel blas lapack atlas-devel libgfortran 
sudo yum install -y dos2unix

#sudo amazon-linux-extras install -y R3.4
sudo amazon-linux-extras install -y ansible2
sudo amazon-linux-extras install -y python3.8
sudo amazon-linux-extras install -y epel
#sudo yum install -y s3fs-fuse

sudo yum install -y python3-pip python38-devel python3-tkinter
sudo yum install -y amazon-efs-utils
sudo yum install -y libtiff-devel

# install GEOS 
sudo yum search geos
sudo yum install -y geos geos-devel

# install node for compatability with Amazon's cloud9 dev env
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
nvm install  v16.20.1

# install miniconda so we can use conda virtualenvs - more flexible than basic python ones
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh > miniconda.sh
chmod +x ./miniconda.sh && ./miniconda.sh -b

conda create -n wmpl python=3.8
conda activate wmpl
conda install -y shapely geos proj pytz cartopy

# create a swap file
if [ ! -f /var/swap.1 ] ; then 
    sudo /bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=4096
    sudo /sbin/mkswap /var/swap.1
    sudo chmod 600 /var/swap.1
    sudo /sbin/swapon /var/swap.1
    cp /etc/fstab /tmp/fstab
    echo "/var/swap.1   swap    swap    defaults        0   0" >> /tmp/fstab
    sudo cp /tmp/fstab /etc
fi

if [ $(uname -i) != 'aarch64' ] ; then 
    # need to install/build QT5 and then create a softlink for qmake, which is needed to install PyQt5
    mkdir ~/src && cd ~/src
    git clone https://code.qt.io/qt/qtbase.git
    cd qtbase
    git checkout 5.15
    sudo yum -y install perl
    ./configure
    gmake
    sudo gmake install
    sudo ln -s $HOME/src/qtbase/bin/qmake /usr/bin/qmake
    pip install PyQt5
else
    echo QT and PyQt5 not available currently for aarch64
fi

cd ~/src
git clone --recursive https://github.com/markmac99/WesternMeteorPyLib.git
cd WesternMeteorPyLib
pip install -r requirements.txt
python setup.py install
#rm -Rf wmpl/MetSim
#rm -Rf wmpl/CAMO

echo "now edit wmpl/__init__.py and add GUI to the list of things to be ignored"

pip install boto3 gmplot cryptography

# not required on the batch server
mkdir ~/src/ukmon_pylib
cd ~/src/ukmon_pylib
git init
git remote add -f origin https://github.com/markmac99/UKmon-shared.git
git config core.sparseCheckout true
echo "ukmon_pylib" > .git/info/sparse-checkout
git pull origin master

