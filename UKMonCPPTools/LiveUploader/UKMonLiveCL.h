#pragma once
/*
Copyright 2018 Mark McIntyre.

UKMONLiveCL is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#define _WIN32_WINNT 0x0501

// disable warnings that I'm ignoring the return from getchar and strtok. I know...
#pragma warning( disable : 6031)

#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <ShlObj.h>
#include <string>
#include <iostream>
#include <fstream>
#include <ctime>
#include <iomanip>      // std::setprecision

#include <aws/core/Aws.h>
#include <aws/s3/S3Client.h>
#include <aws/s3/model/PutObjectRequest.h>
#include <aws/core/auth/AWSCredentialsProvider.h>

#include "../shared/PreprocessXML.h"
//#include "../shared/eventlog.h"
#include "version.h"

struct KeyData
{
	char AccountKey[128];
	char AccountName[128];
	char QueueEndPoint[128];
	char StorageEndPoint[128];
	char TableEndPoint[128];
	char BucketName[128];
	char AccountKey_D[128];
	char AccountName_D[128];
	char region[128];
};

extern struct KeyData theKeys;
extern char ProcessingPath[512];
extern char ffmpegPath[512];
extern int nCounter;
extern int maxretry;
extern int Debug;
extern int dryrun;
extern int delay_ms;
extern long framelimit;
extern long minbright;
extern long minframes;
extern double maxrms;
extern long minPxls;
extern int doFireballs;
extern Aws::Auth::AWSCredentials creds; // aws credentials
extern Aws::Client::ClientConfiguration clientConfig; // client setup

int LoadIniFiles(void);

int String2Hex(char* out, char* in);
int Hex2String(char* out, char* in);
int Encrypt(char *out, char* in, int Key);
int Decrypt(char *out, char* in, int Key);

#define XML 1
#define JPG 2
#define MP4 3

int put_file(char* buckname, const char* fname, long frcount, long maxbmax, double rms, int filetype);

int ProcessData(std::string pattern, long framelimit, long minbright, char *pth);


