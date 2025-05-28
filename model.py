from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

# 모든 모델의 기본 클래스이다.
Base = declarative_base()

class PhotoSession(Base):
    __tablename__ = 'photo_sessions'
    id = Column(String(50), nullable=False, primary_key=True)
    frame = Column(String(50), nullable=False)
    qrfile = Column(String(50), default=None)
    photofile = Column(String(50), default=None)