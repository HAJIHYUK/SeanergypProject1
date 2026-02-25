import win32gui, win32process, psutil, time

"""
연구 기록: 프로세스 오탐지(크롬/터미널) 방지 기술 연구
--------------------------------------------------
- 배경: 창 제목 '지혁'만 보고 긁었더니 엉뚱한 크롬 창에서 복사하는 현상 발생.
- 해결: 제목뿐만 아니라 실제 프로세스명(KakaoTalk.exe)까지 2중 체크함.
- 결과: 성공. 어떤 상황에서도 진짜 카톡 대화창만 정확히 타겟팅 가능해짐.
--------------------------------------------------
"""

def process_targeting_research():
    print("--- [시도 3] 진짜 카톡 프로세스만 골라내기 테스트 ---")
    
    target_process = "KakaoTalk.exe"
    target_room = "지혁"
    
    def on_window_found(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            
            # 핸들로 프로세스 ID 따오고 이름까지 확인함
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                p_name = proc.name()
                
                # 제목에 방 이름 있고 프로세스가 카톡인 경우만 합격
                if target_room in title and target_process.lower() in p_name.lower():
                    print(f"\n[찾았다!] {title}")
                    print(f" - PID: {pid}, Handle: {hex(hwnd)}")
                    print(f" - 상태: {'최소화됨' if win32gui.IsIconic(hwnd) else '활성화됨'}")
            except:
                pass
        return True

    print(f"시스템의 모든 창 훑어서 {target_process} 추적함...")
    win32gui.EnumWindows(on_window_found, None)

if __name__ == "__main__":
    process_targeting_research()
