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

To build this project you will need the AWS C++ SDK, Visual Studio 2015 or later and the relevant MSVC Runtime Libraries.

*/

#include "UKMonMonthlyArchiver.h"
#include <algorithm> 

#define BUFLEN 32768 // number of files I can read at one time
int nCounter;		 // number of events uploaded
int maxretry = 5;	 // number of retries 

std::ofstream errf;

wchar_t path[MAX_PATH] = { 0 };

int Debug = 0;
int dryrun = 0;
int overwrite = 0;
char y[5] = { 0 };
char m[7] = { 0 };
char d[9] = { 0 };
char cameraname[128] = { 0 };

struct datasets* DataSets;
int nSources;
int maxmonths;

static int FindAFile(char* inpath, const char* templ, int recursed, char* dest);

static int CALLBACK BrowseCallbackProc(HWND hwnd, UINT uMsg, LPARAM lParam, LPARAM lpData)
{

	if (uMsg == BFFM_INITIALIZED)
	{
		std::string tmp = (const char*)lpData;
		SendMessage(hwnd, BFFM_SETSELECTION, TRUE, lpData);
	}

	return 0;
}

int BrowseFolder(std::string saved_path)
{
	const char* path_param = saved_path.c_str();

	BROWSEINFO bi = { 0 };
	bi.lpszTitle = (L"Browse for folder...");
	bi.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE;
	bi.lpfn = BrowseCallbackProc;
	bi.lParam = (LPARAM)path_param;

	LPITEMIDLIST pidl = SHBrowseForFolder(&bi);

	if (pidl != 0)
	{
		//get the name of the folder and put it in path
		SHGetPathFromIDList(pidl, path);

		//free memory used
		IMalloc* imalloc = 0;
		if (SUCCEEDED(SHGetMalloc(&imalloc)))
		{
			imalloc->Free(pidl);
			imalloc->Release();
		}
		return 1;
	}
	return 0;
}
extern char inppth[260];

int main(int argc, char** argv)
{
	wchar_t msg[128] = { 0 };
	wchar_t msg2[128] = { 0 };
	wchar_t msg3[128] = { 0 };
	wchar_t msg4[128] = { 0 };
	char cam[64] = { 0 };

	for (int ac = 0; ac < argc; ac++)
	{
		if (!strcmp(argv[ac], "-dryrun")) dryrun = 1;
		if (!strcmp(argv[ac], "-debug")) Debug = 1;
	}

	wchar_t* logname = (wchar_t*)"UKMONMonthlyArchiver";
	theEventLog.Initialize(logname);
	if (LoadIniFiles() < 0)
		return -1;
	theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 0, L"Started", L"");

	std::time_t t = std::time(0);   // get time now
	std::tm* now = std::localtime(&t);
	int curryear = now->tm_year + 1900;
	int currmonth = now->tm_mon; // 0 = jan
	int startyear = curryear;
	int startmonth = currmonth - maxmonths;
	if (startmonth < 0)
	{
		startyear -= 1;
		startmonth += 13;
	}
	if (maxmonths == 0)
	{
		startyear = 2013;
		startmonth = 0;
	}
	char buffer[32] = { 0 };
	strftime(buffer, 32, "%Y-%m-%d %H:%M:%S", now);
	std::cout << buffer << " UKMON Archive File uploader starting" << std::endl;
	std::cout << "==============================================" << std::endl;
	if (Debug)
	{
		std::cout << "  Debugging is on" << std::endl;
		wsprintf(msg3, L"Debugging is on;");
	}
	if (dryrun)
	{
		std::cout << "  Dry run enabled - nothing will be uploaded" << std::endl;
		wsprintf(msg4, L"Dry run is on- nothing will be uploaded;");
	}
	std::cout << "  Scanning the last " << maxmonths << " months" << std::endl;

	for(int i = 0; i < nSources; i++)
	{
		strcpy(ProcessingPath, DataSets[i].source);
		std::cout << "  Checking: " << ProcessingPath << std::endl;
		wchar_t msg0[512];
		char msg0_s[512];
		sprintf(msg0_s, "Checking %s", ProcessingPath);
		mbstowcs(msg0, msg0_s, 512);

		theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 1, msg0, msg, msg2, msg3, msg4, L"");

		HANDLE hFind;
		WIN32_FIND_DATA file;
		wchar_t wbaseDir[512];
		char baseDir[512];

		int q = strlen(ProcessingPath);

		strcpy(baseDir, ProcessingPath);
		strcat(baseDir, "\\20*");
		mbstowcs(wbaseDir, baseDir, 512);
		hFind = FindFirstFile(wbaseDir, &file);
		do
		{
			if (hFind != INVALID_HANDLE_VALUE)
			{
				// if its a directory, assume we should check it (but not for . or .. )
				if (file.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY &&
					wcscmp(file.cFileName, L".") && wcscmp(file.cFileName, L".."))
				{
					char dirname_s[128] = { 0 };
					wcstombs(dirname_s, file.cFileName, wcslen(file.cFileName));
					int yr = atoi(dirname_s);
					if (yr >= startyear)
					{
						int m1, m2;
						if (yr == startyear)
							m1 = startmonth;
						else
							m1 = 0;
						if (yr != curryear)
							m2 = 12;
						else
							m2 = currmonth+1;

						// loop over all  possible months
						for (int mth = m1; mth < m2; mth++)
						{
							char fullpath[512] = { 0 };
							strncpy(y, dirname_s, 4);
							sprintf(m, "%4.4s%2.2d", y, mth + 1);
							sprintf(fullpath, "%s\\%s\\%s", ProcessingPath, y, m);
							std::cout << "Checking " << fullpath << std::endl;
							FindAFile(fullpath, "\\*", 0, DataSets[i].dest);
						}
					}
				}
			}
			else
			{
				std::cout << "Path " << baseDir << " not found?" << std::endl;
			}
		} while (FindNextFile(hFind, &file));
		FindClose(hFind);
	}
	theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 0, L"Done", L"");
	std::cout << "Done - press any key to close this window" << std::endl << "==============================================" << std::endl;
	getchar();
	return 0;
}


static int FindAFile(char* inpath, const char* templ, int recursed, char* dest)
{
	HANDLE hFind;
	WIN32_FIND_DATA file;
	wchar_t wbaseDir[512];
	char baseDir[512];

	strcpy(baseDir, inpath);
	strcat(baseDir, templ);
	mbstowcs(wbaseDir, baseDir, 512);
	if (Debug) std::cout << "Checking " << baseDir << std::endl;
	hFind = FindFirstFile(wbaseDir, &file);

	if (hFind != INVALID_HANDLE_VALUE) 
	{
		do {
			char filename_s[512] = { 0 };
			wcstombs(filename_s, file.cFileName, wcslen(file.cFileName));
			if (file.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)
			{
				if (wcscmp(file.cFileName, L".") && wcscmp(file.cFileName, L".."))
				{
					if (!strncmp(templ, "\\*", 3))
						strncpy(d, filename_s, 8);
					char newpath[512] = { 0 };
					strcpy(newpath, inpath);
					strcat(newpath, "\\");
					strcat(newpath, filename_s);

					FindAFile(newpath, "\\*.csv", 1, dest);
					FindAFile(newpath, "\\*.xml",1, dest);
					FindAFile(newpath, "\\*.txt",1, dest);
					FindAFile(newpath, "\\*p.jpg",1, dest);
					FindAFile(newpath, "\\*.gif", 1, dest);
				}
			}
			else
			{
				char fullname[512];
				char objname[512];
				if (recursed)
					sprintf(objname, "%s/%s/%s/%s/%s/%s", theKeys.ArchFolder, dest, y, m, d, filename_s);
				else
					sprintf(objname, "%s/%s/%s/%s/%s", theKeys.ArchFolder, dest, y, m, filename_s);
				sprintf(fullname, "%s\\%s", inpath, filename_s);

				put_file(theKeys.BucketName, objname, fullname, theKeys.region, theKeys.AccountName_D, theKeys.AccountKey_D);
			}
		} while (FindNextFile(hFind, &file));
		FindClose(hFind);
	}
	return 0;
}
