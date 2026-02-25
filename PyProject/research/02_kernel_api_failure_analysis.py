import win32gui, win32con, win32api, win32process, ctypes

"""
연구 기록: 시스템 커널 메시지 주입 시도 (AttachThreadInput)
--------------------------------------------------
- 시도: 윈도우 OS의 표준 메시지(WM_GETTEXT)로 텍스트 강탈 시도함.
- 내용: 봇이랑 카톡 스레드를 하나로 묶어서(Attach) 내부 권한 따냄.
- 결과: 절반의 성공. 창 제목(Caption)은 가져오는데 내부 내용은 못 가져옴.
- 결론: 카톡이 표준 메시지 프로토콜도 보안 상의 이유로 응답 안 하게 막아둔 듯함.
--------------------------------------------------
"""

def kernel_api_research():
    print("--- [시도 2] 커널 메시지 및 스레드 결합 테스트 ---")
    
    hwnd = win32gui.FindWindow("EVA_Window_Dblclk", "지혁")
    if not hwnd: return

    # 스레드 ID랑 프로세스 ID 분리해서 가져오기
    dest_thread, pid = win32process.GetWindowThreadProcessId(hwnd)
    curr_thread = win32api.GetCurrentThreadId()
    
    print(f"현재 봇 스레드: {curr_thread}, 카톡 대상 스레드: {dest_thread}")

    try:
        # 스레드 연결해서 포커스 권한이랑 메시지 큐 공유받기
        win32process.AttachThreadInput(curr_thread, dest_thread, True)
        
        # 텍스트 받아올 8KB 버퍼 준비 (ctypes Interop 활용)
        buf_size = 8192
        buf = ctypes.create_unicode_buffer(buf_size)
        
        # WM_GETTEXT 신호 주입 (0.5초 타임아웃 걸어서 시도)
        result = win32gui.SendMessageTimeout(hwnd, win32con.WM_GETTEXT, buf_size, buf, 
                                             win32con.SMTO_ABORTIFHUNG, 500)
        
        if result[0] > 0:
            print(f"탈취 성공한 텍스트: '{buf.value}'")
        else:
            print("[결론] 카톡이 시스템 신호 무시함. 데이터 보호 확인.")
            
        # 작업 끝났으니 스레드 연결 해제 (중요함!)
        win32process.AttachThreadInput(curr_thread, dest_thread, False)
        
    except Exception as e:
        print(f"시스템 예외: {e}")

if __name__ == "__main__":
    kernel_api_research()
