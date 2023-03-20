#!/usr/bin/bash

# This script works for Ubuntu 20.04, but not Debian or Ubuntu 22.04
# note that Python 3.7 or 3.8 is required for RMS at present
sudo apt-get update
sudo apt-get -y upgrade

# must have SSH and net-tools installed, also recommend a useable VIM
sudo apt-get install -y ssh net-tools vim-gui-common vim-runtime

sudo apt-get install -y git mplayer python3 python3-dev python3-pip \
ffmpeg imagemagick python3-pyqt5 python3-venv vlc lxterminal

# install some platform-specific packages
if grep -Fq Debian /etc/issue; then
   	# ..might need to fix  for Bullseye..
   	sudo apt-get install -y python3-tk python3-pil libopencv-dev python3-opencv
   	wget http://ftp.br.debian.org/debian/pool/main/x/xcb-util/libxcb-util1_0.4.0-1+b1_amd64.deb
   	sudo dpkg -i libxcb-util1_0.4.0-1+b1_amd64.deb
   	rm -f libxcb-util1_0.4.0-1+b1_amd64.deb
	PYBIN=python3
elif grep -Fq 'Ubuntu 20.04' /etc/issue; then
	sudo apt-get install -y python3.8-tk libxslt-dev python-imaging-tk \
   		gnome-session-wayland libopencv-dev python3-opencv
	PYBIN=python3
elif grep -Fq 'Ubuntu 22.04' /etc/issue; then
  	sudo apt-get install -y python3-tk libxslt1-dev python3-pil
  	# install python3.8 to avoid issues with many libs
	sudo apt install dirmngr ca-certificates software-properties-common apt-transport-https -y
	sudo gpg --list-keys
	if [ ! -f /etc/apt/sources.list.d/python.list ] ; then 
		echo 'deb [signed-by=/usr/share/keyrings/deadsnakes.gpg trusted=yes] https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu jammy main' | sudo tee -a /etc/apt/sources.list.d/python.list
	fi 
	sudo apt update
	sudo apt install python3.8 python3.8-venv python3.8-dev python3.8-tk -y
	PYBIN=python3.8
fi

# dont overwrite the venv it already exists
if [ ! -d ~/vRMS ] ; then 
    $PYBIN -m venv ~/vRMS
fi

# activate the RMS virtualenv
source ~/vRMS/bin/activate
python -V

if [ ! -d ~/source ] ; then mkdir ~/source ; fi
cd ~/source

# dont try to re-clone RMS if its already there, just refresh it 
if [ ! -d RMS ] ; then 
   git clone https://github.com/markmac99/RMS.git
fi
cd ~/source/RMS
git stash 
git pull
git stash apply

pip install --upgrade pip setuptools

# use the requirements file to ensure we get everything required by the standard install
pip install -r requirements.txt

# needed for SkyFit2 to display graphical elements
pip install PyQt5

# no need to build openCV on Ubuntu or Debian if we pick the right version for the OS version
if grep -Fq Debian /etc/issue; then
	# yeah not worked this out yet - ideally use Python 3.8 on Debian
	pip install opencv_python==4.3.0.38
else
	pip install opencv_python==4.3.0.36
fi 

# now run the install script to build the Cython modules
cd ~/source/RMS
python setup.py install

# get CMNbinViewer....
cd ~/source
if [ ! -d cmn_binviewer ] ; then 
   git clone https://github.com/CroatianMeteorNetwork/cmn_binviewer.git
fi
cd ~/source/cmn_binviewer
git stash
git pull
git stash apply

# check to see if a desktop is installed - not foolproof - doesnt check for X11 env etc..
# needs work - simple links dont work on Ubuntu or Debian, they need to be desktop files
if [ -d "$HOME/Desktop" ] ; then 
  # generate desktop links
  cd ~/source/RMS/Scripts
  ./GenerateDesktopLinks.sh
fi

# configure bashrc so that its ready to use
if ! grep -Fq "vRMS/bin/activate" ~/.bashrc  ; then 
   echo "source ~/vRMS/bin/activate" >> ~/.bashrc 
   echo "cd ~/source/RMS" >> ~/.bashrc 
   echo "export QT_QPA_PLATFORM=xcb" >> ~/.bashrc 
fi

# create some bash aliases - might need alteration for multi-camera installs
#
if [ ! -f ~/.bash_aliases ] ; then
  touch ~/.bash_aliases
  echo "alias h='history'" >> ~/.bash_aliases 
  echo "alias du='du -h'" >> ~/.bash_aliases 
  echo "alias df='df -h'" >> ~/.bash_aliases 
  echo "alias src='cd ~/source/RMS && pwd'" >> ~/.bash_aliases 
  echo "alias logs='cd ~/RMS_data/logs && pwd'" >> ~/.bash_aliases 
  echo "alias cap='cd ~/RMS_data/CapturedFiles && pwd'" >> ~/.bash_aliases 
  echo "alias arc='cd ~/RMS_data/ArchivedFiles && pwd'" >> ~/.bash_aliases 
fi

# set sudo rules to allow passwordless sudo for the user
#
echo "$(whoami) ALL=(ALL:ALL) NOPASSWD:ALL" > /tmp/010_$(whoami)-nopasswd
sudo cp /tmp/010_$(whoami)-nopasswd /etc/sudoers.d/

# configure VIM for easier use
if [ ! -f ~/.vimrc ] ; then 
   touch ~/.vimrc
   echo "set nocompatible" >> ~/.vimrc
   echo "set mouse=" >> ~/.vimrc
   echo "syntax on" >> ~/.vimrc
fi

if [ ! -f ~/.config/autostart/rms.desktop ] ; then
	mkdir -p ~/.config/autostart > /dev/null 
	echo "[Desktop Entry]" > ~/.config/autostart/rms.desktop
	echo "Type=Application" >> ~/.config/autostart/rms.desktop
	echo "Exec=/usr/bin/lxterminal -e \"${HOME}/source/RMS/Scripts/RMS_FirstRun.sh\"" >> ~/.config/autostart/rms.desktop
	echo "Terminal=false" >> ~/.config/autostart/rms.desktop
	echo "Hidden=false" >> ~/.config/autostart/rms.desktop
	echo "NoDisplay=false" >> ~/.config/autostart/rms.desktop
	echo "X-GNOME-Autostart-enabled=true" >> ~/.config/autostart/rms.desktop
	echo "Name=RMS" >> ~/.config/autostart/rms.desktop
	echo "Comment=Run RMS in a window at startup" >> ~/.config/autostart/rms.desktop
fi 

