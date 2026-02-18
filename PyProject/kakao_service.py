import window_utils
import win32gui, win32api, pyperclip, time

class KakaoService:
    def __init__(self, room_name):
        self.room_name = room_name
        self.class_name = "EVA_Window_Dblclk" # 카톡 대화창 전용 클래스
        self.last_messages_window = [] # 중복 체크를 위한 이전 메시지 저장소

    def get_target_hwnd(self):
        return window_utils.find_hwnd(self.class_name, self.room_name)

    def is_user_ready(self, threshold=3.0):
        # 마지막 입력으로부터 일정 시간이 지났는지 체크 (사용자 방해 방지용)
        return window_utils.get_idle_time() >= threshold

    def collect_chat_data(self):
        hwnd = self.get_target_hwnd()
        if not hwnd: return None

        # 작업 전 포커스 상태랑 클립보드 백업
        curr_hwnd = win32gui.GetForegroundWindow()
        old_clip = pyperclip.paste()

        # 윈도우 포커스 잡고 가상 클릭 후 복사 실행
        window_utils.set_stealth_focus(hwnd)
        time.sleep(0.3)
        
        if win32gui.GetForegroundWindow() == hwnd:
            window_utils.virtual_click(hwnd)
            time.sleep(0.1)
            
            # Ctrl+A, C 직접 주입
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x41, 0, 0, 0)
            win32api.keybd_event(0x43, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(0x43, 0, 2, 0)
            win32api.keybd_event(0x41, 0, 2, 0)
            win32api.keybd_event(0x11, 0, 2, 0)
            time.sleep(0.2)

        # 복사한 데이터 챙기고 원래대로 복구
        raw_text = pyperclip.paste()
        pyperclip.copy(old_clip) 
        
        # 원래 작업하던 창으로 포커스 돌려주기
        if curr_hwnd and curr_hwnd != hwnd:
            try: win32gui.SetForegroundWindow(curr_hwnd)
            except: pass
            
        return raw_text

    def extract_new_messages(self, raw_text):
        if not raw_text: return []
        
        # 텍스트 라인별로 자르고 빈 줄 제거
        lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]
        # 터미널 프롬프트 등 오염된 데이터는 뺌
        lines = [l for l in lines if "PS C:\\" not in l and "psutil" not in l]

        if not lines: return []

        # 처음 켜졌을 땐 기준점만 잡음
        if not self.last_messages_window:
            self.last_messages_window = lines[-10:]
            return []

        # 슬라이딩 윈도우 방식으로 이전에 어디까지 읽었는지 찾음
        # 같은 메시지 도배 상황을 고려해서 최근 3개 뭉치를 비교함
        new_start_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[max(0, i-2):i+1] == self.last_messages_window[-3:]:
                new_start_idx = i + 1
                break
        
        # 새로 들어온 메시지만 리스트로 반환
        new_msgs = lines[new_start_idx:]
        
        # 다음 번 스캔을 위해 기준점 업데이트
        if new_msgs:
            self.last_messages_window = lines[-10:]
            
        return new_msgs
