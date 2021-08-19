# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# User specific aliases and functions
alias h='history'
alias df='df -h'
alias du='du -h'
#source $HOME/src/config/config.ini > /dev/null 2>&1

function dev {
	source ~/dev/config/config.ini >/dev/null 2>&1 
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (dev) [\W]\$ "
	cd ~/dev
	alias logs='cd ~/dev/logs'
	export PYTHONPATH=$PYLIB:$wmpl_loc
}
function prd {
	source ~/prod/config/config.ini >/dev/null 2>&1
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (prd) [\W]\$ "
	cd ~/prod
	alias logs='cd ~/prod/logs'
	export PYTHONPATH=$PYLIB:$wmpl_loc
}
