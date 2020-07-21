#define _CRT_SECURE_NO_WARNINGS
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

#include "UKMonLiveCL.h"

struct KeyData theKeys = { 0,0,0,0,0,0,0,0,0};
char ProcessingPath[512];
char ErrFile[512];

#define INIFILENAME "UKMONLiveWatcher.ini"
#define AUTHFILENAME "AUTH_UKMONLiveWatcher.ini"

int LoadIniFiles(void)
{
	char szLocalPath[512];
	HRESULT hres = SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, szLocalPath);
	char inifile[512];
	char authfile[512];
	sprintf(inifile, "%s\\%s", szLocalPath, INIFILENAME);
	sprintf(authfile, "%s\\%s", szLocalPath, AUTHFILENAME);
	FILE *f = fopen(authfile, "r");
	if (!f)
	{
		std::cerr << "Unable to open security key file" << std::endl;
		//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Unable to open AUTH_UKMONLiveWatcher.ini; cannot continue", L"");
		return -1;
	}

	char s[512];
	fgets(s, 512, f); // ignore this line
	fgets(theKeys.AccountKey, 128, f); // account key encrypted and recoded in Hex 
	fgets(theKeys.AccountName, 128, f); // account name encrypted and recoded in Hex
	fgets(theKeys.QueueEndPoint, 128, f);
	fgets(theKeys.StorageEndPoint, 128, f);
	fgets(theKeys.TableEndPoint, 128, f);
	if (fgets(theKeys.BucketName, 128, f) == NULL)
	{
		//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Security key file malformed; cannot continue", L"");
		return -1;
	}

	theKeys.AccountKey[strcspn(theKeys.AccountKey, "\n")] = 0;
	theKeys.AccountName[strcspn(theKeys.AccountName, "\n")] = 0;
	theKeys.QueueEndPoint[strcspn(theKeys.QueueEndPoint, "\n")] = 0;
	theKeys.StorageEndPoint[strcspn(theKeys.StorageEndPoint, "\n")] = 0;
	theKeys.TableEndPoint[strcspn(theKeys.TableEndPoint, "\n")] = 0;
	theKeys.BucketName[strcspn(theKeys.BucketName, "\n")] = 0;

	Decrypt(theKeys.AccountName_D, theKeys.AccountName, 712); // hope this works! 
	Decrypt(theKeys.AccountKey_D, theKeys.AccountKey, 1207);
	char s3buck[128];
	strcpy(s3buck, theKeys.StorageEndPoint);
	strtok(s3buck, ".");
	strcpy(theKeys.region, &s3buck[3]);

	fclose(f);
	f = fopen(inifile, "r");
	if (!f)
	{
		//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Unable to open UKMONLiveWatcher.ini; cannot continue", L"");
		return -1;
	}
	fgets(s, 512, f); // ignore this line
	if (fgets(ProcessingPath, 512, f) == NULL) // location of files
	{
		std::cerr << "Ini file malformed" << std::endl;
		return -1;
	}

	ProcessingPath[strcspn(ProcessingPath, "\n")] = 0;
	char tmp[20];
	if (fgets(tmp, 20, f) != NULL)
		delay_ms = atoi(tmp);
	if (fgets(tmp, 20, f) != NULL)
	{
		framelimit = atol(tmp);
		if (framelimit == 0) framelimit = -1;
	}
	else
		framelimit = -1;

	if (fgets(tmp, 20, f) != NULL)
	{
		minbright = atol(tmp);
		if (minbright==0) minbright = -1;
	}
	else
		minbright = -1;

	if (fgets(tmp, 20, f) != NULL)
	{
		maxrms = atof(tmp);
		if (maxrms< 0.2) maxrms = 1.0;
	}
	else
		maxrms = 1.0;

	fclose(f);

	return 0;
}

int String2Hex(char* out, char* in)
{
	size_t i, j;
	for (i = 0, j = 0; i<strlen(in); i++, j += 2)
	{
		sprintf((char*)out + j, "%02X", in[i]);
	}
	out[j] = '\0'; /*adding NULL in the end*/
	return (int)strlen(out);
}

int Hex2String(char* out, char* in)
{
	size_t i, j;
	for (i = 0,j=0; i < strlen(in); i+=2,j++)
	{
		int c1 = in[i];
		int c2 = in[i + 1];
		c1 > '9' ? c1 -= '7' : c1 -= '0';
		c2 > '9' ? c2 -= '7' : c2 -= '0';
		int v = char(c1 * 16 + c2);
		out[j] = (char)v;
	}
	out[j] = 0;
	return (int)strlen(out);
}

int Decrypt(char *out, char* in, int Key)
{
	char tmp[512] = { 0 };
	Hex2String(tmp, in);
	for (size_t i = 0; i < strlen(tmp); i++)
		out[i] = tmp[i] ^ (Key >> 8);
	return (int)strlen(out);
}

int Encrypt(char *out, char* in, int Key)
{
	char tmp[512] = { 0 };
	for (size_t i = 0; i < strlen(in); i++)
		tmp[i] = in[i] ^ (Key >> 8);
	return String2Hex(out, tmp);
}
