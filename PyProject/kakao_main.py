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

    # 백그라운드 수신 루프 (별도 스레드에서 작동)
    def run_receiver_loop(self):
        print(f"[{self.room_name}] 실시간 메시지 수집 중...")
        while self.is_running:
            try:
                # 유저 유휴 상태일 때만 몰래 데이터 긁어옴
                if self.receive_service.is_idle(threshold=3.0):
                    # 데이터 수집 및 DB 저장 통합 실행
                    saved_msgs = self.receive_service.collect_and_save()
                    for m in saved_msgs:
                        # 수신된 메시지 출력 (한 줄 띄워서 가독성 확보)
                        sys.stdout.write(f"\n[NEW DB SAVE] {m}\n나: ")
                        sys.stdout.flush()
            except:
                pass 
            finally:
                time.sleep(1)

    # 유저 입력 대기 인터페이스 (메인 스레드)
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
                # 서비스 호출해서 전송
                if self.send_service.send_message(msg):
                    pass # 성공 시 조용히 넘어감
                else:
                    print(f"!! 전송 실패 (채팅방 확인 필요)")

if __name__ == "__main__":
    controller = KakaoBotController("지혁")

    # 수신 봇 스레드 실행
    receiver_thread = threading.Thread(target=controller.run_receiver_loop, daemon=True)
    receiver_thread.start()

    # 송신 대기 (메인 흐름)
    controller.run_sender_interface()
