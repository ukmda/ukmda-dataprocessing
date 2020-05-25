#define _CRT_SECURE_NO_WARNINGS
/*
Copyright 2019 Mark McIntyre.

UKMON Monthly Archiver is free software: you can redistribute it and/or modify
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

#include "UKMonMonthlyArchiver.h"

struct KeyData theKeys = { 0,0,0,0,0,0,0,0,0};
char ProcessingPath[512];
char ErrFile[512];
char inppth[260];

#define AUTHFILENAME "UKMONArchiver.ini"

int LoadIniFiles(void)
{
	char szLocalPath[512] = { 0 };
	char authfile[512] = { 0 };
	wchar_t wInifile[512] = { 0 };
	wchar_t wRetval[128] = { 0 };

	HRESULT hres = SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, szLocalPath);
	sprintf(authfile, "%s\\UKMON\\%s", szLocalPath, AUTHFILENAME);
	mbstowcs(wInifile, authfile, strlen(authfile));

	DWORD res;
	res = GetPrivateProfileString(L"awsconfig", L"key", NULL, wRetval, 128, wInifile);
	wcstombs(theKeys.AccountName, wRetval, wcslen(wRetval));
	res = GetPrivateProfileString(L"awsconfig", L"secret", NULL, wRetval, 128, wInifile);
	wcstombs(theKeys.AccountKey, wRetval, wcslen(wRetval));

	Decrypt(theKeys.AccountName_D, theKeys.AccountName, 712); // hope this works! 
	Decrypt(theKeys.AccountKey_D, theKeys.AccountKey, 1207);

	res = GetPrivateProfileString(L"awsconfig", L"bucket", NULL, wRetval, 128, wInifile);
	wcstombs(theKeys.BucketName, wRetval, wcslen(wRetval));
	res = GetPrivateProfileString(L"awsconfig", L"region", NULL, wRetval, 128, wInifile);
	wcstombs(theKeys.region, wRetval, wcslen(wRetval));
	res = GetPrivateProfileString(L"awsconfig", L"archfolder", NULL, wRetval, 128, wInifile);
	wcstombs(theKeys.ArchFolder, wRetval, wcslen(wRetval));

	nSources = GetPrivateProfileInt(L"cameras", L"cameras", 0, wInifile);
	maxmonths = GetPrivateProfileInt(L"general", L"maxmonths", 0, wInifile);
	int tmpdryrun = GetPrivateProfileInt(L"general", L"dryrun", 0, wInifile);
	if (tmpdryrun == 1)
		dryrun = 1;
	int tmpdebug = GetPrivateProfileInt(L"general", L"debug", 0, wInifile);
	if (tmpdebug == 1)
		Debug = 1;

	DataSets = (datasets*) calloc(nSources, sizeof(datasets));
	for (int i = 0; i<nSources; i++)
	{
		wchar_t key[10];
		wsprintf(key, L"%s%i", L"camera-", i+1);
		res = GetPrivateProfileString(key, L"src", NULL, wRetval, 128, wInifile);
		wcstombs(DataSets[i].source, wRetval, wcslen(wRetval));
		res = GetPrivateProfileString(key, L"dest", NULL, wRetval, 128, wInifile);
		wcstombs(DataSets[i].dest, wRetval, wcslen(wRetval));
	}

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
	return strlen(out);
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
	return strlen(out);
}

int Decrypt(char *out, char* in, int Key)
{
	char tmp[512] = { 0 };
	Hex2String(tmp, in);
	for (size_t i = 0; i < strlen(tmp); i++)
		out[i] = tmp[i] ^ (Key >> 8);
	return strlen(out);
}

int Encrypt(char *out, char* in, int Key)
{
	char tmp[512] = { 0 };
	for (size_t i = 0; i < strlen(in); i++)
		tmp[i] = in[i] ^ (Key >> 8);
	return String2Hex(out, tmp);
}
