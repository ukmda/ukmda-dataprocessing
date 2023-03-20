#!/bin/bash

######### RMS & Camera configuration - generic to all cameras
cp ~/RMS_data/config/.config ~/source/RMS
cp ~/RMS_data/config/platepar* ~/source/RMS
cp ~/RMS_data/config/mask.bmp ~/source/RMS
cp ~/RMS_data/config/.rmsautorunflag ~

mkdir ~/.ssh
chmod 0600 ~/.ssh
cp ~/RMS_data/config/.ssh/* ~/.ssh
chmod 0600 ~/.ssh/id_rsa
chmod 0644 ~/.ssh/id_rsa.pub

# Update RMS
cd ~/source/RMS
git stash
git pull
git stash apply
python setup.py install 
###### end of RMS and camera configuration

# create some bash aliases - handy if you have to investigate issues
#
touch ~/.bash_aliases
echo "alias h='history'" >> ~/.bash_aliases 
echo "alias du='du -h'" >> ~/.bash_aliases 
echo "alias df='df -h'" >> ~/.bash_aliases 
echo "alias src='cd ~/source/RMS && pwd'" >> ~/.bash_aliases 
echo "alias logs='cd ~/RMS_data/logs && pwd'" >> ~/.bash_aliases 
echo "alias cap='cd ~/RMS_data/CapturedFiles && pwd'" >> ~/.bash_aliases 
echo "alias arc='cd ~/RMS_data/ArchivedFiles && pwd'" >> ~/.bash_aliases 
source ~/.bash_aliases

# UKMON-specific configuration 
chmod 0600 ~/.ssh/ukmon 
chmod 0644 ~/.ssh/ukmon.pub
chmod 0600 ~/.ssh/mjmm-data.key
chmod 0600 ~/.ssh/known_hosts
cp ~/RMS_data/config/ukmon.ini ~/source/ukmon-pitools
if [ -f ~/RMS_data/config/domp4s ] ; then cp ~/RMS_data/config/domp4s ~/source/ukmon-pitools ; fi
if [ -f ~/RMS_data/config/dotimelapse ] ; then cp ~/RMS_data/config/dotimelapse ~/source/ukmon-pitools ; fi
cd ~/source/ukmon-pitools
./refreshTools.sh

# user-specific stuff, remove if not me!
mkdir ~/mjmm && cd ~/mjmm && git init
git remote add -f origin https://github.com/markmac99/pi-meteortools.git
git config core.sparseCheckout true
echo "pi/" >> .git/info/sparse-checkout && git pull origin master
chmod +x ~/mjmm/pi/*.sh
cp ~/RMS_data/config/config.ini ~/mjmm/pi

########## Finally, start RMS 
cd ~/source/RMS
Scripts/RMS_StartCapture.sh -r