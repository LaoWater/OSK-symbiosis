#include <windows.h>
#include <psapi.h>
#include <iostream>
#include <thread>

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

int main() {
    std::wcout << L"Starting VLC window hider" << std::endl;

    // Need to run as admin for some windows
    if (!IsUserAnAdmin()) {
        std::wcerr << L"Warning: Not running as administrator" << std::endl;
    }

    MonitorWindows();
    return 0;
}