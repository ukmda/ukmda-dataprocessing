# bash aliases
alias h='history'
alias df='df -h'
alias du='du -h'

alias data='cd $SRC/data && pwd'
alias logs='cd $SRC/logs && pwd'
alias matchdir='cd $MATCHDIR/RMSCorrelate && pwd'
alias arch='cd $ARCHDIR && pwd'

alias tml='tail -f $(ls -1 $SRC/logs/matches-*.log | tail -1)'
alias tnj='tail -f $(ls -1 $SRC/logs/nigh*.log | tail -1)'

alias stats='tail $DATADIR/dailyreports/stats.txt'

alias matchstatus='grep TRAJ $(ls -1 $SRC/logs/matches-*.log | tail -1)|grep SOLVING && grep Observations: $(ls -1 $SRC/logs/matches-*.log | tail -1) | wc -l '
