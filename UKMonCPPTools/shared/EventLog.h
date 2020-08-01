#pragma once
/*
EventLog.h based on a sample by Hartmut Luetz - Hawranke at
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

//#define _WIN32_WINNT 0x0501

#define _AFXDLL
#if !defined(AFX_EVENTLOG_H__7D48CC33_4E41_4E0C_B16A_5FC714CAC457__INCLUDED_)
#define AFX_EVENTLOG_H__7D48CC33_4E41_4E0C_B16A_5FC714CAC457__INCLUDED_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include <afxwin.h>

class CEventLog : public CObject
{
	DECLARE_DYNCREATE(CEventLog)

public:
	CEventLog(void);
	virtual ~CEventLog(void);

	BOOL Initialize(const wchar_t *csApp);
	HANDLE GetHandle(void) { return m_hLog; };

	BOOL Fire(WORD wType, WORD wCategory, DWORD dwEventID, ...);
	BOOL FireWithData(WORD wType, WORD wCategory,
		DWORD dwEventID, DWORD dwData, LPVOID ptr, ...);

	CString LoadMessage(DWORD dwMsgId, ...);
	BOOL LaunchViewer(void);

	DWORD AddEventSource(const wchar_t *csName,DWORD dwCategoryCount = 0);
	DWORD RemoveEventSource(const wchar_t *csApp);

protected:
	PSID GetUserSID(PSID * ppSid);

protected:
	HANDLE m_hLog;
};

extern CEventLog theEventLog;
#endif
// !defined(AFX_EVENTLOG_H__7D48CC33_4E41_4E0C_B16A_5FC714CAC457__INCLUDED_)