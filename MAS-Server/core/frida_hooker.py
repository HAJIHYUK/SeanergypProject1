import frida
import sys

# 카톡 메모리에 주입할 자바스크립트 훅 코드 (안드로이드 시스템 레벨 타격)
HOOK_JS = """
Java.perform(function () {
    console.log("[*] 카카오톡 메모리 훅 준비 완료...");

    // 안드로이드 알림 매니저 클래스 후킹
    var NotificationManager = Java.use("android.app.NotificationManager");

    // notify 메서드 가로채기 (알림이 발생하는 순간)
    NotificationManager.notify.overload('java.lang.String', 'int', 'android.app.Notification').implementation = function (tag, id, notification) {
        
        try {
            // 알림 객체 안에 숨겨진 'extras' 보따리 열기
            var extras = notification.extras.value;
            
            if (extras != null) {
                // 발신자 이름과 원본 전체 텍스트 추출 (글자 수 제한 없음)
                var title = extras.getString("android.title");
                var text = extras.getString("android.text");
                
                if (title != null && text != null) {
                    // 파이썬 서버로 데이터 전송
                    send({
                        "type": "kakaotalk_msg",
                        "sender": title,
                        "content": text
                    });
                }
            }
        } catch (e) {
            console.log("[-] 파싱 에러: " + e);
        }

        // 원래 하려던 알림 띄우기 동작은 정상적으로 실행되게 둠 (카톡이 눈치채지 못하게)
        this.notify(tag, id, notification);
    };
});
"""

def on_message(message, data):
    """자바스크립트 훅에서 쏴준 데이터를 파이썬이 받는 곳"""
    if message['type'] == 'send':
        payload = message['payload']
        if payload.get('type') == 'kakaotalk_msg':
            print("
" + "🔥" * 20)
            print(" [메모리 가로채기 성공! 1 안지워짐]")
            print(f" 👤 보낸사람: {payload['sender']}")
            print(f" 💬 전체내용: {payload['content']}")
            print("🔥" * 20 + "
")
            # TODO: 여기서 DB(PostgreSQL/SQLite)로 저장하는 로직 추가
    elif message['type'] == 'error':
        print(f"❌ 훅 에러: {message['stack']}")

def start_hooking():
    print("🚀 [MAS 스텔스 엔진] 에뮬레이터 연결 중...")
    try:
        # USB(ADB)로 연결된 기기(LDPlayer) 가져오기
        device = frida.get_usb_device()
        
        print("🎯 [MAS 스텔스 엔진] 카카오톡 프로세스 타겟팅...")
        # 카톡 프로세스(com.kakao.talk)에 접속
        session = device.attach("com.kakao.talk")
        
        print("💉 [MAS 스텔스 엔진] 메모리 빨대 꽂는 중...")
        # 자바스크립트 코드 주입
        script = session.create_script(HOOK_JS)
        script.on('message', on_message)
        script.load()
        
        print("✅ [MAS 스텔스 엔진] 가동 완료! (메시지를 보내보세요. Ctrl+C로 종료)")
        sys.stdin.read() # 프로그램이 안 꺼지고 대기하게 만듦
        
    except frida.ServerNotRunningError:
        print("❌ [에러] 에뮬레이터에 frida-server가 실행되어 있지 않습니다.")
        print("    -> 사수에게 'frida-server 세팅법'을 물어보세요!")
    except frida.ProcessNotFoundError:
        print("❌ [에러] 카카오톡이 실행되어 있지 않습니다. 카톡을 켜주세요.")
    except Exception as e:
        print(f"❌ [에러] {e}")

if __name__ == "__main__":
    start_hooking()
