import window_utils
import win32gui, win32api, pyperclip, time

class KakaoReceiveService:
    def __init__(self, room_name):
        self.room_name = room_name
        self.class_name = "EVA_Window_Dblclk"
        self.last_messages_window = [] # 이전에 긁어온 메시지들 저장 (중복 방지)

    def _get_hwnd(self):
        return window_utils.find_hwnd(self.class_name, self.room_name)

    # 유저가 3초 이상 자리 비웠는지 확인
    def is_idle(self, threshold=3.0):
        return window_utils.get_idle_time() >= threshold

    # 카톡방 활성화해서 데이터 복사해오기
    def collect_new_messages(self):
        hwnd = self._get_hwnd()
        if not hwnd: return []

        # 클립보드 날아가는 거 방지용 백업
        old_clip = pyperclip.paste()
        
        # 포커스 뺏고 클릭해서 복사 (Ctrl+A, C)
        window_utils.set_stealth_focus(hwnd)
        time.sleep(0.3)
        
        raw_text = ""
        if win32gui.GetForegroundWindow() == hwnd:
            window_utils.virtual_click(hwnd)
            time.sleep(0.1)
            
            # 하드웨어 신호 직접 쏨
            win32api.keybd_event(0x11, 0, 0, 0) # Ctrl
            win32api.keybd_event(0x41, 0, 0, 0) # A
            win32api.keybd_event(0x43, 0, 0, 0) # C
            time.sleep(0.1)
            win32api.keybd_event(0x43, 0, 2, 0)
            win32api.keybd_event(0x41, 0, 2, 0)
            win32api.keybd_event(0x11, 0, 2, 0)
            time.sleep(0.2)
            raw_text = pyperclip.paste()

        # 복사 끝났으니 유저 클립보드 원복
        pyperclip.copy(old_clip)
        return self._parse_data(raw_text)

    # 전체 텍스트에서 새 메시지만 골라내기
    def _parse_data(self, raw_text):
        if not raw_text: return []
        
        # 빈 줄 제거하고 리스트화
        lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]
        # 터미널 프롬프트 등 쓰레기 데이터 필터링
        lines = [l for l in lines if "PS C:\\" not in l and "psutil" not in l]

        if not lines: return []
        
        # 처음 시작할 땐 현재 보이는 것들만 저장하고 끝냄
        if not self.last_messages_window:
            self.last_messages_window = lines[-10:]
            return []

        # 이전에 어디까지 읽었는지 지점 찾기 (도배 대응 위해 3개 뭉치 비교)
        idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[max(0, i-2):i+1] == self.last_messages_window[-3:]:
                idx = i + 1
                break
        
        new_msgs = lines[idx:]
        if new_msgs:
            self.last_messages_window = lines[-10:] # 기준점 갱신
            
        return new_msgs
