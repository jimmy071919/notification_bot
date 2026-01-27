import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


class Config:
    """應用配置類"""
    
    # Flask 設定
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-please-change')
    
    # LINE Bot 設定
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    
    # 資料庫設定
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reminders.db')
    
    # 時區設定
    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Taipei')
    
    @staticmethod
    def validate():
        """驗證必要的配置是否存在"""
        if not Config.LINE_CHANNEL_ACCESS_TOKEN:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 未設定")
        if not Config.LINE_CHANNEL_SECRET:
            raise ValueError("LINE_CHANNEL_SECRET 未設定")
