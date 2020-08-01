#define _CRT_SECURE_NO_WARNINGS
/*
Copyright 2018-2020 Mark McIntyre.

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

To build this project you will need the AWS C++ SDK, Visual Studio 2015 or later and the relevant MSVC Runtime Libraries.

*/

#include "UKMonLiveCL.h"

#define BUFLEN 32768 // number of files I can read at one time
int nCounter;		 // number of events uploaded
int maxretry = 5;	 // number of retries 
int delay_ms=1000;	 // retry delay if the jpg isn't present or the upload fails
long framelimit=120; // max number of frames before we consider it to be an aircraft or bird
long minframes = 66; // software records 30 frames either side of event
long minbright=60;	 // min brightness to be too dim to bother uploading
double maxrms = 2.0; // max error in the LSQ fit before the data is discarded. Meteors are usually < 1.0 !
long minPxls = 200;	 // min pixelcount for an interesting event

std::ofstream errf;

int Debug = 0;
int dryrun = 0;

int main(int argc, char** argv)
{
	wchar_t msg[512] = {0};
	wchar_t msg2[512] = {0};
	wchar_t msg3[512] = {0};
	wchar_t msg4[512] = {0};

	Aws::SDKOptions options;
	Aws::InitAPI(options);

	if (argc > 1 && argv[1][0] == 'D')
		Debug = 1;
	if (argc > 1 && argv[1][0] == 'T')
	{
		Debug = 1;
		dryrun = 1;
	}
	const wchar_t* ptr = L"UKMonLiveCL";
	//theEventLog.Initialize(ptr);
	if (LoadIniFiles() < 0)
		return -1;
	//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 0, L"Started", L"");

	creds.SetAWSAccessKeyId(theKeys.AccountName_D);
	creds.SetAWSSecretKey(theKeys.AccountKey_D);
	clientConfig.region = theKeys.region;

	std::time_t t = std::time(0);   // get time now
	std::tm* now = std::localtime(&t);

	std::cout << (now->tm_year + 1900) << '-' << (now->tm_mon + 1) << '-' << now->tm_mday << ' ' << now->tm_hour << ":" << now->tm_min << ":" << now->tm_sec;
	std::cout << " UKMON Live Filewatcher C++ version. Monitoring: " << ProcessingPath << std::endl;
	std::cout << "Logging to the windows eventlog" << std::endl;
	wchar_t msg0[512] = { 0 };
	char msg0_s[512] = { 0 };
	sprintf(msg0_s, "Monitoring %s", ProcessingPath);
	mbstowcs(msg0, msg0_s, 512);
	std::cout << "The following checks are in place: " << std::endl;
	if (framelimit > -1) std::cout << "frame count < " << framelimit << std::endl;
	if (minbright > -1) std::cout << "brightness > " << minbright << std::endl;
	std::cout << "error in fit < " << std::setprecision(2) << maxrms << std::endl;

	wsprintf(msg, L"Checking for trails shorter than %ld;", framelimit);
	wsprintf(msg2, L"Checking for objects brighter than %ld;", minbright);

	if (Debug)
	{
		std::cout << "Debugging is on" << std::endl;
		wsprintf(msg3, L"Debugging is on;");
	}
	if (dryrun)
	{
		std::cout << "Dry run enabled - nothing will be uploaded" << std::endl;
		wsprintf(msg4, L"Dry run is on- nothing will be uploaded;");
	}
	//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 1, msg0, msg, msg2, msg3, msg4, L"");

	std::cout << "==============================================" << std::endl;

	wchar_t lpDir[512] = {0};
	DWORD buflen=0, retsiz=0;
	DWORD dwFilter = FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_FILE_NAME| FILE_NOTIFY_CHANGE_SIZE;

	mbstowcs(lpDir, ProcessingPath, strlen(ProcessingPath));
	HANDLE hDir = CreateFile(
		lpDir,
		FILE_LIST_DIRECTORY,
		FILE_SHARE_WRITE | FILE_SHARE_READ | FILE_SHARE_DELETE,
		NULL,
		OPEN_EXISTING,
		FILE_FLAG_BACKUP_SEMANTICS,
		NULL);
	if (hDir == NULL)
	{
		//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Invalid data file path; cannot continue;", L"");
		return -1;
	}

	nCounter = 0;

	// last filename retrieved - to avoid processing the same file twice
	// the initial write to a file generates one event but subsequent ones generate two
	wchar_t lastname[512] = { 0 }; 
	while (1)
	{
		FILE_NOTIFY_INFORMATION *lpBuf = (FILE_NOTIFY_INFORMATION *)calloc(BUFLEN, sizeof(DWORD));
		buflen = BUFLEN* sizeof(DWORD);
		FILE_NOTIFY_INFORMATION *pbuf;
		if (!lpBuf)
		{
			//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Unable to allocate memory for directory reads; cannot continue;", L"");
			exit (-1);
		}
		if (Debug && !dryrun) std::cout << "1. waiting for changes" << std::endl;
		if (ReadDirectoryChangesW(hDir, (LPVOID)lpBuf, buflen, TRUE, dwFilter, &retsiz, NULL, NULL))
		{
			if (Debug && !dryrun) std::cout << "2. Recieved " << retsiz << " bytes" << std::endl;
			if (lpBuf == NULL)
			{
				wchar_t msg[512] = { 0 };
				char msg_s[512] = { 0 };
				DWORD e = GetLastError();
				FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM, 0, e, 0, msg, 512,NULL);
				wcstombs(msg_s, msg, 512);
				std::cout << "Error " << e << " scanning directory" << ProcessingPath << " - buffer trashed" << msg << std::endl;
				//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 98, L"Error Scanning directory" , L"buffer trashed;", L"");
			}	
			else if (retsiz > 0)
			{
				DWORD offset; 
				pbuf = lpBuf;
				do 
				{
					wchar_t fname[512] = { 0 };
					wcsncpy(fname, pbuf->FileName, pbuf->FileNameLength/2);
					offset = pbuf->NextEntryOffset;

					// check file is different and action is modified 
					if (wcsncmp(lastname, fname, pbuf->FileNameLength/2) != 0 && (pbuf->Action == FILE_ACTION_ADDED))
					{
						char filename_s[512] = { 0 };
						wcstombs(filename_s, fname, wcslen(fname));

						if (Debug && !dryrun) std::cout << filename_s << std::endl;


						// wait for the XML file, but skip files with a + in it as these are manual captures. 
						// and skip files with A.XML in them as these are analysis files
						std::string fn = filename_s;
						size_t m1, m2, m3, l;
						m1 = fn.find(".xml");
						m2 = fn.find("+");
						m3 = fn.find("A.XML");
						l = fn.npos;

						if(m1!=l && m2==l && m3 == l)
						{
							// check for data quality - long recordings are usually planes or birds, short ones are flashes
							// and dim ones arent worth uploading to the live stream

							long frcount = minframes+1;
							long maxbmax = minbright+1;
							double rms = 0;
							int pxls = 0;
							std::string pth = ProcessingPath;
							int gooddata = 1;
							Sleep(500); //to allow file write to complete
							ReadBasicXML(pth, filename_s, frcount, maxbmax, rms, pxls);
							if (framelimit > -1 && (frcount > framelimit || frcount < minframes))// || rms > maxrms))
								gooddata = 0;
							if (minbright > -1 && maxbmax < minbright)
								gooddata = 0;

							if(Debug && !dryrun) std::cout << "A: " << filename_s << " " << theKeys.BucketName << std::endl;

							if (gooddata)
							{
								put_file(theKeys.BucketName, filename_s, frcount, maxbmax, rms);
								fn.replace(m1, 4, "P.jpg");
								put_file(theKeys.BucketName, fn.c_str(), frcount, maxbmax, rms);
								if (pxls > minPxls)
								{
									std::string bname = fn.substr(0, m1);
									std::cout << bname << std::endl;
									char cmd[512] = { 0 };
									sprintf(cmd, "%s -i %s\\%s.avi %s\\%s.mp4", ffmpegPath,
										ProcessingPath, bname.c_str(), ProcessingPath, bname.c_str());
									system(cmd);
									std::string mp4name = bname + ".mp4";
									put_file(theKeys.BucketName, mp4name.c_str(), frcount, maxbmax, rms);
								}
							}
							else
							{
								nCounter++;
								std::cout << nCounter << ": Skipping " << filename_s << ":";
								if (frcount < minframes)
									std::cout << " framecount " << frcount << "<" << minframes;
								if (frcount > framelimit)
									std::cout << " framecount " << frcount << ">" << framelimit;
								if (maxbmax < minbright)
									std::cout << " brightness " << maxbmax << "<" << minbright;
								if (rms > maxrms)
									std::cout << " RMS error " << std::setprecision(2) << rms << ">" << maxrms;
								std::cout << std::endl;

								wsprintf(msg, L"%d: skipping %ls - framecount %d brightness %d rms %.2f", nCounter, fname, frcount, maxbmax, rms);
								//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 3, msg, L"");
							}
						}
					}
					char *p = (char *)pbuf;
					p += offset;
					pbuf = (FILE_NOTIFY_INFORMATION *)p;
					wcscpy(lastname, fname);
				} while (offset > 0);
				memset(lpBuf, 0, BUFLEN);
			}
		}
		else
		{
			wchar_t mmsg[512] = { 0 };
			char msg_s[512] = { 0 };
			DWORD e = GetLastError();
			FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM, 0, e, 0, mmsg, 512, NULL);
			wcstombs(msg_s, mmsg, 512);
			std::cout << "Error " << e << " scanning directory" << ProcessingPath << " " << mmsg << std::endl;
			//theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 99, L"Error Scanning Directory; cannot continue", mmsg, L"");
			exit(-1);
		}
		free(lpBuf);
	}
	Aws::ShutdownAPI(options);
	return 0;
}
