#!/bin/bash

# script to extract the start/stop times of the Calculation Engine server from the logs
# I have a spreadsheet that consumes this and works out the cost for various models of server (c8g.2xlarge, c8g.4xlarge etc)

cd ~/prod/logs

csl=/tmp/calcserver_timings.txt
csl2=/tmp/csl.txt
[ -f $csl ] && rm $csl
touch $csl

ls -1tr nightly*.gz | while read i 
do
    mfz=matchJob${i:10:50}
    gunzip $i
    gunzip $mfz
    nf=$(basename $i .gz)
    mf=$(basename $mfz .gz)
    egrep "start correlation server|stop the server again|restarting server to|stopping calcserver again" $mf $nf >> $csl
    gzip $nf
    gzip $mf
done
ls -1tr nightlyJob* | grep -v gz | while read nf
do
    mf=matchJob${nf:10:50}
    egrep "start correlation server|stop the server again|restarting server to|stopping calcserver again" $mf $nf >> $csl
done
[ -f $csl2 ] && rm $csl2
touch $csl2
cat $csl | while read i 
do
    parta=$(echo $i | awk -F ">" '{print $2}')
    partb=$(echo $parta | awk -F " " '{printf("%s, %s, %s\n",$1,$2,$3)}')
    echo $partb >> $csl2
done
[ -f $csl ] && rm $csl
python  << EOD
lis = open('$csl2','r').readlines()
data = [x.strip().split(',') for x in lis]
currdt = None
results = []
res = []
col = 0
with open('/tmp/computeservertimes.csv','w') as outf:
    for i in range(len(data)):
        mth = data[i][0]
        dy = data[i][1]
        tim = data[i][2]
        dtstr = f'{mth} {dy}'
        if currdt is None:
            currdt = dtstr
        if currdt != dtstr:
            outf.write(','.join(res) + '\n')
            res = []
            col = 0
        if col == 0:
            res.append(dtstr)
            res.append(tim)
        else:
            res.append(tim)
        col += 1
        currdt = dtstr
    outf.write(','.join(res) + '\n')
EOD
[ -f $csl2 ] && rm $csl2
