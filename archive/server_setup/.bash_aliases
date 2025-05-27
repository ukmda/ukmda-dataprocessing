# bash aliases
# Copyright (C) 2018-2023 Mark McIntyre

alias h='history'
alias df='df -h'
alias du='du -h'

alias data='if [ "$SRC" == "" ] ; then echo select env first; else cd $SRC/data && pwd ; fi'
alias logs='if [ "$SRC" == "" ] ; then echo select env first; else cd $SRC/logs && pwd ; fi'

alias tml='if [ "$SRC" == "" ] ; then echo select env first; else tail -f $(ls -1 $SRC/logs/matchJob.log | tail -1) ; fi'
alias tnj='if [ "$SRC" == "" ] ; then echo select env first; else tail -f $(ls -1 $SRC/logs/nightlyJob.log | tail -1) ; fi'

alias stats='if [ "$DATADIR" == "" ] ; then echo select env first; else tail $DATADIR/dailyreports/stats.txt ; fi'

alias matchstatus='if [ "$SRC" == "" ] ; then echo select env first; else grep "Running" $SRC/logs/matchJob.log && grep TRAJ $SRC/logs/matchJob.log | grep SOLVING && echo -n "Completed " && grep Observations: $SRC/logs/matchJob.log | wc -l &&  grep "nightlyJob" $SRC/logs/nightlyJob.log ; fi '
alias spacecalc='ls -1 | egrep -v "ukmon-shared" | while read i ; do \du -s $i ; done | sort -n'

alias startcalc='~/prod/utils/stopstart-calcengine.sh start'
alias stopcalc='~/prod/utils/stopstart-calcengine.sh stop'

function dev {
	source ~/dev/config.ini >/dev/null
	conda activate $HOME/miniconda3/envs/${WMPL_ENV}
	PS1="(wmpl) (dev) [\W]\$ "
	cd ~/dev
}
function prd {
	source ~/prod/config.ini >/dev/null
	conda activate $HOME/miniconda3/envs/${WMPL_ENV}
	PS1="(wmpl) (prd) [\W]\$ "
	cd ~/prod
}

function calcserver { 
	sts=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].State --output text --profile ukmonshared)
	ipaddr=$(aws ec2 describe-instances --instance-ids $SERVERINSTANCEID --query Reservations[*].Instances[*].PrivateIpAddress --output text --profile ukmonshared)
	isrunning=$(echo $sts | cut -d " " -f 1)
	if [ $isrunning -ne 16 ] ; then
		/home/ec2-user/prod/utils/stopstart-calcengine.sh start
		echo "starting server on ${ipaddr}... waiting 10s..."
		sleep 10
	fi 
	ssh -i ~/.ssh/markskey.pem ec2-user@$ipaddr
}
