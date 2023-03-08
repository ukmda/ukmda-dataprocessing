# .bashrc
# Copyright (C) 2018-2023 Mark McIntyre

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi
# User specific aliases and functions
if [ -f ~/.bash_aliases ]; then
	. ~/.bash_aliases
fi

# prevent shell from escaping $ in variables when hitting tab
shopt -s direxpand

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# required for proj4 and libgeos 
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/geos/lib:/usr/local/proj4/lib
export PATH=$PATH:/usr/local/geos/bin:/usr/local/proj4/bin

if shopt -q login_shell ; then
 echo ""
 echo "Type 'dev' to activate the dev environment"
 echo "Type 'prd' to activate the dev environment"
 echo ""
 echo " Some handy aliases that work in either environment are"
 echo " logs => go to the logs folder"
 echo " data => go to the data folder"
 echo " matchstatus => check status of matching process today"
 echo " stats => display recent matching statistics"
 echo " tml => tail the matching process log"
 echo " tnj => tail the nightly job log"
 echo " spacecalc => display space usage in the current folder"
 echo ""
 prd
 matchstatus
fi