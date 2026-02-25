import subprocess
import os

def deep_pull_all():
    remote_dir = "/data/data/com.kakao.talk/databases/"
    local_dir = "./all_dbs"
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    print("🕵️‍♂️ [1단계] 모든 DB 관련 파일(WAL/SHM 포함) 추출 시작...")
    
    # 해당 폴더의 모든 파일을 가져온다
    list_cmd = ["adb", "shell", "su", "-c", f"ls {remote_dir}"]
    result = subprocess.run(list_cmd, capture_output=True, text=True)
    
    if not result.stdout:
        print("❌ 파일을 찾을 수 없습니다.")
        return

    files = result.stdout.split()
    for filename in files:
        filename = filename.strip()
        if not filename: continue
        
        remote_path = remote_dir + filename
        local_path = os.path.join(local_dir, filename)
        
        # 1. 임시 복사
        subprocess.run(["adb", "shell", "su", "-c", f"cp {remote_path} /sdcard/{filename}"], capture_output=True)
        # 2. 권한 변경
        subprocess.run(["adb", "shell", "su", "-c", f"chmod 777 /sdcard/{filename}"], capture_output=True)
        # 3. PC로 가져오기
        subprocess.run(["adb", "pull", f"/sdcard/{filename}", local_path], capture_output=True)
        print(f" ✅ Pulled: {filename}")

    print(f"\n✨ 모든 파일이 '{local_dir}'에 저장되었습니다. 이제 최신 데이터가 반영됩니다.")

if __name__ == "__main__":
    deep_pull_all()
