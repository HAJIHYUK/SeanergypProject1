import xml.etree.ElementTree as ET
import os
import subprocess

class KakaoUIParser:
    def __init__(self):
        self.local_xml = "room_view.xml"

    def dump_and_parse_room(self):
        """채팅방 내부의 대화 내용을 정밀하게 긁어옴 (content-desc 대응 버전)"""
        print("🕵️‍♂️ [Step 1] 채팅방 화면 덤프 중...")
        
        # 1. 화면 덤프 및 가져오기 (room_view.xml로 저장)
        subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/room_view.xml"], capture_output=True)
        subprocess.run(["adb", "pull", "/sdcard/room_view.xml", self.local_xml], capture_output=True)

        if not os.path.exists(self.local_xml):
            print("❌ XML 덤프 실패")
            return []

        print("🚀 [Step 2] 대화 내용 정밀 파싱 중...")
        try:
            tree = ET.parse(self.local_xml)
            root = tree.getroot()
            
            messages = []
            room_name = "알수없음"
            current_sender = "나" # 기본값 (보통 내 메시지는 닉네임 노드가 없음)

            # 모든 노드를 순차적으로 탐색
            for node in root.iter('node'):
                res_id = node.get('resource-id', '')
                text = node.get('text', '')
                content_desc = node.get('content-desc', '')

                # 1. 채팅방 이름 찾기
                if "id/toolbar_default_title_text" in res_id:
                    room_name = content_desc if content_desc else text
                    print(f"🏠 [확인된 채팅방]: {room_name}")

                # 2. 보낸 사람 이름 (상대방일 경우에만 나타남)
                if "id/nickname" in res_id and text:
                    current_sender = text
                
                # 3. 메시지 내용 (핵심: content-desc 확인)
                elif "id/message" in res_id:
                    msg_content = content_desc if content_desc else text
                    if msg_content:
                        messages.append({
                            "sender": current_sender,
                            "content": msg_content.strip(),
                            "room": room_name
                        })
                
                # 4. 사진/미디어 감지
                elif "id/image" in res_id and content_desc == "사진":
                    messages.append({
                        "sender": current_sender,
                        "content": "[📸 사진 첨부됨]",
                        "room": room_name
                    })

            return messages
        except Exception as e:
            print(f"❌ 파싱 에러: {e}")
            return []

if __name__ == "__main__":
    parser = KakaoUIParser()
    chat_logs = parser.dump_and_parse_room()
    
    print("\n" + "="*60)
    print(f"💬 채팅방 스캔 결과 ({len(chat_logs)}개 항목)")
    print("="*60)
    
    for log in chat_logs:
        print(f"👤 {log['sender']}: {log['content']}")
    
    print("="*60)
