# .bashrc

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

function bigserver {
	source $SERVERAWSKEYS
	AWS_DEFAULT_REGION=eu-west-2
	privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
	ssh -i ~/.ssh/markskey.pem $privip
}