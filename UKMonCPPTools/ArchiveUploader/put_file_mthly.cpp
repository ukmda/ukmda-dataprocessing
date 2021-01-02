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

/*
Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
This file is licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License. A copy of
the License is located at
http://aws.amazon.com/apache2.0/
This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
*/
#include "UKMonMonthlyArchiver.h"

#undef GetMessage                       // workaround for AWSError method GetMessage()
#undef GetObject 
#undef PutObject

__int64 FileSize(const wchar_t* name);

/**
* Put an object to an Amazon S3 bucket.
*/
int put_file(char* buckname, const char* objname, const char* fname, Aws::S3::S3Client s3_client)
{
	wchar_t msg[512] = { 0 };

	const Aws::String bucket_name = buckname;

	Aws::String file_name;
	Aws::String key_name;
	file_name = fname;
	key_name = objname;
	wchar_t wfname[512] = { 0 };

	if (Debug) std::cout << "Checking " << key_name << " " << file_name << std::endl;

	/* check if the object already exists - don't overwrite it unless the flag is set */
	int exists = 0;
	__int64 locfsize = 0, awsfsize = 0;

	if (!overwrite)
	{
		mbstowcs(wfname, fname, strlen(fname));
		locfsize = FileSize(wfname);

		Aws::S3::Model::HeadObjectRequest request;
		request.WithBucket(bucket_name).WithKey(key_name);
		const auto res = s3_client.HeadObject(request);
		if (res.IsSuccess())
		{
			awsfsize = res.GetResult().GetContentLength();
			if (awsfsize != locfsize)
				exists = 0;
			else
				exists = 1;
		}
	}
	if (overwrite || !exists)
	{
		Aws::S3::Model::PutObjectRequest object_request;
		object_request.WithBucket(bucket_name).WithKey(key_name);

		// Binary files must also have the std::ios_base::bin flag or'ed in
		auto input_data = Aws::MakeShared<Aws::FStream>("PutObjectInputStream",
			file_name.c_str(), std::ios_base::in | std::ios_base::binary);

		object_request.SetBody(input_data);

		if (dryrun == 0)
		{
			nCounter++;
			std::cout << nCounter << ": Uploading " << fname << "...";

			Aws::S3::Model::PutObjectOutcome put_object_outcome = s3_client.PutObject(object_request);
			int retry = maxretry;
			while (!put_object_outcome.IsSuccess() && retry > 0)
			{
				Sleep(1000);
				put_object_outcome = s3_client.PutObject(object_request);
				retry--;
			}
			if (put_object_outcome.IsSuccess())
			{
				std::cerr << "Done!" << std::endl;
				wsprintf(msg, L"%d: Uploading %ls....done!", nCounter, wfname);
				theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 2, msg, L"");
			}
			else
			{
				std::cerr << "Upload of " << file_name << " failed after " << maxretry << " attempts - check log!" << std::endl;

				wchar_t wfname[512] = { 0 };
				mbstowcs(wfname, fname, strlen(fname));
				wsprintf(msg, L"%d: Uploading %ls....Failed after %d attempts!", nCounter, wfname, maxretry);
				wchar_t msg2[512] = { 0 };
				Aws::String errmsg = put_object_outcome.GetError().GetExceptionName();
				wchar_t errtype[512] = { 0 };
				mbstowcs(errtype, errmsg.c_str(), strlen(errmsg.c_str()));
				wsprintf(msg2, L"%s: %s", errtype, L"failed");
				theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 2, msg, msg2, L"");
			}
		}
		else
		{
			std::cout << std::endl << "dry run, would have sent " << file_name << std::endl;
			wchar_t wfname[512] = { 0 };
			mbstowcs(wfname, fname, strlen(fname));
			wsprintf(msg, L"Dry Run: Uploading %ls....done!", wfname);
			theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 2, msg, L"");
		}
	}
	else
	{
		//printf("skipping %s\n", fname);
	}

	return 0;
}

static __int64 FileSize(const wchar_t* name)
{
	HANDLE hFile = CreateFile(name, GENERIC_READ,
		FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL, NULL);
	if (hFile == INVALID_HANDLE_VALUE)
		return -1; // error condition, could call GetLastError to find out more

	LARGE_INTEGER size;
	if (!GetFileSizeEx(hFile, &size))
	{
		CloseHandle(hFile);
		return -1; // error condition, could call GetLastError to find out more
	}

	CloseHandle(hFile);
	return size.QuadPart;
}
#if 0
#if (_WIN32_WINNT==0x0501)

typedef size_t socklen_t;

int inet_pton(int af, const char *src, void *dst)
{
	struct sockaddr_storage ss;
	int size = sizeof(ss);
	char src_copy[INET6_ADDRSTRLEN + 1];

	ZeroMemory(&ss, sizeof(ss));
	// stupid non-const API
	strncpy(src_copy, src, INET6_ADDRSTRLEN + 1);
	src_copy[INET6_ADDRSTRLEN] = 0;

	if (WSAStringToAddressA(src_copy, af, NULL, (struct sockaddr *)&ss, &size) == 0)
	{
		switch (af)
		{
		case AF_INET:
			*(struct in_addr *)dst = ((struct sockaddr_in *)&ss)->sin_addr;
			return 1;

		case AF_INET6:
			*(struct in6_addr *)dst = ((struct sockaddr_in6 *)&ss)->sin6_addr;
			return 1;
		}
	}

	return 0;
}

const char *inet_ntop(int af, const void *src, char *dst, socklen_t size)
{
	struct sockaddr_storage ss;
	unsigned long s = size;

	ZeroMemory(&ss, sizeof(ss));
	ss.ss_family = af;

	switch (af)
	{
	case AF_INET:
		((struct sockaddr_in *)&ss)->sin_addr = *(struct in_addr *)src;
		break;

	case AF_INET6:
		((struct sockaddr_in6 *)&ss)->sin6_addr = *(struct in6_addr *)src;
		break;

	default:
		return NULL;
	}

	// cannot directly use &size because of strict aliasing rules
	return WSAAddressToStringA((struct sockaddr *)&ss, sizeof(ss), NULL, dst, &s) == 0 ? dst : NULL;
}
#endif
#endif