from sqlalchemy.orm import Session
from models import KakaoMessage
from database_config import engine, Base

Base.metadata.create_all(bind=engine)

class KakaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, message_entity: KakaoMessage):
        """메시지 저장 (중복 o )"""
        try:
            self.db.add(message_entity)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            return False

    def get_last_n_messages(self, n=20):
        """DB의 마지막 메시지 n개를 가져와서 동기화 기준으로 삼음"""
        results = self.db.query(KakaoMessage.content)\
            .order_by(KakaoMessage.id.desc())\
            .limit(n).all()
        # db에서 최신순으로 가져오기에 다시 뒤집어서 카톡창 대화 순서에 맞춤 
        return [r[0] for r in reversed(results)]
