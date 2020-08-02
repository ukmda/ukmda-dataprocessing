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
char ffmpegPath[512]= {"C:\\Program Files (x86)\\ukmonlive\\ffmpeg.exe"};

#define INIFILENAME "UKMONLiveWatcher.ini"
#define AUTHFILENAME "AUTH_UKMONLiveWatcher.ini"
#define NEWAUTHFILENAME "UKMONArchiver.ini"

int LoadIniFiles(void)
{
	char inifile[512];
	char authfile[512];
	char szLocalPath[512];
	wchar_t wInifile[512] = { 0 };
	wchar_t wRetVal[128] = { 0 };

	HRESULT hres = SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, SHGFP_TYPE_CURRENT, szLocalPath);
	sprintf(authfile, "%s\\UKMON\\%s", szLocalPath, NEWAUTHFILENAME);
	mbstowcs(wInifile, authfile, strlen(authfile));
	DWORD res;
	res = GetPrivateProfileString(L"liveaws", L"key", NULL, wRetVal, 128, wInifile);
	if (res == 0)
	{
		sprintf(inifile, "%s\\%s", szLocalPath, INIFILENAME);
		sprintf(authfile, "%s\\%s", szLocalPath, AUTHFILENAME);
		FILE* f = fopen(authfile, "r");
		if (!f)
		{
			WritePrivateProfileString(L"liveaws", L"Key", L"43494B43313458584549464A555334574B575741", wInifile);
			WritePrivateProfileString(L"liveaws", L"Secret", L"713674424F333D613C335E4E454C434D6C426C616031456F534030367332323C354F714F3C6C636B", wInifile);
			WritePrivateProfileString(L"liveaws", L"Bucket", L"ukmon-live", wInifile);
			WritePrivateProfileString(L"liveaws", L"Region", L"eu-west-1", wInifile);

			WritePrivateProfileString(L"live", L"ProcessingPath", L"c:\\ukmon", wInifile);
			WritePrivateProfileString(L"live", L"FrameLimit", L"135", wInifile);
			WritePrivateProfileString(L"live", L"MinBright", L"66", wInifile);
			WritePrivateProfileString(L"live", L"MaxRMS", L"1.5", wInifile);

			WritePrivateProfileString(L"fireball", L"DoFireballs", L"1", wInifile);
			WritePrivateProfileString(L"fireball", L"MinPxls", L"200", wInifile);
			WritePrivateProfileString(L"fireball", L"FFMpeg", L"C:\\Program Files (x86)\\ukmonlive\\ffmpeg.exe", wInifile);
		}
		else
		{
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
				if (minbright == 0) minbright = -1;
			}
			else
				minbright = -1;
			maxrms = 1.5;
			if (fgets(tmp, 20, f) != NULL)
			{
				maxrms = atof(tmp);
			}
			if (maxrms < 1.0) maxrms = 1.5;

			fclose(f);
			// now write the keys back to the new file
			wchar_t an[512] = {};
			mbstowcs(an, theKeys.AccountName, strlen(theKeys.AccountName));
			WritePrivateProfileString(L"liveaws", L"Key", an, wInifile);
			wchar_t ak[512] = {};
			mbstowcs(ak, theKeys.AccountKey, strlen(theKeys.AccountKey));
			WritePrivateProfileString(L"liveaws", L"Secret", ak, wInifile);
			wchar_t bn[512] = {};
			mbstowcs(bn, theKeys.BucketName, strlen(theKeys.BucketName));
			WritePrivateProfileString(L"liveaws", L"Bucket", bn, wInifile);
			WritePrivateProfileString(L"liveaws", L"Region", L"eu-west-1", wInifile);

			wchar_t pp[512] = {};
			mbstowcs(pp, ProcessingPath, strlen(ProcessingPath));
			WritePrivateProfileString(L"live", L"ProcessingPath", pp, wInifile);
			wchar_t wtmp[256] = { 0 };
			wsprintf(wtmp, L"%d\0", framelimit);
			WritePrivateProfileString(L"live", L"FrameLimit", wtmp, wInifile);
			wsprintf(wtmp, L"%d\0", minbright);
			WritePrivateProfileString(L"live", L"MinBright", wtmp, wInifile);
			WritePrivateProfileString(L"live", L"MaxRMS", L"1.5", wInifile);

			wsprintf(wtmp, L"%d\0", doFireballs);
			WritePrivateProfileString(L"fireball", L"DoFireballs", wtmp, wInifile);
			WritePrivateProfileString(L"fireball", L"MinPxls", L"200", wInifile);
			mbstowcs(wtmp, ffmpegPath, strlen(ffmpegPath));
			WritePrivateProfileString(L"fireball", L"FFMpeg", wtmp, wInifile);
			// now remove the old config files
			printf("Merged config into %%APPDATA%%\\local\\ukmon\\ukmonarchiver.ini\n");
			remove(inifile);
			remove(authfile);
		}
	}
	res = GetPrivateProfileString(L"liveaws", L"Key", NULL, wRetVal, 128, wInifile);
	wcstombs(theKeys.AccountName, wRetVal, wcslen(wRetVal));
	res = GetPrivateProfileString(L"liveaws", L"Secret", NULL, wRetVal, 128, wInifile);
	wcstombs(theKeys.AccountKey, wRetVal, wcslen(wRetVal));
	Decrypt(theKeys.AccountName_D, theKeys.AccountName, 712); // hope this works! 
	Decrypt(theKeys.AccountKey_D, theKeys.AccountKey, 1207);

	res = GetPrivateProfileString(L"liveaws", L"Bucket", NULL, wRetVal, 128, wInifile);
	wcstombs(theKeys.BucketName, wRetVal, wcslen(wRetVal));
	res = GetPrivateProfileString(L"liveaws", L"Region", NULL, wRetVal, 128, wInifile);
	wcstombs(theKeys.region, wRetVal, wcslen(wRetVal));

	res = GetPrivateProfileString(L"live", L"ProcessingPath", NULL, wRetVal, 128, wInifile);
	wcstombs(ProcessingPath, wRetVal, wcslen(wRetVal));
	framelimit=GetPrivateProfileInt(L"live", L"FrameLimit", 135, wInifile);
	minbright = GetPrivateProfileInt(L"live", L"MinBright", 60, wInifile);

	res = GetPrivateProfileString(L"live", L"MaxRMS", NULL, wRetVal, 128, wInifile);
	maxrms = _wtof(wRetVal);
	if (maxrms < 1.0) maxrms = 1.5;

	doFireballs = GetPrivateProfileInt(L"fireball", L"DoFireballs", 1, wInifile);
	minPxls = GetPrivateProfileInt(L"fireball", L"MinPxls", 200, wInifile);
	res = GetPrivateProfileString(L"fireball", L"FFMpeg", L"C:\\Program Files (x86)\\ukmonlive\\ffmpeg.exe", wRetVal, 128, wInifile);
	wcstombs(ffmpegPath, wRetVal, wcslen(wRetVal));

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
