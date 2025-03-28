#include <windows.h>
#include <psapi.h>
#include <iostream>
#include <thread>
#include <shellapi.h>  // Add this header for IsUserAnAdmin()


// Helper to get process name from window handle
std::wstring GetProcessName(DWORD processId) {
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, processId);
    if (!hProcess) return L"";

    WCHAR buffer[MAX_PATH];
    DWORD size = MAX_PATH;
    std::wstring processName;

    if (QueryFullProcessImageNameW(hProcess, 0, buffer, &size)) {
        processName = buffer;
    }
    CloseHandle(hProcess);

    // Extract filename from path
    size_t pos = processName.find_last_of(L"\\/");
    if (pos != std::wstring::npos) {
        processName = processName.substr(pos + 1);
    }

    return processName;
}

// Window enumeration callback
BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam) {
    DWORD processId;
    GetWindowThreadProcessId(hwnd, &processId);

    std::wstring targetProcess = L"vlc.exe";
    std::wstring currentProcess = GetProcessName(processId);

    if (currentProcess == targetProcess) {
        std::wcout << L"Found VLC window: " << hwnd << std::endl;

        // Try to set window affinity
        if (SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)) {
            std::wcout << L"Successfully hid window: " << hwnd << std::endl;
        } else {
            std::wcerr << L"Failed to hide window (" << GetLastError() << L")" << std::endl;
        }
    }
    return TRUE;
}

void MonitorWindows() {
    while (true) {
        std::wcout << L"Scanning windows..." << std::endl;
        EnumWindows(EnumWindowsProc, 0);
        std::this_thread::sleep_for(std::chrono::seconds(2));
    }
}


bool IsRunningAsAdmin() {
    BOOL isAdmin = FALSE;
    HANDLE hToken = NULL;

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
    std::wcout << L"Starting VLC window hider" << std::endl;

    if (!IsRunningAsAdmin()) {
        std::wcerr << L"Warning: Not running as administrator" << std::endl;
    }

    MonitorWindows();
    return 0;
}



// First Contact Conclusions
// According to Microsoft’s documentation, SetWindowDisplayAffinity is intended to protect the contents of windows from being captured by certain screen capture APIs—but only for windows that your application created. Windows has security restrictions that prevent one process from modifying the properties of a window owned by another process. That’s why your VLC windows typically return “Failed to hide window (5)”.

// A few additional notes:
// • Running as administrator does not grant you permission to change properties on windows created by another process.
// • Even if you were able to inject code or otherwise modify another process’s properties (which brings its own set of difficulties and security implications), Windows only supports display affinity on its own windows.
// • The fact that one VLC window (0x580ba4) gave error code 0 might be due to some oddity in the state of that window or the timing of the query—but the important thing is that the function isn’t intended to work with foreign windows.
