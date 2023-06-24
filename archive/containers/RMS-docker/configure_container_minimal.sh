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

# finally run bash, so that the container remains alive 
bash 
