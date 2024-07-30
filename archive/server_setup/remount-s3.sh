#!/bin/bash
s3fs -o endpoint=eu-west-2 -o use_cache=/tmp -o uid=1000 -o mp_umask=002 -o multireq_max=5  mjmm-data /home/ec2-user/data -o url=https://s3-eu-west-2.amazonaws.com
#s3fs -o endpoint=eu-west-2 -o use_cache=/tmp -o uid=1000 -o mp_umask=002 -o multireq_max=5 -o passwd_file=~/.passwd-s3fs mjmm-data ./mjmm-data
s3fs -o endpoint=eu-west-2 -o use_cache=/tmp -o uid=1000 -o mp_umask=002 -o multireq_max=5 -o passwd_file=~/.passwd-ee-s3 ukmon-shared /home/ec2-user/ukmon-shared

