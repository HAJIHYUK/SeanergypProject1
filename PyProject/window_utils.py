import win32gui, win32con, win32api, win32process, time

# 창 핸들 찾기 (클래스명, 창 제목 기준)
def find_hwnd(class_name, title):
    return win32gui.FindWindow(class_name, title)

# 사용자가 마지막으로 움직인 후 경과 시간(초) 계산
def get_idle_time():
    last_input = win32api.GetLastInputInfo()
    curr_tick = win32api.GetTickCount()
    return (curr_tick - last_input) / 1000.0

# 마우스 커서 안 움직이고 내부 메시지로만 클릭 신호 보내기
def virtual_click(hwnd):
    rect = win32gui.GetClientRect(hwnd)
    # 창 중앙 좌표 계산해서 윈도우 메시지 생성
    lparam = win32api.MAKELONG((rect[2]-rect[0])//2, (rect[3]-rect[1])//2)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)

# 스레드 연결 기술(AttachThreadInput) 써서 강제로 포커스 가져오기
def set_stealth_focus(hwnd):
    try:
        # 대상 창의 스레드 ID랑 내 스레드 ID 가져옴
        dest_thread, _ = win32process.GetWindowThreadProcessId(hwnd)
        curr_thread = win32api.GetCurrentThreadId()
        
        # 최소화 상태면 복구하고 화면에 노출시킴
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
        # 두 스레드를 연결해서 입력 권한을 공유받음 (핵심 트릭)
        win32process.AttachThreadInput(curr_thread, dest_thread, True)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetFocus(hwnd)
        win32process.AttachThreadInput(curr_thread, dest_thread, False) # 작업 후 해제
        return True
    except:
        # 위 방식 실패 시 Alt 키 눌러서 포커스 뺏어오는 고전적인 방식 시도
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        win32gui.SetForegroundWindow(hwnd)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        return False

# 창을 모니터 밖 구석으로 보내버리기 (사용자 눈에 안 띄게)
def move_window_to_ghost(hwnd):
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, -5000, -5000, 0, 0, 
                          win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)
