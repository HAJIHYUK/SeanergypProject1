import subprocess
import re

class ADBHandler:
    def __init__(self):
        pass

    def get_full_notification_text(self, package_name="com.kakao.talk"):
        """상단바를 내리지 않고 시스템 메모리에서 알림 전체 텍스트를 추출"""
        print(f"🕵️‍♂️ [{package_name}] 알림 데이터 정밀 스캔 중...")
        
        # dumpsys notification 명령어로 알림 데이터 확보
        cmd = ["adb", "shell", "dumpsys", "notification"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if not result.stdout:
            return None

        # 해당 패키지(카톡)의 알림 섹션 찾기
        # 실무 팁: 'tickerText'나 'extras' 항목에 전체 본문이 들어있음
        output = result.stdout
        
        # 카톡 알림 섹션만 추출 (간략화된 파싱)
        if package_name in output:
            # 텍스트 데이터가 포함된 'extras' 영역을 정규식으로 타겟팅
            # 안드로이드 버전에 따라 구조가 다를 수 있으나 보통 'android.text' 필드에 본문이 있음
            texts = re.findall(r'android\.text=(.*?)\n', output)
            titles = re.findall(r'android\.title=(.*?)\n', output)
            
            if texts:
                # 가장 최근 알림(보통 리스트의 마지막) 반환
                full_content = texts[-1]
                sender = titles[-1] if titles else "Unknown"
                return {"sender": sender, "content": full_content}
        
        return None

if __name__ == "__main__":
    # 테스트: 지금 알림창에 카톡이 떠있다면 실행해봐라
    handler = ADBHandler()
    data = handler.get_full_notification_text()
    if data:
        print("\n" + "="*50)
        print(f"🎯 찾았다! 원본 데이터")
        print(f"👤 보낸사람: {data['sender']}")
        print(f"💬 전체내용: {data['content']}")
        print("="*50)
    else:
        print("❌ 카톡 알림을 찾지 못했습니다.")
