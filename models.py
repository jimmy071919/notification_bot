from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# 建立資料庫引擎
engine = create_engine(Config.DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Event(Base):
    """事件資料表模型"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(100), nullable=False, index=True)
    event_datetime = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=False)
    remind_level = Column(Integer, default=0, nullable=False)
    # remind_level 說明:
    # 0: 未提醒
    # 1: 已發送 24 小時提醒
    # 2: 已發送 60 分鐘提醒
    # 3: 已發送 30 分鐘提醒
    # 4: 已發送整點提醒（完成）
    
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Event(id={self.id}, group_id={self.group_id}, event_datetime={self.event_datetime}, description={self.description}, remind_level={self.remind_level})>"
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'group_id': self.group_id,
            'event_datetime': self.event_datetime.isoformat(),
            'description': self.description,
            'remind_level': self.remind_level,
            'created_at': self.created_at.isoformat()
        }


def init_database():
    """初始化資料庫"""
    Base.metadata.create_all(engine)
    print("資料庫初始化完成！")


if __name__ == "__main__":
    init_database()
