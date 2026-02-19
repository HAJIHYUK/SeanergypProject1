from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite 파일 DB 경로
DB_URL = "sqlite:///./kakao_data.db"

# DB 엔진 및 세션 설정
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 모델용 베이스 클래스
Base = declarative_base()

# DB 세션 획득용 유틸리티
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
