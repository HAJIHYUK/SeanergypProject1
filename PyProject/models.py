from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database_config import Base

# 카톡 메시지 저장 테이블 모델
class KakaoMessage(Base):
    __tablename__ = "kakao_messages"

    # 고유 ID (자동 증가)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 메시지 지문 (검색/인덱싱용)
    # [참고] 현재 도배 메시지 저장을 위해 UNIQUE 제약은 해제된 상태임
    msg_hash = Column(String(64), index=True, nullable=False)
    
    sender = Column(String(100))    # 발신자 이름
    content = Column(Text)          # 메시지 본문
    room_name = Column(String(100)) # 채팅방 이름
    sent_at = Column(String(100))   # 카톡상의 전송 시간 (오전/오후 HH:mm)
    created_at = Column(DateTime, default=datetime.now) # 실제 DB 저장 시점

    def __repr__(self):
        return f"<KakaoMessage(sender={self.sender}, content={self.content[:10]}...)>"
