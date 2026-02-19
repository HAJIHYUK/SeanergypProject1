import window_utils
import win32gui, win32api, pyperclip, time
import hashlib
import re
from models import KakaoMessage
from kakao_repository import KakaoRepository
from database_config import SessionLocal

class KakaoReceiveService:
    def __init__(self, room_name):
        self.room_name = room_name
        self.class_name = "EVA_Window_Dblclk"
        self.db = SessionLocal()
        self.repository = KakaoRepository(self.db)
        
        # 메시지 파싱 패턴
        self.msg_pattern = re.compile(r"^\[(?P<sender>.+?)\] \[(?P<time>(?:오전|오후) \d{1,2}:\d{2})\] (?P<content>.*)$")

    def _get_hwnd(self):
        return window_utils.find_hwnd(self.class_name, self.room_name)

    def is_idle(self, threshold=3.0):
        return window_utils.get_idle_time() >= threshold

    def collect_and_save(self):
        """데이터를 긁어오고 매번 DB와 대조하여 저장"""
        hwnd = self._get_hwnd()
        if not hwnd: return []

        old_clip = pyperclip.paste()
        window_utils.set_stealth_focus(hwnd)
        time.sleep(0.3)
        
        raw_text = ""
        if win32gui.GetForegroundWindow() == hwnd:
            window_utils.virtual_click(hwnd)
            time.sleep(0.1)
            # 전체 선택 복사
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x41, 0, 0, 0)
            win32api.keybd_event(0x43, 0, 0, 0)
            time.sleep(0.1)
            win32api.keybd_event(0x43, 0, 2, 0)
            win32api.keybd_event(0x41, 0, 2, 0)
            win32api.keybd_event(0x11, 0, 2, 0)
            time.sleep(0.2)
            raw_text = pyperclip.paste()

        pyperclip.copy(old_clip)
        return self._sync_with_db_and_save(raw_text)

    def _sync_with_db_and_save(self, raw_text):
        """매번 DB에서 꼬리 데이터를 가져와 현재 텍스트와 대조"""
        if not raw_text: return []
        
        # 1. 현재 카톡창 텍스트 정제
        lines = [l.strip() for l in raw_text.strip().splitlines() if l.strip()]
        lines = [l for l in lines if "PS C:\\" not in l and "psutil" not in l]
        if not lines: return []

        # 2. [DB 최신화] DB에서 마지막 20줄을 실시간으로 가져옴
        db_tail = self.repository.get_last_n_messages(20)
        
        # 3. [동기화 지점 찾기]
        # DB의 마지막 5줄 뭉치가 현재 긁어온 리스트의 어디에 있는지 뒤에서부터 정밀 탐색
        new_start_idx = 0
        if db_tail:
            # 안전을 위해 마지막 5줄을 앵커로 잡음 (도배 방어력 강화)
            anchor_size = min(5, len(db_tail))
            anchor = db_tail[-anchor_size:]
            
            for i in range(len(lines) - 1, -1, -1):
                # 현재 긁어온 데이터에서 앵커와 완벽히 일치하는 구간 탐색
                if lines[max(0, i-anchor_size+1):i+1] == anchor:
                    new_start_idx = i + 1
                    break
        
        # 4. 신규 데이터(지점 이후)만 골라내어 저장
        new_lines = lines[new_start_idx:]
        new_saved_msgs = []
        
        current_sender, current_time = "시스템", "알수없음"

        for line in new_lines:
            match = self.msg_pattern.match(line)
            if match:
                sender = match.group("sender")
                sent_at = match.group("time")
                content = match.group("content")
                current_sender, current_time = sender, sent_at
            else:
                sender, sent_at, content = current_sender, current_time, line

            # 해시 생성 (내용 중복 허용을 위해 UNIQUE 제약 없음)
            msg_hash = hashlib.sha256(line.encode('utf-8')).hexdigest()
            
            entity = KakaoMessage(
                msg_hash=msg_hash,
                sender=sender,
                sent_at=sent_at,
                content=content,
                room_name=self.room_name
            )
            
            if self.repository.save(entity):
                new_saved_msgs.append(f"[{sender}] {content}")
        
        return new_saved_msgs
