# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi
# User specific aliases and functions
if [ -f ~/.bash_aliases ]; then
	. ~/.bash_aliases
fi

# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

function dev {
	source ~/dev/config/config.ini >/dev/null 2>&1 
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (dev) [\W]\$ "
	cd ~/dev
	export PYTHONPATH=$PYLIB:$wmpl_loc
}
function prd {
	source ~/prod/config/config.ini >/dev/null 2>&1
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (prd) [\W]\$ "
	cd ~/prod
	export PYTHONPATH=$PYLIB:$wmpl_loc
}
