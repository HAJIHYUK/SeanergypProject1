from kakao_receive_service import KakaoReceiveService
from kakao_send_service import KakaoSendService
import threading
import time
import sys

class KakaoBotController:
    def __init__(self, room_name):
        self.receive_service = KakaoReceiveService(room_name)
        self.send_service = KakaoSendService(room_name)
        self.room_name = room_name
        self.is_running = True

    def run_receiver_loop(self):
        print(f"[{self.room_name}] DB 동기화 및 수집 시작...")
        while self.is_running:
            try:
                if self.receive_service.is_idle(threshold=3.0):
                    # 데이터 수집 및 DB 저장 통합 실행
                    saved_msgs = self.receive_service.collect_and_save()
                    for m in saved_msgs:
                        sys.stdout.write(f"\n[NEW DB SAVE] {m}\n나: ")
                        sys.stdout.flush()
            except:
                pass 
            time.sleep(1)

    def run_sender_interface(self):
        print("\n" + "="*40)
        print(f" 통합 카톡 봇 (ORM/DB 저장 모드)")
        print(f" 대상: {self.room_name} | DB: kakao_data.db")
        print("="*40 + "\n")

        while self.is_running:
            msg = input("나: ")
            if msg.lower() == 'exit':
                self.is_running = False
                break
            
            if msg.strip():
                if self.send_service.send_message(msg):
                    pass # 성공 시 조용히 넘어감
                else:
                    print(f"!! 전송 실패")

if __name__ == "__main__":
    controller = KakaoBotController("지혁")
    receiver_thread = threading.Thread(target=controller.run_receiver_loop, daemon=True)
    receiver_thread.start()
    controller.run_sender_interface()
