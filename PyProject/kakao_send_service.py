import window_utils
import win32gui, win32con, win32api, pyperclip, time

class KakaoSendService:
    def __init__(self, room_name):
        self.room_name = room_name
        self.chat_room_class = "EVA_Window_Dblclk"
        self.edit_class = "RICHEDIT50W" # 카톡 입력칸 클래스명

    # 메시지 전송 로직 (붙여넣기 방식)
    def send_message(self, message):
        parent_hwnd = window_utils.find_hwnd(self.chat_room_class, self.room_name)
        if not parent_hwnd:
            parent_hwnd = window_utils.find_hwnd(None, self.room_name)
        if not parent_hwnd: return False

        # 실제 텍스트 치는 입력칸 찾기
        edit_hwnd = win32gui.FindWindowEx(parent_hwnd, None, self.edit_class, None)
        if not edit_hwnd: return False

        # 현재 작업 중인 창 핸들 기억 (나중에 돌려주기용)
        original_active_hwnd = win32gui.GetForegroundWindow()
        
        # 유저 클립보드 백업
        user_backup = pyperclip.paste()

        try:
            # 보낼 메시지 복사
            pyperclip.copy(message)
            time.sleep(0.05)

            # 카톡 소환하고 입력칸 클릭해서 커서 만들기
            window_utils.set_stealth_focus(parent_hwnd)
            time.sleep(0.2)
            
            # 가상 클릭 (마우스 안 움직임)
            rect = win32gui.GetClientRect(edit_hwnd)
            lparam = win32api.MAKELONG(10, 10)
            win32gui.PostMessage(edit_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
            win32gui.PostMessage(edit_hwnd, win32con.WM_LBUTTONUP, 0, lparam)
            time.sleep(0.1)

            # 붙여넣기(Ctrl+V) 후 엔터
            if win32gui.GetForegroundWindow() == parent_hwnd:
                win32api.keybd_event(0x11, 0, 0, 0) # Ctrl Down
                win32api.keybd_event(0x56, 0, 0, 0) # V Down
                time.sleep(0.05)
                win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.1)

                win32api.keybd_event(0x0D, 0, 0, 0) # Enter Down
                win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                time.sleep(0.1)
                
                # 전송 끝났으니 원래 하던 창으로 포커스 롤백
                if original_active_hwnd and original_active_hwnd != parent_hwnd:
                    try:
                        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0) # Alt 트릭
                        win32gui.SetForegroundWindow(original_active_hwnd)
                        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                    except: pass
                
                return True
        except:
            pass
        finally:
            # 유저 클립보드 원상복구
            pyperclip.copy(user_backup)
        
        return False
