from fastapi import FastAPI, Request
import uvicorn
import json
from urllib.parse import parse_qs

app = FastAPI()

@app.post("/receive")
async def receive_data(request: Request):
    try:
        # 일단 원본 데이터를 바이트로 읽음
        body = await request.body()
        if not body:
            print("⚠️ Received empty body")
            return {"status": "empty"}

        decoded_body = body.decode('utf-8')
        
        # 1. JSON 형식인지 먼저 시도
        try:
            data = json.loads(decoded_body)
        except json.JSONDecodeError:
            # 2. 실패하면 URL-encoded (Form) 형식으로 파싱 시도
            # 예: from=199999&content=hello...
            parsed = parse_qs(decoded_body)
            # 리스트 형태의 값을 단일 값으로 변환
            data = {k: v[0] for k, v in parsed.items()}

        # 터미널에 실시간 출력
        print("\n" + "="*50)
        print("🔔 [NEW DATA RECEIVED]")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("="*50 + "\n")
        
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Critical Error: {e}")
        print(f"Raw Body: {decoded_body if 'decoded_body' in locals() else 'No Body'}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # 모든 IP(0.0.0.0)에서 8080 포트로 대기
    uvicorn.run(app, host="0.0.0.0", port=8080)
