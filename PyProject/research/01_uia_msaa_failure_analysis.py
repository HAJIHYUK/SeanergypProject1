import uiautomation
import win32gui
import time

"""
연구 기록: 카톡 내부 텍스트 추출 시도 (UIA/MSAA 방식)
--------------------------------------------------
- 시도: uiautomation 라이브러리 써서 텍스트 속성 직접 읽기 시도함.
- 내용: AutomationId '100' 구역(채팅방) 잡아서 하위 노드 싹 다 뒤져봄.
- 결과: 실패. 카톡은 글자를 객체로 안 만들고 직접 캔버스에 그리는 듯함.
- 결론: Name, Value 속성이 다 비어있어서 이 방식으로는 데이터 수집 불가능함 확인.
--------------------------------------------------
"""

def perform_deep_scan():
    print("--- [시도 1] 카톡 내부 구조 정밀 스캔 시작 ---")
    
    # win32gui로 핸들 먼저 획득 
    hwnd = win32gui.FindWindow("EVA_Window_Dblclk", "지혁")
    if not hwnd: return

    # 핸들로부터 UIA 객체 생성
    kakao_win = uiautomation.ControlFromHandle(hwnd)
    chat_area = kakao_win.Control(AutomationId="100")
    
    found_count = 0

    # 재귀적으로 자식 노드들 훑으면서 이름 있는지 체크함
    def scan_recursive(control, depth):
        nonlocal found_count
        for child in control.GetChildren():
            name_val = child.Name if child.Name else "N/A"
            
            # 레거시(MSAA) 방식의 Value도 체크해봄
            try:
                legacy = child.GetLegacyIAccessiblePattern()
                l_val = legacy.Value if legacy and legacy.Value else "N/A"
            except: l_val = "N/A"
            
            if name_val != "N/A" or l_val != "N/A":
                print(f"{'  ' * depth}[{child.ControlTypeName}] Name: {name_val} | Legacy: {l_val}")
                found_count += 1
            
            if found_count > 50: return
            scan_recursive(child, depth + 1)

    print("내부 노드 조사 중")
    if chat_area.Exists(1):
        scan_recursive(chat_area, 1)
    else:
        scan_recursive(kakao_win, 1)
    
    if found_count == 0:
        print("\n[결론] 텍스트 데이터 하나도 안 잡힘. 카톡 보안 렌더링 확인 완료.")

if __name__ == "__main__":
    perform_deep_scan()
