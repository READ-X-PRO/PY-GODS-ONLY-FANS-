#include <windows.h>
#include <commctrl.h>
#include <shlobj.h>
#include <fstream>
#include <sstream>
#include <vector>
#include <map>
#include <algorithm>
#include <cctype>
#include <ctime>
#include <thread>
#include <chrono>
#include <shellapi.h>

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "shell32.lib")

using namespace std;

// Global variables
HWND g_hMainWindow;
HWND g_hTabControl;
HWND g_hCommandList;
HWND g_hDetailsEdit;
HWND g_hSearchEdit;
HWND g_hCategoryCombo;
HWND g_hStatusBar;
vector<HWND> g_hTabs;

// Command structure
struct Command {
    wstring name;
    wstring description;
    wstring category;
    wstring examples;
    wstring dependencies;
};

// OS tabs
enum OSTab {
    LINUX_TAB = 0,
    WINDOWS_TAB,
    MACOS_TAB,
    FAVORITES_TAB
};

// Command data
map<OSTab, vector<Command>> g_commands;
vector<int> g_favorites;

// Current selection
OSTab g_currentTab = LINUX_TAB;
int g_currentSelection = -1;

// Matrix effect variables
const int MATRIX_COLS = 80;
const int MATRIX_ROWS = 25;
wchar_t g_matrix[MATRIX_ROWS][MATRIX_COLS];
const wchar_t MATRIX_CHARS[] = L"01";
const int MATRIX_UPDATE_INTERVAL = 100; // ms

// Colors
const COLORREF BG_COLOR = RGB(10, 10, 10);
const COLORREF TEXT_COLOR = RGB(0, 255, 0);
const COLORREF ACCENT_COLOR = RGB(0, 200, 0);
const COLORREF HIGHLIGHT_COLOR = RGB(0, 100, 0);
const COLORREF LIST_BG_COLOR = RGB(18, 18, 18);
const COLORREF LIST_SELECTION_COLOR = RGB(0, 80, 0);

// Forward declarations
void InitializeCommands();
void CreateMainWindow(HINSTANCE hInstance);
void CreateControls();
void PopulateCommandList();
void ShowCommandDetails(int index);
void FilterCommands();
void AddFavorite(int index);
void RemoveFavorite(int index);
bool IsFavorite(int index);
void RunSimulation();
void DrawMatrixEffect(HDC hdc, RECT rect);
void UpdateMatrixEffect();
void SaveOutputToFile();
void SetDarkTheme(HWND hwnd);

// Window procedure
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE:
            CreateControls();
            InitializeCommands();
            PopulateCommandList();
            
            // Initialize matrix effect
            srand(static_cast<unsigned int>(time(nullptr)));
            UpdateMatrixEffect();
            
            // Start matrix update timer
            SetTimer(hwnd, 1, MATRIX_UPDATE_INTERVAL, nullptr);
            return 0;
            
        case WM_SIZE: {
            RECT rc;
            GetClientRect(hwnd, &rc);
            
            // Position controls
            int statusHeight = 24;
            int tabHeight = 300;
            int detailsHeight = 200;
            int searchHeight = 30;
            
            // Status bar
            MoveWindow(g_hStatusBar, 0, rc.bottom - statusHeight, rc.right, statusHeight, TRUE);
            
            // Tab control
            MoveWindow(g_hTabControl, 10, 10, rc.right - 20, tabHeight, TRUE);
            
            // Command list
            for (HWND tab : g_hTabs) {
                MoveWindow(tab, 15, 40, rc.right - 30, tabHeight - 30, TRUE);
            }
            
            // Search box
            MoveWindow(g_hSearchEdit, 20, tabHeight + 15, 200, searchHeight, TRUE);
            
            // Category combo
            MoveWindow(g_hCategoryCombo, 230, tabHeight + 15, 150, searchHeight, TRUE);
            
            // Details edit
            MoveWindow(g_hDetailsEdit, 20, tabHeight + searchHeight + 20, 
                      rc.right - 40, detailsHeight, TRUE);
            
            break;
        }
        
        case WM_COMMAND: {
            int wmId = LOWORD(wParam);
            
            if (HIWORD(wParam) == EN_CHANGE && (HWND)lParam == g_hSearchEdit) {
                FilterCommands();
            }
            else if (HIWORD(wParam) == CBN_SELCHANGE && (HWND)lParam == g_hCategoryCombo) {
                FilterCommands();
            }
            else if (wmId == 100) { // Run simulation
                RunSimulation();
            }
            else if (wmId == 101) { // Save output
                SaveOutputToFile();
            }
            else if (wmId == 102) { // Exit
                SendMessage(hwnd, WM_CLOSE, 0, 0);
            }
            else if (wmId == 103) { // Add/Remove favorite
                if (g_currentSelection != -1) {
                    if (IsFavorite(g_currentSelection)) {
                        RemoveFavorite(g_currentSelection);
                    }
                    else {
                        AddFavorite(g_currentSelection);
                    }
                    if (g_currentTab == FAVORITES_TAB) {
                        PopulateCommandList();
                    }
                    ShowCommandDetails(g_currentSelection);
                }
            }
            break;
        }
        
        case WM_NOTIFY: {
            LPNMHDR nmhdr = (LPNMHDR)lParam;
            
            if (nmhdr->idFrom == 0 && nmhdr->code == TCN_SELCHANGE) {
                g_currentTab = (OSTab)TabCtrl_GetCurSel(g_hTabControl);
                PopulateCommandList();
                g_currentSelection = -1;
                SetWindowText(g_hDetailsEdit, L"Select a command to view details...");
            }
            else if (nmhdr->hwndFrom == g_hCommandList && nmhdr->code == LVN_ITEMCHANGED) {
                LPNMLISTVIEW pnmv = (LPNMLISTVIEW)lParam;
                if (pnmv->iItem != -1 && (pnmv->uChanged & LVIF_STATE)) {
                    g_currentSelection = pnmv->iItem;
                    ShowCommandDetails(g_currentSelection);
                }
            }
            break;
        }
        
        case WM_DRAWITEM: {
            LPDRAWITEMSTRUCT pDIS = (LPDRAWITEMSTRUCT)lParam;
            
            if (pDIS->CtlID == 0) { // Tab control
                HBRUSH hBrush = CreateSolidBrush(BG_COLOR);
                FillRect(pDIS->hDC, &pDIS->rcItem, hBrush);
                DeleteObject(hBrush);
                
                wchar_t tabText[256];
                TCITEM tci;
                tci.mask = TCIF_TEXT;
                tci.pszText = tabText;
                tci.cchTextMax = 256;
                TabCtrl_GetItem(pDIS->hwndItem, pDIS->itemID, &tci);
                
                int textLen = lstrlen(tabText);
                SetTextColor(pDIS->hDC, TEXT_COLOR);
                SetBkMode(pDIS->hDC, TRANSPARENT);
                
                if (pDIS->itemState & ODS_SELECTED) {
                    HBRUSH selBrush = CreateSolidBrush(HIGHLIGHT_COLOR);
                    FillRect(pDIS->hDC, &pDIS->rcItem, selBrush);
                    DeleteObject(selBrush);
                }
                
                DrawText(pDIS->hDC, tabText, textLen, &pDIS->rcItem, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
                return TRUE;
            }
            else if (pDIS->CtlID == 1) { // List view
                if (pDIS->itemID == -1) break;
                
                wchar_t buffer[256];
                ListView_GetItemText(g_hCommandList, pDIS->itemID, 0, buffer, 256);
                
                // Set background color
                HBRUSH hBrush;
                if (pDIS->itemState & ODS_SELECTED) {
                    hBrush = CreateSolidBrush(LIST_SELECTION_COLOR);
                }
                else {
                    hBrush = CreateSolidBrush(LIST_BG_COLOR);
                }
                FillRect(pDIS->hDC, &pDIS->rcItem, hBrush);
                DeleteObject(hBrush);
                
                // Draw text
                SetTextColor(pDIS->hDC, TEXT_COLOR);
                SetBkMode(pDIS->hDC, TRANSPARENT);
                
                RECT textRect = pDIS->rcItem;
                textRect.left += 5;
                DrawText(pDIS->hDC, buffer, -1, &textRect, DT_LEFT | DT_VCENTER | DT_SINGLELINE);
                
                // Draw favorite star if applicable
                if (IsFavorite(pDIS->itemID)) {
                    RECT starRect = pDIS->rcItem;
                    starRect.left = starRect.right - 30;
                    DrawText(pDIS->hDC, L"★", -1, &starRect, DT_CENTER | DT_VCENTER | DT_SINGLELINE);
                }
                
                return TRUE;
            }
            break;
        }
        
        case WM_CTLCOLORSTATIC:
        case WM_CTLCOLOREDIT: {
            HDC hdc = (HDC)wParam;
            SetTextColor(hdc, TEXT_COLOR);
            SetBkColor(hdc, LIST_BG_COLOR);
            return (LRESULT)CreateSolidBrush(LIST_BG_COLOR);
        }
        
        case WM_CTLCOLORLISTBOX: {
            HDC hdc = (HDC)wParam;
            SetTextColor(hdc, TEXT_COLOR);
            SetBkColor(hdc, LIST_BG_COLOR);
            return (LRESULT)CreateSolidBrush(LIST_BG_COLOR);
        }
        
        case WM_PAINT: {
            PAINTSTRUCT ps;
            HDC hdc = BeginPaint(hwnd, &ps);
            
            RECT rc;
            GetClientRect(hwnd, &rc);
            
            // Fill background
            HBRUSH hBrush = CreateSolidBrush(BG_COLOR);
            FillRect(hdc, &rc, hBrush);
            DeleteObject(hBrush);
            
            // Draw title
            SetTextColor(hdc, TEXT_COLOR);
            SetBkMode(hdc, TRANSPARENT);
            HFONT hFont = CreateFont(28, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET, 
                                    OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, 
                                    DEFAULT_PITCH | FF_DONTCARE, L"Courier New");
            HFONT hOldFont = (HFONT)SelectObject(hdc, hFont);
            
            RECT titleRect = {20, 15, rc.right - 20, 50};
            DrawText(hdc, L"RE_start", -1, &titleRect, DT_LEFT);
            
            // Draw subtitle
            HFONT hSubFont = CreateFont(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, 
                                       OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, 
                                       DEFAULT_PITCH | FF_DONTCARE, L"Courier New");
            SelectObject(hdc, hSubFont);
            
            RECT subRect = {120, 25, rc.right - 20, 50};
            DrawText(hdc, L"Terminal Commands Explorer", -1, &subRect, DT_LEFT);
            
            // Draw matrix effect
            RECT matrixRect = {rc.right - 220, 15, rc.right - 20, 50};
            DrawMatrixEffect(hdc, matrixRect);
            
            // Restore old font
            SelectObject(hdc, hOldFont);
            DeleteObject(hFont);
            DeleteObject(hSubFont);
            
            EndPaint(hwnd, &ps);
            return 0;
        }
        
        case WM_TIMER: {
            if (wParam == 1) { // Matrix update timer
                UpdateMatrixEffect();
                RECT rc;
                GetClientRect(hwnd, &rc);
                RECT matrixRect = {rc.right - 220, 15, rc.right - 20, 50};
                InvalidateRect(hwnd, &matrixRect, FALSE);
            }
            break;
        }
        
        case WM_CLOSE:
            DestroyWindow(hwnd);
            break;
            
        case WM_DESTROY:
            KillTimer(hwnd, 1);
            PostQuitMessage(0);
            break;
            
        default:
            return DefWindowProc(hwnd, msg, wParam, lParam);
    }
    return 0;
}

// Entry point
int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    // Initialize common controls
    INITCOMMONCONTROLSEX icc;
    icc.dwSize = sizeof(icc);
    icc.dwICC = ICC_WIN95_CLASSES | ICC_LISTVIEW_CLASSES | ICC_TAB_CLASSES;
    InitCommonControlsEx(&icc);
    
    // Register window class
    WNDCLASSEX wc = {};
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hCursor = LoadCursor(nullptr, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)CreateSolidBrush(BG_COLOR);
    wc.lpszClassName = L"REstartClass";
    RegisterClassEx(&wc);
    
    // Create main window
    g_hMainWindow = CreateWindow(
        L"REstartClass", L"RE_start - Terminal Commands Explorer",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 1000, 700,
        nullptr, nullptr, hInstance, nullptr
    );
    
    if (!g_hMainWindow) {
        return 0;
    }
    
    // Show window
    ShowWindow(g_hMainWindow, nCmdShow);
    UpdateWindow(g_hMainWindow);
    
    // Message loop
    MSG msg;
    while (GetMessage(&msg, nullptr, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    
    return (int)msg.wParam;
}

void CreateControls() {
    // Create tab control
    g_hTabControl = CreateWindow(
        WC_TABCONTROL, L"",
        WS_CHILD | WS_VISIBLE | TCS_FIXEDWIDTH | TCS_FOCUSNEVER,
        0, 0, 0, 0,
        g_hMainWindow, nullptr, GetModuleHandle(nullptr), nullptr
    );
    
    // Add tabs
    TCITEM tie = {};
    tie.mask = TCIF_TEXT;
    
    tie.pszText = L" Linux ";
    TabCtrl_InsertItem(g_hTabControl, LINUX_TAB, &tie);
    
    tie.pszText = L" Windows ";
    TabCtrl_InsertItem(g_hTabControl, WINDOWS_TAB, &tie);
    
    tie.pszText = L" macOS ";
    TabCtrl_InsertItem(g_hTabControl, MACOS_TAB, &tie);
    
    tie.pszText = L" ★ Favorites ";
    TabCtrl_InsertItem(g_hTabControl, FAVORITES_TAB, &tie);
    
    // Create command list for each tab
    for (int i = 0; i < 4; i++) {
        HWND hList = CreateWindow(
            WC_LISTVIEW, L"",
            WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | LVS_NOCOLUMNHEADER | LVS_OWNERDRAWFIXED,
            0, 0, 0, 0,
            g_hMainWindow, (HMENU)1, GetModuleHandle(nullptr), nullptr
        );
        
        // Add single column
        LVCOLUMN lvc = {};
        lvc.mask = LVCF_WIDTH;
        lvc.cx = 400;
        ListView_InsertColumn(hList, 0, &lvc);
        
        // Set extended style
        ListView_SetExtendedListViewStyle(hList, LVS_EX_FULLROWSELECT);
        
        // Hide all but first tab initially
        if (i != 0) {
            ShowWindow(hList, SW_HIDE);
        }
        
        g_hTabs.push_back(hList);
    }
    g_hCommandList = g_hTabs[0];
    
    // Create search box
    g_hSearchEdit = CreateWindow(
        WC_EDIT, L"",
        WS_CHILD | WS_VISIBLE | WS_BORDER | ES_AUTOHSCROLL,
        0, 0, 0, 0,
        g_hMainWindow, nullptr, GetModuleHandle(nullptr), nullptr
    );
    SetWindowText(g_hSearchEdit, L"Search...");
    
    // Create category combo
    g_hCategoryCombo = CreateWindow(
        WC_COMBOBOX, L"",
        WS_CHILD | WS_VISIBLE | CBS_DROPDOWNLIST | CBS_HASSTRINGS,
        0, 0, 0, 0,
        g_hMainWindow, nullptr, GetModuleHandle(nullptr), nullptr
    );
    
    // Add categories
    const wchar_t* categories[] = {
        L"All", L"File System", L"Networking", L"System Management",
        L"Package Management", L"Permissions", L"Text Processing", L"Utilities"
    };
    
    for (int i = 0; i < sizeof(categories) / sizeof(categories[0]); i++) {
        SendMessage(g_hCategoryCombo, CB_ADDSTRING, 0, (LPARAM)categories[i]);
    }
    SendMessage(g_hCategoryCombo, CB_SETCURSEL, 0, 0);
    
    // Create details edit control
    g_hDetailsEdit = CreateWindow(
        WC_EDIT, L"",
        WS_CHILD | WS_VISIBLE | WS_VSCROLL | ES_MULTILINE | ES_READONLY | ES_AUTOVSCROLL,
        0, 0, 0, 0,
        g_hMainWindow, nullptr, GetModuleHandle(nullptr), nullptr
    );
    
    // Set font for details
    HFONT hFont = CreateFont(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, 
                            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, 
                            FIXED_PITCH | FF_DONTCARE, L"Consolas");
    SendMessage(g_hDetailsEdit, WM_SETFONT, (WPARAM)hFont, TRUE);
    
    // Create status bar
    g_hStatusBar = CreateWindow(
        STATUSCLASSNAME, L"Initializing system...",
        WS_CHILD | WS_VISIBLE | SBARS_SIZEGRIP,
        0, 0, 0, 0,
        g_hMainWindow, nullptr, GetModuleHandle(nullptr), nullptr
    );
    
    // Create buttons
    CreateWindow(
        L"BUTTON", L"Run Simulation",
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        400, 0, 120, 30,
        g_hMainWindow, (HMENU)100, GetModuleHandle(nullptr), nullptr
    );
    
    CreateWindow(
        L"BUTTON", L"Save Output",
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        530, 0, 100, 30,
        g_hMainWindow, (HMENU)101, GetModuleHandle(nullptr), nullptr
    );
    
    CreateWindow(
        L"BUTTON", L"Add/Remove Favorite",
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        640, 0, 140, 30,
        g_hMainWindow, (HMENU)103, GetModuleHandle(nullptr), nullptr
    );
    
    CreateWindow(
        L"BUTTON", L"Exit",
        WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
        790, 0, 80, 30,
        g_hMainWindow, (HMENU)102, GetModuleHandle(nullptr), nullptr
    );
    
    // Set dark theme for controls
    for (HWND hwnd : g_hTabs) {
        SetDarkTheme(hwnd);
    }
    SetDarkTheme(g_hSearchEdit);
    SetDarkTheme(g_hCategoryCombo);
    SetDarkTheme(g_hDetailsEdit);
    SetDarkTheme(g_hStatusBar);
}

void InitializeCommands() {
    // Linux commands
    vector<Command> linuxCmds = {
        {L"ls", L"List directory contents", L"File System", 
         L"$ ls -l      # List in long format\n$ ls -a      # List all files including hidden", 
         L"Core utility"},
        {L"grep", L"Search text using patterns", L"Text Processing", 
         L"$ grep 'pattern' file.txt\n$ ps aux | grep 'process'", 
         L"Core utility"},
        {L"chmod", L"Change file permissions", L"Permissions", 
         L"$ chmod 755 script.sh\n$ chmod u+x file", 
         L"Core utility"},
        {L"ssh", L"Secure shell remote login", L"Networking", 
         L"$ ssh user@192.168.1.100\n$ ssh -i key.pem user@server.com", 
         L"openssh-client"},
        {L"find", L"Search for files in directory hierarchy", L"File System", 
         L"$ find . -name '*.py'\n$ find /var/log -size +10M", 
         L"Core utility"},
        {L"apt-get", L"Package management utility (Debian)", L"Package Management", 
         L"$ sudo apt-get update\n$ sudo apt-get install nginx", 
         L"apt"},
        {L"systemctl", L"Control systemd system and service manager", L"System Management", 
         L"$ systemctl start nginx\n$ systemctl status ssh", 
         L"systemd"},
        {L"iptables", L"Administration tool for IPv4 packet filtering", L"Networking", 
         L"$ iptables -L\n$ iptables -A INPUT -p tcp --dport 22 -j ACCEPT", 
         L"iptables"}
    };
    g_commands[LINUX_TAB] = linuxCmds;
    
    // Windows commands
    vector<Command> winCmds = {
        {L"dir", L"List directory contents", L"File System", 
         L"> dir /w     # Wide list format\n> dir /a     # List all files including hidden", 
         L"Built-in"},
        {L"ipconfig", L"Display network configuration", L"Networking", 
         L"> ipconfig\n> ipconfig /all\n> ipconfig /release", 
         L"Built-in"},
        {L"tasklist", L"Display running processes", L"Process Management", 
         L"> tasklist\n> tasklist /svc", 
         L"Built-in"},
        {L"netsh", L"Network shell configuration tool", L"Networking", 
         L"> netsh wlan show profiles\n> netsh advfirewall set allprofiles state off", 
         L"Built-in"},
        {L"choco", L"Chocolatey package manager", L"Package Management", 
         L"> choco install git\n> choco upgrade all", 
         L"Chocolatey (https://chocolatey.org/install)"},
        {L"powershell", L"Task automation framework", L"Scripting", 
         L"> powershell Get-Process\n> powershell Get-Service", 
         L"Built-in"},
        {L"netstat", L"Display network connections", L"Networking", 
         L"> netstat -ano\n> netstat -ab", 
         L"Built-in"},
        {L"sfc", L"System File Checker", L"System Management", 
         L"> sfc /scannow", 
         L"Built-in"}
    };
    g_commands[WINDOWS_TAB] = winCmds;
    
    // macOS commands
    vector<Command> macCmds = {
        {L"ls", L"List directory contents", L"File System", 
         L"$ ls -l\n$ ls -a", 
         L"Core utility"},
        {L"brew", L"Homebrew package manager", L"Package Management", 
         L"$ brew install wget\n$ brew update", 
         L"Homebrew (https://brew.sh/)"},
        {L"say", L"Convert text to speech", L"Utilities", 
         L"$ say \"Hello World\"\n$ say -v Daniel \"How are you?\"", 
         L"Built-in"},
        {L"diskutil", L"Disk management utility", L"Storage", 
         L"$ diskutil list\n$ diskutil eject /dev/disk2", 
         L"Built-in"},
        {L"networksetup", L"Network configuration tool", L"Networking", 
         L"$ networksetup -listallnetworkservices\n$ networksetup -setdnsservers Wi-Fi 8.8.8.8", 
         L"Built-in"},
        {L"launchctl", L"Service management framework", L"System Management", 
         L"$ launchctl list\n$ launchctl load ~/Library/LaunchAgents/my.script.plist", 
         L"Built-in"},
        {L"airport", L"Wi-Fi diagnostic tool", L"Networking", 
         L"$ airport -s\n$ airport -I", 
         L"Built-in (located at /System/Library/PrivateFrameworks/Apple80211.framework/Resources/airport)"}
    };
    g_commands[MACOS_TAB] = macCmds;
    
    // Favorites starts empty
    g_commands[FAVORITES_TAB] = vector<Command>();
}

void PopulateCommandList() {
    HWND hList = g_hTabs[g_currentTab];
    
    // Set as current command list
    g_hCommandList = hList;
    
    // Hide all lists except the current one
    for (HWND tab : g_hTabs) {
        ShowWindow(tab, tab == hList ? SW_SHOW : SW_HIDE);
    }
    
    // Clear existing items
    ListView_DeleteAllItems(hList);
    
    // Get commands for current tab
    vector<Command> commands;
    if (g_currentTab == FAVORITES_TAB) {
        for (int index : g_favorites) {
            // Determine which OS the favorite belongs to
            OSTab sourceTab = LINUX_TAB;
            if (index >= 1000) {
                sourceTab = WINDOWS_TAB;
                index -= 1000;
            }
            else if (index >= 2000) {
                sourceTab = MACOS_TAB;
                index -= 2000;
            }
            
            if (index >= 0 && index < static_cast<int>(g_commands[sourceTab].size())) {
                commands.push_back(g_commands[sourceTab][index]);
            }
        }
    }
    else {
        commands = g_commands[g_currentTab];
    }
    
    // Add items to list
    LVITEM lvi = {};
    lvi.mask = LVIF_TEXT;
    
    for (int i = 0; i < static_cast<int>(commands.size()); i++) {
        lvi.iItem = i;
        lvi.iSubItem = 0;
        lvi.pszText = const_cast<LPWSTR>(commands[i].name.c_str());
        ListView_InsertItem(hList, &lvi);
    }
    
    // Auto-size column
    ListView_SetColumnWidth(hList, 0, LVSCW_AUTOSIZE);
}

void ShowCommandDetails(int index) {
    if (index == -1) return;
    
    wstring details;
    Command cmd;
    wstring osName;
    
    if (g_currentTab == FAVORITES_TAB) {
        if (index < 0 || index >= static_cast<int>(g_favorites.size())) return;
        
        int favIndex = g_favorites[index];
        OSTab sourceTab = LINUX_TAB;
        int sourceIndex = favIndex;
        
        if (favIndex >= 1000) {
            sourceTab = WINDOWS_TAB;
            sourceIndex = favIndex - 1000;
        }
        else if (favIndex >= 2000) {
            sourceTab = MACOS_TAB;
            sourceIndex = favIndex - 2000;
        }
        
        if (sourceIndex >= 0 && sourceIndex < static_cast<int>(g_commands[sourceTab].size())) {
            cmd = g_commands[sourceTab][sourceIndex];
            
            switch (sourceTab) {
                case LINUX_TAB: osName = L"Linux"; break;
                case WINDOWS_TAB: osName = L"Windows"; break;
                case MACOS_TAB: osName = L"macOS"; break;
                default: osName = L"Unknown"; break;
            }
        }
    }
    else {
        if (index < 0 || index >= static_cast<int>(g_commands[g_currentTab].size())) return;
        cmd = g_commands[g_currentTab][index];
        
        switch (g_currentTab) {
            case LINUX_TAB: osName = L"Linux"; break;
            case WINDOWS_TAB: osName = L"Windows"; break;
            case MACOS_TAB: osName = L"macOS"; break;
            default: osName = L"Unknown"; break;
        }
    }
    
    // Format details
    details += L"Command: " + cmd.name + L"\n";
    details += L"OS: " + osName + L"\n";
    details += L"Category: " + cmd.category + L"\n\n";
    details += L"Description:\n" + cmd.description + L"\n\n";
    details += L"Examples:\n" + cmd.examples + L"\n\n";
    details += L"Dependencies:\n" + cmd.dependencies + L"\n\n";
    
    // Add favorite status
    int globalIndex = index;
    if (g_currentTab != FAVORITES_TAB) {
        // Create a global index that includes OS information
        globalIndex = index;
        if (g_currentTab == WINDOWS_TAB) globalIndex += 1000;
        else if (g_currentTab == MACOS_TAB) globalIndex += 2000;
    }
    
    if (IsFavorite(globalIndex)) {
        details += L"[★] This command is in your favorites\n";
        details += L"Press 'Add/Remove Favorite' to remove it";
    }
    else {
        details += L"[☆] Press 'Add/Remove Favorite' to add this command to favorites";
    }
    
    SetWindowText(g_hDetailsEdit, details.c_str());
}

void FilterCommands() {
    // Get search text
    wchar_t searchText[256];
    GetWindowText(g_hSearchEdit, searchText, 256);
    
    // Get selected category
    wchar_t category[256];
    int sel = SendMessage(g_hCategoryCombo, CB_GETCURSEL, 0, 0);
    SendMessage(g_hCategoryCombo, CB_GETLBTEXT, sel, (LPARAM)category);
    
    // Get commands for current tab
    vector<Command> commands;
    if (g_currentTab == FAVORITES_TAB) {
        for (int index : g_favorites) {
            OSTab sourceTab = LINUX_TAB;
            int sourceIndex = index;
            
            if (index >= 1000) {
                sourceTab = WINDOWS_TAB;
                sourceIndex = index - 1000;
            }
            else if (index >= 2000) {
                sourceTab = MACOS_TAB;
                sourceIndex = index - 2000;
            }
            
            if (sourceIndex >= 0 && sourceIndex < static_cast<int>(g_commands[sourceTab].size())) {
                commands.push_back(g_commands[sourceTab][sourceIndex]);
            }
        }
    }
    else {
        commands = g_commands[g_currentTab];
    }
    
    // Clear existing items
    ListView_DeleteAllItems(g_hCommandList);
    
    // Add filtered items
    LVITEM lvi = {};
    lvi.mask = LVIF_TEXT;
    
    for (int i = 0; i < static_cast<int>(commands.size()); i++) {
        const Command& cmd = commands[i];
        
        // Check search text
        if (wcslen(searchText) > 0 && wcsstr(searchText, L"Search...") == nullptr) {
            wstring lowerName = cmd.name;
            wstring lowerDesc = cmd.description;
            wstring lowerCat = cmd.category;
            
            // Convert to lowercase for case-insensitive search
            transform(lowerName.begin(), lowerName.end(), lowerName.begin(), towlower);
            transform(lowerDesc.begin(), lowerDesc.end(), lowerDesc.begin(), towlower);
            transform(lowerCat.begin(), lowerCat.end(), lowerCat.begin(), towlower);
            
            wstring lowerSearch = searchText;
            transform(lowerSearch.begin(), lowerSearch.end(), lowerSearch.begin(), towlower);
            
            if (lowerName.find(lowerSearch) == wstring::npos &&
                lowerDesc.find(lowerSearch) == wstring::npos &&
                lowerCat.find(lowerSearch) == wstring::npos) {
                continue;
            }
        }
        
        // Check category
        if (wcscmp(category, L"All") != 0 && cmd.category != category) {
            continue;
        }
        
        // Add item
        lvi.iItem = i;
        lvi.iSubItem = 0;
        lvi.pszText = const_cast<LPWSTR>(cmd.name.c_str());
        ListView_InsertItem(g_hCommandList, &lvi);
    }
    
    // Auto-size column
    ListView_SetColumnWidth(g_hCommandList, 0, LVSCW_AUTOSIZE);
}

void AddFavorite(int index) {
    // Create a global index that includes OS information
    int globalIndex = index;
    if (g_currentTab == WINDOWS_TAB) globalIndex += 1000;
    else if (g_currentTab == MACOS_TAB) globalIndex += 2000;
    
    // Add if not already in favorites
    if (find(g_favorites.begin(), g_favorites.end(), globalIndex) == g_favorites.end()) {
        g_favorites.push_back(globalIndex);
    }
}

void RemoveFavorite(int index) {
    // Create a global index that includes OS information
    int globalIndex = index;
    if (g_currentTab == WINDOWS_TAB) globalIndex += 1000;
    else if (g_currentTab == MACOS_TAB) globalIndex += 2000;
    
    // Remove from favorites
    auto it = find(g_favorites.begin(), g_favorites.end(), globalIndex);
    if (it != g_favorites.end()) {
        g_favorites.erase(it);
    }
}

bool IsFavorite(int index) {
    // For Favorites tab, index is already global
    if (g_currentTab == FAVORITES_TAB) {
        if (index < 0 || index >= static_cast<int>(g_favorites.size())) return false;
        int globalIndex = g_favorites[index];
        return (find(g_favorites.begin(), g_favorites.end(), globalIndex) != g_favorites.end());
    }
    
    // For other tabs, create global index
    int globalIndex = index;
    if (g_currentTab == WINDOWS_TAB) globalIndex += 1000;
    else if (g_currentTab == MACOS_TAB) globalIndex += 2000;
    
    return (find(g_favorites.begin(), g_favorites.end(), globalIndex) != g_favorites.end());
}

void RunSimulation() {
    if (g_currentSelection == -1) return;
    
    wstring simulation;
    Command cmd;
    wstring osName;
    
    if (g_currentTab == FAVORITES_TAB) {
        if (g_currentSelection < 0 || g_currentSelection >= static_cast<int>(g_favorites.size())) return;
        
        int favIndex = g_favorites[g_currentSelection];
        OSTab sourceTab = LINUX_TAB;
        int sourceIndex = favIndex;
        
        if (favIndex >= 1000) {
            sourceTab = WINDOWS_TAB;
            sourceIndex = favIndex - 1000;
        }
        else if (favIndex >= 2000) {
            sourceTab = MACOS_TAB;
            sourceIndex = favIndex - 2000;
        }
        
        if (sourceIndex >= 0 && sourceIndex < static_cast<int>(g_commands[sourceTab].size())) {
            cmd = g_commands[sourceTab][sourceIndex];
            osName = (sourceTab == WINDOWS_TAB) ? L"> " : L"$ ";
        }
    }
    else {
        if (g_currentSelection < 0 || g_currentSelection >= static_cast<int>(g_commands[g_currentTab].size())) return;
        cmd = g_commands[g_currentTab][g_currentSelection];
        osName = (g_currentTab == WINDOWS_TAB) ? L"> " : L"$ ";
    }
    
    simulation += osName + cmd.name + L"\n\n";
    
    // Add command-specific simulation output
    if (cmd.name == L"ls") {
        simulation += L"file1.txt\tfile2.txt\tdirectory/\n";
        simulation += L"report.pdf\timage.png\t\n";
    }
    else if (cmd.name == L"grep") {
        simulation += L"search_result: line 42: found the pattern\n";
        simulation += L"search_result: line 87: another match\n";
    }
    else if (cmd.name == L"ipconfig") {
        simulation += L"Ethernet adapter Ethernet0:\n\n";
        simulation += L"   IPv4 Address. . . . . . . . . . . : 192.168.1.100\n";
        simulation += L"   Subnet Mask . . . . . . . . . . . : 255.255.255.0\n";
        simulation += L"   Default Gateway . . . . . . . . . : 192.168.1.1\n";
    }
    else if (cmd.name == L"brew") {
        simulation += L"==> Downloading wget-1.21.2.catalina.bottle.tar.gz\n";
        simulation += L"######################################################################## 100.0%\n";
        simulation += L"==> Pouring wget-1.21.2.catalina.bottle.tar.gz\n";
        simulation += L"🍺  /usr/local/Cellar/wget/1.21.2: 50 files, 3.7MB\n";
    }
    else {
        simulation += L"Command executed successfully\n";
        simulation += L"Output generated for demonstration purposes\n";
    }
    
    simulation += L"\nSimulation complete. Output is for demonstration only.";
    
    SetWindowText(g_hDetailsEdit, simulation.c_str());
}

void DrawMatrixEffect(HDC hdc, RECT rect) {
    // Fill background
    HBRUSH hBrush = CreateSolidBrush(BG_COLOR);
    FillRect(hdc, &rect, hBrush);
    DeleteObject(hBrush);
    
    // Set font
    HFONT hFont = CreateFont(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, DEFAULT_CHARSET, 
                            OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY, 
                            FIXED_PITCH | FF_DONTCARE, L"Consolas");
    HFONT hOldFont = (HFONT)SelectObject(hdc, hFont);
    SetTextColor(hdc, TEXT_COLOR);
    SetBkMode(hdc, TRANSPARENT);
    
    // Draw matrix characters
    int charWidth = 10;
    int charHeight = 14;
    int cols = (rect.right - rect.left) / charWidth;
    int rows = (rect.bottom - rect.top) / charHeight;
    
    for (int row = 0; row < min(rows, MATRIX_ROWS); row++) {
        for (int col = 0; col < min(cols, MATRIX_COLS); col++) {
            wchar_t ch[2] = { g_matrix[row][col], L'\0' };
            TextOut(hdc, rect.left + col * charWidth, rect.top + row * charHeight, ch, 1);
        }
    }
    
    // Restore old font
    SelectObject(hdc, hOldFont);
    DeleteObject(hFont);
}

void UpdateMatrixEffect() {
    // Shift all rows up
    for (int row = 0; row < MATRIX_ROWS - 1; row++) {
        for (int col = 0; col < MATRIX_COLS; col++) {
            g_matrix[row][col] = g_matrix[row + 1][col];
        }
    }
    
    // Generate new bottom row
    for (int col = 0; col < MATRIX_COLS; col++) {
        if (rand() % 5 == 0) { // 20% chance to change a character
            g_matrix[MATRIX_ROWS - 1][col] = MATRIX_CHARS[rand() % (sizeof(MATRIX_CHARS) / sizeof(MATRIX_CHARS[0]) - 1];
        }
        else {
            g_matrix[MATRIX_ROWS - 1][col] = L' ';
        }
    }
}

void SaveOutputToFile() {
    // Get text from details edit
    int textLength = GetWindowTextLength(g_hDetailsEdit) + 1;
    wchar_t* buffer = new wchar_t[textLength];
    GetWindowText(g_hDetailsEdit, buffer, textLength);
    
    // Prepare save dialog
    OPENFILENAME ofn;
    wchar_t szFile[260] = {0};
    
    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = g_hMainWindow;
    ofn.lpstrFile = szFile;
    ofn.nMaxFile = sizeof(szFile);
    ofn.lpstrFilter = L"Text Files (*.txt)\0*.txt\0All Files (*.*)\0*.*\0";
    ofn.nFilterIndex = 1;
    ofn.lpstrDefExt = L"txt";
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_OVERWRITEPROMPT;
    
    // Show save dialog
    if (GetSaveFileName(&ofn)) {
        // Write to file
        ofstream file(ofn.lpstrFile);
        if (file.is_open()) {
            // Convert wchar_t to char (simple conversion for demo)
            for (int i = 0; i < textLength && buffer[i] != L'\0'; i++) {
                file.put(static_cast<char>(buffer[i]));
            }
            file.close();
            
            // Update status
            SendMessage(g_hStatusBar, SB_SETTEXT, 0, (LPARAM)L"Output saved successfully");
        }
        else {
            MessageBox(g_hMainWindow, L"Failed to save file", L"Error", MB_ICONERROR);
        }
    }
    
    delete[] buffer;
}

void SetDarkTheme(HWND hwnd) {
    // Set background color
    SetClassLongPtr(hwnd, GCLP_HBRBACKGROUND, (LONG_PTR)CreateSolidBrush(LIST_BG_COLOR));
    
    // Force redraw
    InvalidateRect(hwnd, nullptr, TRUE);
}