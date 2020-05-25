#define _CRT_SECURE_NO_WARNINGS

/*
EventLog.cpp based on a sample by Hartmut Luetz - Hawranke at
https://www.codeproject.com/Articles/8664/Simple-class-to-fire-messages-to-Windows-EventLog

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

#include "EventLog.h"

#ifdef _DEBUG
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#define new DEBUG_NEW
#endif

//////////////////////////////////////////////////////////////////////
// Konstruktion/Destruktion
//////////////////////////////////////////////////////////////////////

IMPLEMENT_DYNAMIC(CEventLog, CObject)

CEventLog theEventLog;

CEventLog::CEventLog()
{
	m_hLog = NULL;
}

CEventLog::~CEventLog()
{
	if (m_hLog != NULL)
	{
		DeregisterEventSource(m_hLog);
		m_hLog = NULL;
	}
}


BOOL CEventLog::Initialize(wchar_t *csApp)
{
	// Try to add application to EventVwr
	AddEventSource(csApp, 3);
/*	if (AddEventSource(csApp, 3) != 0)
	{
		CString cs;
		cs = "Unable to register EventLog access for application: ";
		cs += "  Please log in with admin rights to do this.";
		cs += "  \nApplication will run without event logging";
		AfxMessageBox(cs, MB_ICONEXCLAMATION);
	}
*/
	// Register to write
	m_hLog = ::RegisterEventSource(NULL, csApp);

	return TRUE;
}

DWORD CEventLog::AddEventSource(wchar_t *csName, DWORD dwCategoryCount)
{
	HKEY hRegKey = NULL;
	DWORD dwError = 0;
	TCHAR szPath[MAX_PATH];

	_stprintf(szPath, _T("SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\%s"), csName );

		// Create the event source registry key
		dwError = RegCreateKey(HKEY_LOCAL_MACHINE, szPath, &hRegKey);
	// This error is ignored
	// if (dwError != 0)
	//   return dwError;

	// Name of the PE module that contains the message resource
	GetModuleFileName(NULL, szPath, MAX_PATH);

	// Register EventMessageFile
	dwError = RegSetValueEx(hRegKey, _T("EventMessageFile"), 0,
		REG_EXPAND_SZ, (PBYTE)szPath,
		(_tcslen(szPath) + 1) * sizeof TCHAR);
	if (dwError == 0)
	{
		// Register supported event types
		DWORD dwTypes = EVENTLOG_ERROR_TYPE | EVENTLOG_WARNING_TYPE |
			EVENTLOG_INFORMATION_TYPE;
		dwError = RegSetValueEx(hRegKey, _T("TypesSupported"),
			0, REG_DWORD, (LPBYTE)&dwTypes, sizeof dwTypes);

		// If we want to support event categories, we have
		// also to register the CategoryMessageFile.
		// and set CategoryCount. Note that categories need
		// to have the message ids 1 to CategoryCount!

		if (dwError == 0 && dwCategoryCount > 0)
		{
			dwError = RegSetValueEx(hRegKey, _T("CategoryMessageFile"), 0,
				REG_EXPAND_SZ, (PBYTE)szPath,
				(_tcslen(szPath) + 1) * sizeof TCHAR);
			if (dwError == 0)
				dwError = RegSetValueEx(hRegKey, _T("CategoryCount"), 0,
					REG_DWORD, (PBYTE)&dwCategoryCount,
					sizeof dwCategoryCount);
		}
	}

	RegCloseKey(hRegKey);

	return dwError;
}

DWORD CEventLog::RemoveEventSource(wchar_t *csApp)
{
	DWORD dwError = 0;
	TCHAR szPath[MAX_PATH];

	_stprintf(szPath, _T("SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\%s"), csApp );
		return RegDeleteKey(HKEY_LOCAL_MACHINE, szPath);
}

CString CEventLog::LoadMessage(DWORD dwMsgId, ...)
{
	wchar_t  pszBuffer[1024];
	DWORD cchBuffer = 1024;

	va_list args;
	va_start(args, cchBuffer);

	if (FormatMessage(FORMAT_MESSAGE_FROM_HMODULE,
		// Module (e.g. DLL) to search
		// for the Message. NULL = own .EXE
		NULL,
		// Id of the message to look up (aus "Messages.h")
		dwMsgId,
		// Language: LANG_NEUTRAL = current thread's language
		LANG_NEUTRAL,
		// Destination buffer
		pszBuffer,
		// Character count of destination buffer
		cchBuffer,
		// Insertion parameters
		&args
	))

		return pszBuffer;
	else
		return "";
}

BOOL CEventLog::Fire(WORD wType, WORD wCategory, DWORD dwEventID, ...)
{
	PSID sid = NULL;
	va_list args;
	va_start(args, dwEventID);

	CString cs;
	int iCount = 0;

	while (1)
	{
		char *p = va_arg(args, char *);
		if (*p != '\0')
			iCount++;
		else
			break;
	}

	// Jump to beginning of list
	va_start(args, dwEventID);

	if (m_hLog == NULL)
		return FALSE;

	BOOL bRet = ReportEvent(m_hLog, wType, wCategory, dwEventID,
		GetUserSID(&sid), iCount, 0, (LPCTSTR *)args, NULL);
	va_end(args);
	if (sid != NULL)
		delete[] sid;
	return bRet;
}

BOOL CEventLog::FireWithData(WORD wType, WORD wCategory,
	DWORD dwEventID, DWORD dwData, LPVOID ptr, ...)
{
	PSID sid = NULL;
	va_list args;
	va_start(args, ptr);

	CString cs;
	int iCount = 0;

	while (1)
	{
		char *p = va_arg(args, char *);
		if (*p != '\0')
			iCount++;
		else
			break;
	}

	// Jump to beginning of list
	va_start(args, ptr);

	if (m_hLog == NULL)
		return FALSE;

	BOOL bRet = ReportEvent(m_hLog, wType, wCategory, dwEventID,
		GetUserSID(&sid), iCount, dwData,
		(LPCTSTR *)args, ptr);
	va_end(args);
	if (sid != NULL)
		delete[] sid;
	return bRet;
}

BOOL CEventLog::LaunchViewer()
{
	CString csVwr = "%SystemRoot%\\system32\\eventvwr.msc", csParam = " /s";
	CString csVwrExpand, csDefaultDir, csMsg;
	long lErr = ExpandEnvironmentStrings(csVwr,
		csVwrExpand.GetBufferSetLength(MAX_PATH), MAX_PATH);
	if (lErr == 0)
		return FALSE;

	csVwrExpand.ReleaseBuffer();
	int iPos = csVwrExpand.ReverseFind('\\');
	if (iPos != -1)
		csDefaultDir = csVwrExpand.Left(iPos);

	long hinst = (long)::FindExecutable(csVwrExpand, csDefaultDir,
		csVwr.GetBufferSetLength(MAX_PATH));
	csVwr.ReleaseBuffer();
	switch (hinst)
	{
	case 0:
		AfxMessageBox(L"The system is out of memory or resources.", MB_ICONSTOP);
		return  FALSE;
	case 31:
		csMsg.Format(L"No association for file type of '%s' found.", csVwrExpand);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return  FALSE;
	case ERROR_FILE_NOT_FOUND:
		csMsg.Format(L"File '%s' not found.", csVwrExpand);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return  FALSE;
	case ERROR_PATH_NOT_FOUND:
		csMsg.Format(L"Path of file '%s' not found.", csVwrExpand);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return  FALSE;
	case ERROR_BAD_FORMAT:
		csMsg.Format(L"The executable file '%s' is invalid (non - Win32®.exe or error in.exe image).", csVwr);
			AfxMessageBox(csMsg, MB_ICONSTOP);
		return  FALSE;
	default:
		if (hinst < 32)
		{
			csMsg.Format(L"Unknown error %d returned from FindExecutable().", hinst);
			AfxMessageBox(csMsg, MB_ICONSTOP);
			return  FALSE;
		}
		break;
	}

	hinst = (long)::ShellExecute(NULL, L"open", csVwr, csVwrExpand + csParam,
		csDefaultDir, SW_SHOWNORMAL);
	switch (hinst)
	{
	case 0:
		AfxMessageBox(L"The operating system is out of memory or resources.", MB_ICONSTOP);
			return FALSE;
	case ERROR_FILE_NOT_FOUND:
		csMsg.Format(L"File '%s' not found.", csVwr);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case ERROR_PATH_NOT_FOUND:
		csMsg.Format(L"Path of file '%s' not found.", csVwr);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case ERROR_BAD_FORMAT:
		csMsg.Format(L"The executable for file '%s' is invalid (non - Win32®.exe or error in.exe image).", csVwr);
			AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case SE_ERR_ACCESSDENIED:
		csMsg.Format(L"The operating system denied access to file '%s'.", csVwr);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case SE_ERR_ASSOCINCOMPLETE:
		csMsg.Format(L"Name association for file %s' is incomplete or invalid.", csVwr);
			AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case SE_ERR_DDEBUSY:
		AfxMessageBox(L"The DDE transaction could not be completed because other DDE transactions were being processed.", 
			MB_ICONSTOP);
		return FALSE;
	case SE_ERR_DDEFAIL:
		AfxMessageBox(L"The DDE transaction failed.", MB_ICONSTOP);
		return FALSE;
	case SE_ERR_DDETIMEOUT:
		AfxMessageBox(L"The DDE transaction could not be completed because the request timed out.", MB_ICONSTOP);
			return FALSE;
	case SE_ERR_DLLNOTFOUND:
		AfxMessageBox(L"The specified dynamic-link library was not found.", MB_ICONSTOP);
			return FALSE;
	case SE_ERR_NOASSOC:
		csMsg.Format(L"No association for file type of '%s' found.", csVwr);
		AfxMessageBox(csMsg, MB_ICONSTOP);
		return FALSE;
	case SE_ERR_OOM:
		AfxMessageBox(L"The system is out of memory or resources.", MB_ICONSTOP);
		return FALSE;
	case SE_ERR_SHARE:
		AfxMessageBox(L"A sharing violation occurred.", MB_ICONSTOP);
		return FALSE;
	default:
		if (hinst < 32)
		{
			csMsg.Format(L"Unknown error %d returned from ShellExecute().", hinst);
			AfxMessageBox(csMsg, MB_ICONSTOP);
			return FALSE;
		}
		return TRUE;
	}
	return FALSE;
}

PSID CEventLog::GetUserSID(PSID * ppSid)
{
	BOOL bRet = FALSE;
	const DWORD INITIAL_SIZE = MAX_PATH;

	CString csAccName;
	DWORD size = INITIAL_SIZE;

	::GetUserName(csAccName.GetBufferSetLength(size), &size);
	csAccName.ReleaseBuffer(size);

	// Validate the input parameters.
	if (csAccName.IsEmpty() || ppSid == NULL)
	{
		return NULL;
	}


	// Create buffers.
	DWORD cbSid = 0;
	DWORD dwErrorCode = 0;
	DWORD dwSidBufferSize = INITIAL_SIZE;
	DWORD cchDomainName = INITIAL_SIZE;
	CString csDomainName;
	SID_NAME_USE eSidType;
	HRESULT hr = 0;


	// Create buffers for the SID.
	*ppSid = (PSID) new BYTE[dwSidBufferSize];
	if (*ppSid == NULL)
	{
		return NULL;
	}
	memset(*ppSid, 0, dwSidBufferSize);


	// Obtain the SID for the account name passed.
	for (; ; )
	{

		// Set the count variables to the buffer sizes and retrieve the SID.
		cbSid = dwSidBufferSize;
		bRet = LookupAccountName(NULL, csAccName, *ppSid, &cbSid,
			csDomainName.GetBufferSetLength(cchDomainName),
			&cchDomainName, &eSidType);
		csDomainName.ReleaseBuffer();
		if (bRet)
		{
			if (IsValidSid(*ppSid) == FALSE)
			{
				CString csMsg;
				csMsg.Format(L"The SID for %s is invalid.\n", csAccName);
				AfxMessageBox(csMsg, MB_ICONSTOP);
				bRet = FALSE;
			}
			break;
		}
		dwErrorCode = GetLastError();


		// Check if one of the buffers was too small.
		if (dwErrorCode == ERROR_INSUFFICIENT_BUFFER)
		{
			if (cbSid > dwSidBufferSize)
			{

				// Reallocate memory for the SID buffer.
				TRACE("The SID buffer was too small. It will be reallocated.\n");
				FreeSid(*ppSid);
				*ppSid = (PSID) new BYTE[cbSid];
				if (*ppSid == NULL)
				{
					return NULL;
				}
				memset(*ppSid, 0, cbSid);
				dwSidBufferSize = cbSid;
			}
		}
		else
		{
			CString csMsg;
			csMsg.Format(L"LookupAccountNameW failed. GetLastError returned : %d\n", dwErrorCode);
				AfxMessageBox(csMsg, MB_ICONSTOP);
			hr = HRESULT_FROM_WIN32(dwErrorCode);
			break;
		}
	}

	// If we had an error, free memory of SID
	if (!bRet && *ppSid != NULL)
	{
		delete[] * ppSid;
		*ppSid = NULL;
	}

	return *ppSid;
}