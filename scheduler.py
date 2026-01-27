from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import logging
import requests
from config import Config
from models import Session, Event
from utils import get_remind_message

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINE API 設定
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}"
}

# 時區設定
tz = pytz.timezone(Config.TIMEZONE)


def check_and_send_reminders():
    """
    檢查資料庫並發送提醒
    每分鐘執行一次
    """
    session = Session()
    try:
        now = datetime.now(tz)
        logger.info(f"[排程] 開始檢查提醒 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 查詢所有未完成的事件（remind_level < 3）
        events = session.query(Event).filter(
            Event.remind_level < 3
        ).all()
        
        if not events:
            logger.info("[排程] 沒有待處理的提醒")
            return
        
        logger.info(f"[排程] 找到 {len(events)} 個待處理事件")
        
        for event in events:
            try:
                # 確保 event_datetime 有時區資訊
                if event.event_datetime.tzinfo is None:
                    event_datetime = tz.localize(event.event_datetime)
                else:
                    event_datetime = event.event_datetime.astimezone(tz)
                
                time_diff = (event_datetime - now).total_seconds() / 60  # 轉換為分鐘
                
                # 邏輯 A: 60 分鐘提醒
                if event.remind_level == 0 and 58 <= time_diff <= 62:
                    send_reminder(event, 60)
                    event.remind_level = 1
                    session.commit()
                    logger.info(f"[排程] 已發送 60 分鐘提醒: {event.description}")
                
                # 邏輯 B: 30 分鐘提醒
                elif event.remind_level == 1 and 28 <= time_diff <= 32:
                    send_reminder(event, 30)
                    event.remind_level = 2
                    session.commit()
                    logger.info(f"[排程] 已發送 30 分鐘提醒: {event.description}")
                
                # 邏輯 C: 整點提醒
                elif event.remind_level == 2 and -2 <= time_diff <= 2:
                    send_reminder(event, 0)
                    event.remind_level = 3
                    session.commit()
                    logger.info(f"[排程] 已發送整點提醒: {event.description}")
                
                # 例外處理：如果事件在 1 小時內才創建，跳過已過的提醒階段
                elif event.remind_level == 0 and time_diff < 58:
                    if 28 <= time_diff <= 62:
                        # 直接進入 30 分鐘提醒階段
                        event.remind_level = 1
                        session.commit()
                        logger.info(f"[排程] 跳過 60 分鐘提醒（時間不足）: {event.description}")
                    elif -2 <= time_diff < 28:
                        # 直接進入整點提醒階段
                        event.remind_level = 2
                        session.commit()
                        logger.info(f"[排程] 跳過 60+30 分鐘提醒（時間不足）: {event.description}")
                
                # 例外處理：如果 remind_level=1 但時間已不足 30 分鐘
                elif event.remind_level == 1 and time_diff < 28 and time_diff > -2:
                    event.remind_level = 2
                    session.commit()
                    logger.info(f"[排程] 跳過 30 分鐘提醒（時間不足）: {event.description}")
                
                # 清理已過期且已完成的事件（事件時間過後 10 分鐘）
                elif event.remind_level == 3 and time_diff < -10:
                    session.delete(event)
                    session.commit()
                    logger.info(f"[排程] 清理已完成事件: {event.description}")
                    
            except Exception as e:
                logger.error(f"[排程] 處理事件失敗: {event.id} - {e}")
                continue
        
    except Exception as e:
        logger.error(f"[排程] 檢查提醒時發生錯誤: {e}")
    finally:
        session.close()


def send_reminder(event, remind_type):
    """
    發送提醒訊息到 LINE 群組（使用 requests 避免 OpenSSL 問題）
    
    Args:
        event: Event 物件
        remind_type: 提醒類型 (60, 30, 0)
    """
    try:
        # 確保 event_datetime 有時區資訊
        if event.event_datetime.tzinfo is None:
            event_datetime = tz.localize(event.event_datetime)
        else:
            event_datetime = event.event_datetime
        
        message_text = get_remind_message(
            event.description,
            event_datetime,
            remind_type
        )
        
        # 使用 requests 發送推播訊息
        payload = {
            "to": event.group_id,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        
        response = requests.post(
            LINE_PUSH_URL,
            headers=LINE_HEADERS,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"成功發送提醒到群組 {event.group_id}")
        else:
            logger.error(f"發送提醒失敗: {response.status_code} - {response.text}")
            raise Exception(f"LINE API 錯誤: {response.status_code}")
        
    except Exception as e:
        logger.error(f"發送提醒失敗: {e}", exc_info=True)
        raise


def start_scheduler():
    """啟動排程器"""
    scheduler = BackgroundScheduler(timezone=tz)
    
    # 每 10 秒執行一次檢查
    scheduler.add_job(
        check_and_send_reminders,
        'interval',
        seconds=10,
        id='reminder_checker',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("排程器已啟動，每 10 秒檢查一次提醒")
    
    return scheduler


if __name__ == "__main__":
    # 測試排程器
    print("啟動排程器測試...")
    scheduler = start_scheduler()
    
    try:
        # 保持運行
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("排程器已關閉")
