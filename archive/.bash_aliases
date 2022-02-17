# bash aliases
alias h='history'
alias df='df -h'
alias du='du -h'

alias data='if [ "$SRC" == "" ] ; then echo select env first; else cd $SRC/data && pwd ; fi'
alias logs='if [ "$SRC" == "" ] ; then echo select env first; else cd $SRC/logs && pwd ; fi'
alias matchdir='if [ "$MATCHDIR" == "" ] ; then echo select env first; else cd $MATCHDIR/RMSCorrelate && pwd ; fi'
alias arch='if [ "$ARCHDIR" == "" ] ; then echo select env first; else cd $ARCHDIR && pwd ; fi'

alias tml='if [ "$SRC" == "" ] ; then echo select env first; else tail -f $(ls -1 $SRC/logs/matches-*.log | tail -1) ; fi'
alias tnj='if [ "$SRC" == "" ] ; then echo select env first; else tail -f $(ls -1 $SRC/logs/nigh*.log | tail -1) ; fi'

alias stats='if [ "$DATADIR" == "" ] ; then echo select env first; else tail $DATADIR/dailyreports/stats.txt ; fi'

alias matchstatus='if [ "$SRC" == "" ] ; then echo select env first; else grep "Running" $(ls -1 $SRC/logs/matches-*.log| tail -1 ) && grep TRAJ $(ls -1 $SRC/logs/matches-*.log | tail -1)|grep SOLVING && grep Observations: $(ls -1 $SRC/logs/matches-*.log | tail -1) | wc -l ; fi'
alias spacecalc='ls -1 | egrep -v "ukmon-shared" | while read i ; do \du -s $i ; done | sort -n'

function dev {
	source ~/dev/config/config.ini >/dev/null 2>&1 
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (dev) [\W]\$ "
	cd ~/dev
}
function prd {
	source ~/prod/config/config.ini >/dev/null 2>&1
	source ~/venvs/$WMPL_ENV/bin/activate
	PS1="(wmpl) (prd) [\W]\$ "
	cd ~/prod
}

function bigserver {
	source $SERVERAWSKEYS
	AWS_DEFAULT_REGION=eu-west-2
	privip=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text)
	ssh -i ~/.ssh/markskey.pem $privip
}