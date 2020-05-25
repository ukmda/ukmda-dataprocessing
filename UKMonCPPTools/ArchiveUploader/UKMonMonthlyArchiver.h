#pragma once
/*
Copyright 2019 Mark McIntyre.

UKMON Monthly ARchiver is free software: you can redistribute it and/or modify
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

#include "EventLog.h"
#include <Windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <ShlObj.h>
#include <string>
#include <iostream>
#include <fstream>
#include <ctime>


struct KeyData
{
	char AccountKey[128];
	char AccountName[128];
	char BucketName[128];
	char AccountKey_D[128];
	char AccountName_D[128];
	char region[128];
	char ArchFolder[128];
};
extern struct KeyData theKeys;

struct datasets
{
	char source[128];
	char dest[128];
};
extern struct datasets* DataSets;
extern int nSources;
extern int maxmonths;

extern char ProcessingPath[512];
extern int nCounter;
extern int maxretry;
extern int Debug;
extern int dryrun;
extern int overwrite;

int LoadIniFiles(void);

int String2Hex(char* out, char* in);
int Hex2String(char* out, char* in);
int Encrypt(char *out, char* in, int Key);
int Decrypt(char *out, char* in, int Key);

int put_file(char* buckname, const char* objname, const char* fname, char* reg, char* acct, char* secret);




