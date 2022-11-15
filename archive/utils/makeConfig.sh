#!/bin/bash

if [[ "$1" != "PROD" && "$1" != "DEV" ]] ; then
    echo "must provide runtime env of PROD or DEV"
    exit -1
fi 
RUNTIME_ENV=$1
envname=$(echo $RUNTIME_ENV | tr '[:upper:]' '[:lower:]')

# read from AWS SSM Parameterset
SRC=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_srcdir --query Parameters[0].Value  | tr -d '"')
ARCHDIR=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_archdir --query Parameters[0].Value  | tr -d '"')
MATCHDIR=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_matchdir --query Parameters[0].Value  | tr -d '"')
SITEURL=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_siteurl --query Parameters[0].Value  | tr -d '"')
WEBSITEBUCKET=s3://$(aws ssm get-parameters --region eu-west-2 --names ${envname}_websitebucket --query Parameters[0].Value  | tr -d '"')
UKMONSHAREDBUCKET=s3://$(aws ssm get-parameters --region eu-west-2 --names ${envname}_sharedbucket --query Parameters[0].Value  | tr -d '"')
UKMONLIVEBUCKET=s3://$(aws ssm get-parameters --region eu-west-2 --names ${envname}_livebucket --query Parameters[0].Value  | tr -d '"')
RMS_LOC=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_rmshome --query Parameters[0].Value  | tr -d '"')
WMPL_LOC=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_wmplhome --query Parameters[0].Value  | tr -d '"')
SERVERINSTANCEID=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_calcinstance --query Parameters[0].Value  | tr -d '"')
BKPINSTANCEID=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_backupinstance --query Parameters[0].Value  | tr -d '"')
SERVERSSHKEY=$(aws ssm get-parameters --region eu-west-2 --names ${envname}_sshkey --query Parameters[0].Value  | tr -d '"')

# hardcoded
PYLIB=$SRC/ukmon_pylib
TEMPLATES=$SRC/website/templates
RCODEDIR=$SRC/R
DATADIR=$SRC/data
AWS_DEFAULT_REGION=eu-west-2
MATCHSTART=2
MATCHEND=0
RMS_ENV=RMS
WMPL_ENV=wmpl
APIKEY=$(cat ~/.ssh/gmapsapikey)
KMLTEMPLATE=*70km.kml

# create the config file
now=$(date +%Y-%m-%d-%H:%M:%S)
CFGFILE=~/${envname}/config.ini

echo "# Config last updated ${now}" > ${CFGFILE}
echo "RUNTIME_ENV=${RUNTIME_ENV}" >> ${CFGFILE}
echo "SRC=${SRC}" >> ${CFGFILE}
echo "ARCHDIR=${ARCHDIR}" >> ${CFGFILE}
echo "MATCHDIR=${MATCHDIR}" >> ${CFGFILE}
echo "SITEURL=${SITEURL}" >> ${CFGFILE}
echo "WEBSITEBUCKET=${WEBSITEBUCKET}" >> ${CFGFILE}
echo "UKMONSHAREDBUCKET=${UKMONSHAREDBUCKET}" >> ${CFGFILE}
echo "UKMONLIVEBUCKET=${UKMONLIVEBUCKET}" >> ${CFGFILE}
echo "PYLIB=${PYLIB}" >> ${CFGFILE}
echo "TEMPLATES=${TEMPLATES}" >> ${CFGFILE}
echo "RCODEDIR=${RCODEDIR}" >> ${CFGFILE}
echo "DATADIR=${DATADIR}" >> ${CFGFILE}
echo "SERVERINSTANCEID=${SERVERINSTANCEID}" >> ${CFGFILE}
echo "BKPINSTANCEID=${BKPINSTANCEID}" >> ${CFGFILE}
echo "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" >> ${CFGFILE}
echo "RMS_ENV=${RMS_ENV}" >> ${CFGFILE}
echo "WMPL_ENV=${WMPL_ENV}" >> ${CFGFILE}
echo "RMS_LOC=${RMS_LOC}" >> ${CFGFILE}
echo "WMPL_LOC=${WMPL_LOC}" >> ${CFGFILE}
echo "MATCHSTART=${MATCHSTART}" >> ${CFGFILE}
echo "MATCHEND=${MATCHEND}" >> ${CFGFILE}
echo "SERVERSSHKEY=${SERVERSSHKEY}" >> ${CFGFILE}
echo "APIKEY=${APIKEY}" >> ${CFGFILE}
echo "KMLTEMPLATE=${KMLTEMPLATE}" >> ${CFGFILE}
echo "" >> ${CFGFILE}
echo "export RUNTIME_ENV SRC ARCHDIR MATCHDIR SITEURL" >> ${CFGFILE}
echo "export WEBSITEBUCKET UKMONSHAREDBUCKET UKMONSHAREDBUCKET" >> ${CFGFILE}
echo "export PYLIB TEMPLATES RCODEDIR DATADIR BKPINSTANCEID AWS_DEFAULT_REGION" >> ${CFGFILE}
echo "export RMS_ENV RMS_LOC WMPL_ENV WMPL_LOC" >> ${CFGFILE}
echo "export PYTHONPATH=${RMS_LOC}:${WMPL_LOC}:${PYLIB}:${SRC}/share" >> ${CFGFILE}
echo "export MATCHSTART MATCHEND SERVERSSHKEY" >> ${CFGFILE}
echo "export APIKEY KMLTEMPLATE SERVERINSTANCEID" >> ${CFGFILE}
echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/usr/local/geos/lib:/usr/local/proj4/lib" >> ${CFGFILE}
