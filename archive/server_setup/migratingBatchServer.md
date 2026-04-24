# Replacing the UKMON helper server 
The ukmon helper server provides two services. 
* camera authentication and key management
* batch processing

# how to move batch processing
The best approach is to reinstall all the code using the ansible deployment scripts.
Both dev and prod envs should be created, though arguably the dev env should be on a separate server.
Additionally, WMPL will need to be reinstalled. 
After doing this, the additional UKMON python requirements can be added. 

The contents of ~/prod/data should be replicated to the new server. 
The contents of ~/keymgmt should be replicated to the new server. 

Finally, double check that all required SSM variables exist in the account holding the server. These
are used to build the config file, but originally were only in Mark McIntyre's account. 

## how to move accounts to a new server
The basic process is to extract the user accounts from the current server along with
group and password info, then import it back in on the new server. Its important to avoid 
accidentally overwriting system or otherwise-existing accounts on the new server. 

On most systems, accoutns below 500 are system accounts. Check though, as some AWS servers create
new accounts starting at 1000 and working both upwards and downwards! 

Steps in brief. NB must all be done as root, of course. 

### On the old server
``` bash
mkdir /root/move/
export UGIDLIMIT=500
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/passwd > /root/move/passwd.mig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/group > /root/move/group.mig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534) {print $1}' /etc/passwd | tee - |egrep -f - /etc/shadow > /root/move/shadow.mig
cp /etc/gshadow /root/move/gshadow.mig

# Also backup the user homedirs. In our case, they're all in /var/sftp
tar cvfz /root/move/varsftp.tar.gz /var/sftp
# now copy the files to target server, 
scp /root/move/* newserver:/tmp

```

### On the new server
In summary: backup the existing files, remove any accounts from the .mig files 
that are already present in the target, then append the filtered data. 

When comparing groups, remember new ids will get added to the sftp group. 


``` bash
mkdir -p /root/move/bkp
mv /tmp/*.mig /tmp/varsftp.tar.gz /root/move
cp /etc/passwd /etc/group /etc/shadow /etc/gshadow /root/move/bkp

cd /
tar -xvf /root/move/varsftp.tar.gz .

export UGIDLIMIT=500
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/passwd > /root/move/passwd.orig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534)' /etc/group > /root/move/group.orig
awk -v LIMIT=$UGIDLIMIT -F: '($3>=LIMIT) && ($3!=65534) {print $1}' /etc/passwd | tee - |egrep -f - /etc/shadow > /root/move/shadow.orig

cd /root/move
diff passwd.orig passwd.mig
diff shadow.orig shadow.mig
diff group.orig group.mig
```

# Other stuff
To install PyQt5 - needs at least 4GB memory so add 3GB swap
``` bash
sudo apt install qtbase5-dev qt5-qmake
pip install pyqt5
```