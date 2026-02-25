import win32gui, win32con, win32api, time

"""
연구 기록: 카톡 메시지 송신 삽질 및 실패 원인 분석
--------------------------------------------------
- 배경: 창 안 띄우고(백그라운드) 조용히 메시지 보내보려 함.
- 해결 시도 1: WM_SETTEXT로 글자 강제 주입.
  결과1: 글자는 들어가는데 카톡 내부 '입력 이벤트'가 안 터짐, 전송 버튼이 계속 회색(비활성)이고 엔터 쳐도 반응 없음.
- 해결 시도 2: SendInput으로 하드웨어 타이핑 에뮬레이션.
  결과2: 포커스는 가는데 글자가 안 써짐. RICHEDIT50W에서 외부 입력을 차단하는 듯.
- 결론: 텍스트 직접 주입은 보안상 막혀있음. '클립보드 복붙'이 가장 확실한 길임 확인.
--------------------------------------------------
"""

def test_send_failure():
    print("--- [시도 4] 송신 실패 케이스 재현 테스트 ---")
    
    room_name = "지혁"
    parent_hwnd = win32gui.FindWindow("EVA_Window_Dblclk", room_name)
    if not parent_hwnd:
        print("에러: 채팅방을 못 찾겠음.")
        return

    # 채팅 입력칸(RICHEDIT50W) 핸들 따오기
    edit_hwnd = win32gui.FindWindowEx(parent_hwnd, None, "RICHEDIT50W", None)
    
    if edit_hwnd:
        print(f"입력창 핸들 확인: {hex(edit_hwnd)}")
        
        # [테스트 1] 글자만 쓱 밀어넣어보기
        print("1. WM_SETTEXT 주입 중...")
        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, "보내져라 제발")
        
        # [테스트 2] 엔터키 신호 줘보기
        print("2. 엔터 신호(PostMessage) 주입 중...")
        win32gui.PostMessage(edit_hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
        
        print("\n[결과 확인]")
        print("- 입력창에 글자는 생겼는데 전송 버튼이 안 살아남.")
        print("- 카톡이 '어? 글자가 들어왔네?'라고 인지를 못 함 (UI 상태 동기화 실패).")
    else:
        print("입력창(RichEdit)을 못 찾았음.")

if __name__ == "__main__":
    test_send_failure()
