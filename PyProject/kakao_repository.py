from sqlalchemy.orm import Session
from models import KakaoMessage
from database_config import engine, Base

# 테이블 자동 생성
Base.metadata.create_all(bind=engine)

class KakaoRepository:
    def __init__(self, db: Session):
        self.db = db

    # 새로운 메시지 저장
    def save(self, message_entity: KakaoMessage):
        try:
            self.db.add(message_entity)
            self.db.commit()
            return True
        except:
            self.db.rollback()
            return False

    # 최근 저장된 메시지들을 지정한 개수(limit)만큼 가져옴
    def get_last_n_messages(self, limit: int):
        # 최신 ID 순으로 정렬해서 가져오기
        results = self.db.query(KakaoMessage.content)\
            .order_by(KakaoMessage.id.desc())\
            .limit(limit).all()
        # 카톡창 순서에 맞게 다시 뒤집어서 반환
        return [r[0] for r in reversed(results)]
