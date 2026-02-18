from kakao_service import KakaoService
import time

# 프로그램 메인 진입점
def main():
    # 타겟팅할 채팅방 이름 (별도 창으로 분리되어 있어야 함)
    target_room = "지혁"
    kakao_service = KakaoService(target_room)
    
    print(f"[{target_room}] 메시지 수집 시작함.")
    print("사용자가 3초 동안 입력을 멈추면 작동합니다.")

    while True:
        try:
            # 1. 사용자가 키보드/마우스를 안 쓰는 유휴 상태인지 체크
            if kakao_service.is_user_ready(threshold=3.0):
                
                # 2. 카톡 대화창 활성화해서 데이터 복사해오기
                raw_data = kakao_service.collect_chat_data()
                
                # 3. 이전 데이터랑 비교해서 새 메시지만 리스트로 추출
                new_messages = kakao_service.extract_new_messages(raw_data)
                
                if new_messages:
                    print(f"\n[{time.strftime('%H:%M:%S')}] 새 메시지 {len(new_messages)}개 발견")
                    for msg in new_messages:
                        print(f" > {msg}")
                    
        except KeyboardInterrupt:
            print("\n사용자가 프로그램을 중단함.")
            break
        except Exception as e:
            print(f"런타임 에러 발생: {e}")
            
        # 루프 간격 (너무 짧으면 CPU 점유율 올라감)
        time.sleep(1)

if __name__ == "__main__":
    main()
