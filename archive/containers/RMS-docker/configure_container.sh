#!/bin/bash
# Copyright (C) Mark McIntyre

######## Start SSHD so we can login remotely ##########
/usr/sbin/sshd -D -o ListenAddress=0.0.0.0 & 

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
chmod 0600 ~/.ssh/known_hosts

# Update RMS
cd ~/source/RMS
git stash
git pull
git stash apply
python setup.py install 
###### end of RMS and camera configuration

######### create some bash aliases - handy if you have to investigate issues
touch ~/.bash_aliases
echo "alias h='history'" >> ~/.bash_aliases 
echo "alias du='du -h'" >> ~/.bash_aliases 
echo "alias df='df -h'" >> ~/.bash_aliases 
echo "alias src='cd ~/source/RMS && pwd'" >> ~/.bash_aliases 
echo "alias logs='cd ~/RMS_data/logs && pwd'" >> ~/.bash_aliases 
echo "alias cap='cd ~/RMS_data/CapturedFiles && pwd'" >> ~/.bash_aliases 
echo "alias arc='cd ~/RMS_data/ArchivedFiles && pwd'" >> ~/.bash_aliases 
source ~/.bash_aliases
######### end of generic configuration

######### UKMON-specific configuration 
cd ~/source
git clone https://github.com/markmac99/ukmon-pitools.git
cd ~/source/ukmon-pitools
./refreshTools.sh
chmod 0600 ~/.ssh/ukmon 
chmod 0644 ~/.ssh/ukmon.pub
cp ~/RMS_data/config/ukmon.ini ~/source/ukmon-pitools
./refreshTools.sh
if [ -f ~/RMS_data/config/domp4s ] ; then cp ~/RMS_data/config/domp4s ~/source/ukmon-pitools ; fi
if [ -f ~/RMS_data/config/dotimelapse ] ; then cp ~/RMS_data/config/dotimelapse ~/source/ukmon-pitools ; fi

######### user-specific stuff, remove if not me!
chmod 0600 ~/.ssh/pikey
chmod 0644 ~/.ssh/pikey.pub
chmod 0600 ~/.ssh/mjmm-data.key
mkdir ~/mjmm && cd ~/mjmm && git init
git remote add -f origin https://github.com/markmac99/pi-meteortools.git
git config core.sparseCheckout true
echo "pi/" >> .git/info/sparse-checkout && git pull origin master
chmod +x ~/mjmm/pi/*.sh
cp ~/RMS_data/config/config.ini ~/mjmm/pi
cp ~/RMS_data/config/token.pickle ~/mjmm/pi
cd ~/mjmm/pi && pip install -r requirements.txt
echo "/root/mjmm/pi/dailyPostProc.py" > ~/source/ukmon-pitools/extrascript
echo "1" > ~/mjmm/pi/doistream

########## Finally, start RMS and the UKMON live monitor
# do not use -r parameter as it'll restart in last night's folder
cd ~/source/RMS
Scripts/RMS_StartCapture.sh & 
# wait long enough to allow RMS to start fully before starting ukmon-live 
sleep 120  
~/source/ukmon-pitools/liveMonitor.sh & 
# finally run bash, so that the container remains alive 
bash 
