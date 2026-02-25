import win32gui, win32con, win32api, win32process, time

# 제목이랑 클래스명으로 윈도우 핸들(HWND) 찾기
def find_hwnd(class_name, title):
    return win32gui.FindWindow(class_name, title)

# 유저가 마지막으로 움직인 지 얼마나 됐는지 확인 (초 단위)
def get_idle_time():
    last_input = win32api.GetLastInputInfo()
    curr_tick = win32api.GetTickCount()
    return (curr_tick - last_input) / 1000.0

# 마우스 안 움직이고 해당 좌표에 클릭 신호만 꽂기
def virtual_click(hwnd):
    rect = win32gui.GetClientRect(hwnd)
    lparam = win32api.MAKELONG((rect[2]-rect[0])//2, (rect[3]-rect[1])//2)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

# 윈도우 포커스 방어 기제 뚫고 강제로 주인공 창 만들기
def set_stealth_focus(hwnd):
    try:
        # 내 스레드랑 대상 창 스레드 연결해서 권한 뺏어오기
        dest_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        curr_thread = win32api.GetCurrentThreadId()
        
        # 숨어있거나 최소화된 창 꺼내기
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
        win32process.AttachThreadInput(curr_thread, dest_thread, True)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetFocus(hwnd)
        win32process.AttachThreadInput(curr_thread, dest_thread, False) # 작업 후 바로 해제
        return True
    except:
        # 실패 시 Alt 키 트릭으로 한 번 더 시도
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        return False

# 창을 화면 밖 구석(-5000)으로 던져버림
def move_window_to_ghost(hwnd):
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, -5000, -5000, 0, 0, 
                          win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
