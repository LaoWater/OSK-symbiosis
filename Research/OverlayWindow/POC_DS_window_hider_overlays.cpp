#include <windows.h>
#include <psapi.h>
#include <iostream>
#include <thread>
#include <shellapi.h>

// Enable debug privileges for window manipulation
bool EnableDebugPrivilege() {
    HANDLE hToken;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken)) {
        return false;
    }

    TOKEN_PRIVILEGES tp;
    LUID luid;

    if (!LookupPrivilegeValue(nullptr, SE_DEBUG_NAME, &luid)) {
        CloseHandle(hToken);
        return false;
    }

    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    if (!AdjustTokenPrivileges(hToken, FALSE, &tp, sizeof(TOKEN_PRIVILEGES), nullptr, nullptr)) {
        CloseHandle(hToken);
        return false;
    }

    CloseHandle(hToken);
    return true;
}

std::wstring GetProcessName(DWORD processId) {
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ, FALSE, processId);
    if (!hProcess) return L"";

    WCHAR buffer[MAX_PATH];
    DWORD size = MAX_PATH;
    std::wstring processName;

    if (QueryFullProcessImageNameW(hProcess, 0, buffer, &size)) {
        processName = buffer;
    }
    CloseHandle(hProcess);

    size_t pos = processName.find_last_of(L"\\/");
    if (pos != std::wstring::npos) {
        processName = processName.substr(pos + 1);
    }

    return processName;
}

BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam) {
    if (!IsWindow(hwnd) || !IsWindowVisible(hwnd)) {
        return TRUE;
    }

    DWORD processId;
    GetWindowThreadProcessId(hwnd, &processId);

    std::wstring targetProcess = L"vlc.exe";
    std::wstring currentProcess = GetProcessName(processId);

    if (currentProcess == targetProcess) {
        std::wcout << L"Found VLC window: " << hwnd << std::endl;

        // Set window as layered
        LONG_PTR style = GetWindowLongPtr(hwnd, GWL_EXSTYLE);
        if (!(style & WS_EX_LAYERED)) {
            SetWindowLongPtr(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED);
        }

        // Make window transparent but clickable
        if (SetLayeredWindowAttributes(hwnd, 0, 1, LWA_ALPHA)) {
            std::wcout << L"Window made transparent: " << hwnd << std::endl;
            
            // Force window redraw
            SetWindowPos(hwnd, nullptr, 0, 0, 0, 0,
                       SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED);
        } else {
            DWORD error = GetLastError();
            std::wcerr << L"Failed to set transparency (Error " << error << L")" << std::endl;
        }
    }
    return TRUE;
}

void MonitorWindows() {
    while (true) {
        EnumWindows(EnumWindowsProc, 0);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
}

bool IsRunningAsAdmin() {
    BOOL isAdmin = FALSE;
    HANDLE hToken = nullptr;

    if (OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &hToken)) {
        TOKEN_ELEVATION elevation;
        DWORD size;
        if (GetTokenInformation(hToken, TokenElevation, &elevation, sizeof(elevation), &size)) {
            isAdmin = elevation.TokenIsElevated;
        }
        CloseHandle(hToken);
    }
    return isAdmin;
}

int main() {
    std::wcout << L"Starting VLC Window Ghostifier" << std::endl;

    if (!IsRunningAsAdmin()) {
        std::wcerr << L"Error: Administrator privileges required!" << std::endl;
        return 1;
    }

    if (!EnableDebugPrivilege()) {
        std::wcerr << L"Warning: Debug privileges not enabled (Error " 
                  << GetLastError() << L")" << std::endl;
    }

    MonitorWindows();
    return 0;
}