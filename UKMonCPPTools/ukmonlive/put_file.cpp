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

Aws::Auth::AWSCredentials creds; // aws credentials
Aws::Client::ClientConfiguration clientConfig; // client setup

/**
* Put an object to an Amazon S3 bucket.
*/
int put_file(char* buckname, const char* fname, long frcount, long maxbmax, double rms)
{
	wchar_t msg[512] = { 0 };
	Aws::String file_name = ProcessingPath;
	file_name += "/";
	file_name += fname;
	if (Debug) std::cout << "B1: " << file_name << " " << buckname << std::endl;
	const char* fullname = file_name.c_str();

	// filename may contain path relative to the processing path - we need to remove this before
	// fixing the key_name
	Aws::String kn = fname, key_name;
	size_t n = kn.find_last_of("\\");
	if (n!=kn.npos)
		key_name.assign(kn, n+1);
	else
		key_name = fname;

	if (Debug) std::cout << "C: " << key_name << " " << key_name.c_str() << std::endl;

	nCounter++;

	if (dryrun == 0)
	{
		std::cout << nCounter << ": Uploading " << key_name.c_str() << "...";

		Aws::S3::S3Client s3_client(creds, clientConfig);

		Aws::S3::Model::PutObjectRequest object_request;
		object_request.SetBucket(buckname);
		object_request.SetKey(key_name.c_str());

		// Binary files must also have the std::ios_base::bin flag or'ed in
		const std::shared_ptr<Aws::IOStream> input_data =
			Aws::MakeShared<Aws::FStream>("PutObjectInputStream", fullname, std::ios_base::in | std::ios_base::binary);

		object_request.SetBody(input_data);
		auto put_object_outcome = s3_client.PutObject(object_request);
		int retry = maxretry;
		while (!put_object_outcome.IsSuccess() && retry > 0)
		{
			Sleep(1000);
			put_object_outcome = s3_client.PutObject(object_request);
			retry--;
		}
		if (put_object_outcome.IsSuccess())
		{
			std::cerr << "Done! Frames " << frcount << " brightness " << maxbmax << std::setprecision(2) << " rms " << rms << std::endl;
			wchar_t wfname[512] = { 0 };
			mbstowcs(wfname, fname, strlen(fname));
			wsprintf(msg, L"%d: Uploading %ls....done! Frames %d brightness %d rms %.2f", nCounter, wfname, frcount, maxbmax, rms);
			theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 2, msg, L"");
		}
		else
		{
			std::cerr << "Upload of " << file_name << " failed after " << maxretry << " attempts - check log!" << std::endl;

			wchar_t wfname[512] = { 0 };
			mbstowcs(wfname, fname, strlen(fname));
			wsprintf(msg, L"%d: Uploading %ls....Failed after %d attempts!", nCounter, wfname, maxretry);
			wchar_t msg2[512] = { 0 };
			wsprintf(msg2, L"%s: %s", put_object_outcome.GetError().GetExceptionName(), put_object_outcome.GetError().GetMessage());
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
	return 0;
}
