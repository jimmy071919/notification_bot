import re
from datetime import datetime
import pytz
from config import Config


def parse_command(text):
    """
    解析指令格式：/MM-DD HH:mm 事情描述
    
    Args:
        text: 用戶輸入的文字
        
    Returns:
        dict: 包含 event_datetime 和 description，若解析失敗則返回 None
    """
    # 正則表達式匹配
    pattern = r'^/(\d{2})-(\d{2})\s+(\d{2}):(\d{2})\s+(.+)$'
    match = re.match(pattern, text.strip())
    
    if not match:
        return None
    
    month, day, hour, minute, description = match.groups()
    
    try:
        # 獲取時區
        tz = pytz.timezone(Config.TIMEZONE)
        now = datetime.now(tz)
        current_year = now.year
        current_month = now.month
        
        # 年份處理邏輯
        input_month = int(month)
        if input_month < current_month:
            # 若輸入月份小於當前月份，則設為明年
            year = current_year + 1
        else:
            year = current_year
        
        # 組合完整日期時間
        event_datetime = tz.localize(datetime(
            year=year,
            month=int(month),
            day=int(day),
            hour=int(hour),
            minute=int(minute)
        ))
        
        # 驗證時間是否已過
        if event_datetime <= now:
            return None
        
        return {
            'event_datetime': event_datetime,
            'description': description.strip()
        }
        
    except (ValueError, Exception) as e:
        print(f"解析錯誤: {e}")
        return None


def format_datetime(dt):
    """格式化日期時間為易讀格式"""
    return dt.strftime('%Y-%m-%d %H:%M')


def get_remind_message(description, event_datetime, remind_type):
    """
    生成提醒訊息
    
    Args:
        description: 事件描述
        event_datetime: 事件時間
        remind_type: 提醒類型 (60, 30, 0)
        
    Returns:
        str: 格式化的提醒訊息
    """
    time_str = format_datetime(event_datetime)
    
    if remind_type == 60:
        return f"提醒：還有 1 小時\n\n 時間：{time_str}\n 事項：{description}"
    elif remind_type == 30:
        return f"提醒：還有 30 分鐘\n\n 時間：{time_str}\n 事項：{description}"
    elif remind_type == 0:
        return f"時間到！\n\n 時間：{time_str}\n 事項：{description}"
    
    return f" {time_str}\n {description}"
