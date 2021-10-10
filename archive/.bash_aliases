# bash aliases
alias h='history'
alias df='df -h'
alias du='du -h'

alias data='cd $SRC/data && pwd'
alias logs='cd $SRC/logs && pwd'
alias matchdir='cd $MATCHDIR/RMSCorrelate && pwd'
alias arch='cd $ARCHDIR && pwd'

alias mltail='tail -f $(ls -1 $SRC/logs/matches/matc*.log | tail -1)'
alias njtail='tail -f $(ls -1 $SRC/logs/nigh*.log | tail -1)'

alias stats='tail $DATADIR/dailyreports/stats.txt'
alias bigserver='ssh 172.31.34.152'
