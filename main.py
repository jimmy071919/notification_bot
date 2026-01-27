"""
LINE 提醒機器人主程式
整合 Flask Web Server 和 APScheduler 排程器
"""
from app import app
from scheduler import start_scheduler
from models import init_database
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化資料庫
logger.info("初始化資料庫...")
init_database()

# 啟動排程器
logger.info("啟動排程器...")
scheduler = start_scheduler()

if __name__ == "__main__":
    # 啟動 Flask 應用
    logger.info("啟動 Flask 應用...")
    app.run(host='0.0.0.0', port=5000, debug=False)
