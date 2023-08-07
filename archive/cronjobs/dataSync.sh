#!/bin/bash

yr=$(date +%Y)
ym=$(date +%Y%m)
yd=$(date +%Y%m%d)
tod=$(date +%d)
pm=$(date -d '-1 day' +%Y%m)
pd=$(date -d '-1 day' +%Y%m%d)


# sync the images, mp4s and kmls
aws s3 sync s3://ukmeteornetworkarchive/img/single/${yr}/${ym}/  s3://ukmda-website/img/single/${yr}/${ym}/
aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${yr}/${ym}/  s3://ukmda-website/img/mp4/${yr}/${ym}/
aws s3 sync s3://ukmeteornetworkarchive/img/kmls/  s3://ukmda-website/img/kmls/

# and sync them the other way too so they're avalable on the main website
aws s3 sync s3://ukmda-website/img/single/${yr}/${ym}/ s3://ukmeteornetworkarchive/img/single/${yr}/${ym}/
aws s3 sync s3://ukmda-website/img/mp4/${yr}/${ym}/ s3://ukmeteornetworkarchive/img/mp4/${yr}/${ym}/  
aws s3 sync s3://ukmda-website/img/kmls/ s3://ukmeteornetworkarchive/img/kmls/  

if [ "$tod" == "01" ] ; then
    aws s3 sync s3://ukmeteornetworkarchive/img/single/${yr}/${pm}/  s3://ukmda-website/img/single/${yr}/${pm}/
    aws s3 sync s3://ukmeteornetworkarchive/img/mp4/${yr}/${pm}/  s3://ukmda-website/img/mp4/${yr}/${pm}/
    # no need to do kmls here

    aws s3 sync s3://ukmda-website/img/single/${yr}/${pm}/ s3://ukmeteornetworkarchive/img/single/${yr}/${pm}/  
    aws s3 sync s3://ukmda-website/img/mp4/${yr}/${pm}/ s3://ukmeteornetworkarchive/img/mp4/${yr}/${pm}/  
fi 

# sync the platepar.cal files and second set of kmls
aws s3 sync s3://ukmon-shared/consolidated/platepars/ s3://ukmda-shared/consolidated/platepars/
aws s3 sync s3://ukmon-shared/kmls/ s3://ukmda-shared/kmls/
aws s3 sync s3://ukmda-shared/consolidated/platepars/ s3://ukmon-shared/consolidated/platepars/ 
aws s3 sync s3://ukmda-shared/kmls/ s3://ukmon-shared/kmls/ 

# sync the solver data. Loop over locations and cams for scan efficiency
cams=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/ | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:")
for cam in $cams ; do 
    days=$(aws s3 ls s3://ukmon-shared/matches/RMSCorrelate/${cam} | grep PRE | awk '{print $2}' | egrep -v "daily|traj|plots|:" | grep $pd)
    if [ $? == 0 ]; then 
        aws s3 sync s3://ukmon-shared/matches/RMSCorrelate/${cam}${days} s3://ukmda-shared/matches/RMSCorrelate/${cam}${days}
    fi
done

# sync the other archive data. Loop over locations and cams for scan efficiency
locs=$(aws s3 ls s3://ukmon-shared/archive/ | awk '{print $2}')
for loc in $locs ; do 
    cams=$(aws s3 ls s3://ukmon-shared/archive/${loc} | awk '{print $2}')
    for cam in $cams ; do 
        aws s3 sync s3://ukmon-shared/archive/${loc}${cam}${yr}/${ym}/${yd} s3://ukmda-shared/archive/${loc}${cam}${yr}/${ym}/${yd}
        if [ "$tod" == "01" ] ; then
            aws s3 sync s3://ukmon-shared/archive/${loc}${cam}${yr}/${pm}/${pd} s3://ukmda-shared/archive/${loc}${cam}${yr}/${pm}/$pd} 
        fi 
    done
done

