# SeanergypProject1

# 카카오톡 메시지 실시간 수집 봇 (v1.0)

본 프로젝트는 윈도우 환경에서 카카오톡 PC 버전의 대화 내용을 실시간으로 추출하여 데이터베이스화하기 위한 기초 수집기입니다. 

## 1. 기술적 도전 및 해결 과정 (상상력 발휘)

### [Phase 1] 표준 API 접근 시도 (실패)
- **방법**: Microsoft UI Automation (UIA) 프레임워크를 활용하여 대화창 텍스트 속성에 직접 접근 시도.
- **결과**: 카카오톡이 델파이 기반의 커스텀 렌더링을 사용하여 텍스트 데이터를 외부로 노출하지 않음을 확인 (`IsTextPatternAvailable: False`).
- **상세 기록**: `research/attempt1_uia_scan.py` 참조.

### [Phase 2] 레거시 및 정밀 컨트롤 타격 (실패)
- **방법**: MSAA(LegacyIAccessible) 및 RichEdit 컨트롤 직접 타격 시도.
- **결과**: 윈도우 핸들은 획득 가능하나, 내부 데이터 값(Value)은 여전히 차단되어 있음을 확인.
- **상세 기록**: `research/attempt2_legacy_msaa.py`, `research/attempt3_richedit_hit.py` 참조.

### [Phase 3] 비간섭 클립보드 매크로 설계 (성공)
- **해결책**: 가장 정확한 텍스트 무결성을 보장하는 '복사(Ctrl+C)' 기능을 활용하되, 매크로의 치명적 단점인 **'사용자 방해(포커스 뺏기)'** 문제를 해결.
- **핵심 기술**:
    1. **Idle Time Detection**: 사용자가 키보드/마우스를 3초 이상 사용하지 않을 때만 작동.
    2. **Virtual Click**: 마우스 커서를 움직이지 않고 내부 신호(`PostMessage`)로만 포커스 획득.
    3. **Clipboard Restore**: 봇이 사용한 클립보드 데이터를 0.1초 만에 사용자의 원래 데이터로 복구.
    4. **Ghost Mode**: 카톡 창을 화면 밖(`-5000, -5000`)으로 유기하여 시각적 방해 제거.

## 2. 향후 계획 (Next Step)
- **데이터 무결성 강화**: 수집된 텍스트의 Hash값을 비교하여 중복 저장 방지.
- **Back-end 연동**: Spring Boot 서버와 REST API 통신을 통해 수집 데이터를 DB(MySQL/SQLite)에 영구 저장.
- **비정상 종료 복구**: 프로그램 재시작 시 DB의 마지막 100줄과 카톡 내용을 동기화하는 로직 추가.

## 3. 실행 방법
1. `pip install pywin32 pyperclip psutil`
2. 카카오톡 채팅방을 별도 창으로 실행 (예: "지혁")
3. `python kakao_receiver_main.py` 실행
