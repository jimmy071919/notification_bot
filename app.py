from flask import Flask, request, abort
from config import Config
from models import Session, Event
from utils import parse_command, parse_remove_command, format_datetime
import logging
import json
import requests
import hashlib
import hmac
import base64

# 初始化 Flask 應用
app = Flask(__name__)
app.config.from_object(Config)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 驗證配置
try:
    Config.validate()
except ValueError as e:
    logger.error(f"配置錯誤: {e}")
    logger.error("請確保 .env 文件中設定了正確的 LINE Bot 憑證")

# LINE API 設定（使用 requests 避免 OpenSSL 問題）
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}"
}


@app.route("/", methods=['GET'])
def verify_signature(body, signature):
    """驗證 LINE 簽名"""
    hash_value = hmac.new(
        Config.LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    return signature == expected_signature


@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook 回調端點"""
    # 取得 X-Line-Signature header
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        logger.warning("缺少簽名")
        abort(400)
    
    # 取得請求內容
    body = request.get_data(as_text=True)
    logger.info(f"收到 Webhook: {body}")
    
    # 驗證簽名
    if not verify_signature(body, signature):
        logger.error("無效的簽名")
        abort(400)
    
    # 處理請求
    try:
        body_json = json.loads(body)
        if 'events' in body_json:
            for event_data in body_json['events']:
                handle_event(event_data)
        return 'OK', 200
    except Exception as e:
        logger.error(f"處理 Webhook 時發生錯誤: {e}", exc_info=True)
        abort(500)


def handle_event(event_data):
    """處理單一事件"""
    reply_token = None
    try:
        # 只處理文字訊息
        if event_data.get('type') != 'message':
            return
        
        message = event_data.get('message', {})
        if message.get('type') != 'text':
            return
        
        user_message = message.get('text', '')
        reply_token = event_data.get('replyToken')
        
        # 取得來源 ID
        source = event_data.get('source', {})
        group_id = source.get('groupId') or source.get('roomId') or source.get('userId')
        
        if not group_id:
            logger.warning("無法取得來源 ID")
            return
        
        logger.info(f"處理訊息: {user_message} (來自: {group_id})")
        
        # 只處理以 / 開頭的指令
        if not user_message.startswith('/'):
            return
        
        # 處理 /list 指令
        if user_message.strip().lower() == '/list':
            handle_list_command(reply_token, group_id)
            return
        
        # 處理 /rm 刪除指令
        if user_message.strip().lower().startswith('/rm'):
            handle_remove_command(reply_token, group_id, user_message)
            return
        
        # 解析指令
        parsed = parse_command(user_message)
        
        if parsed is None:
            # 指令格式錯誤
            reply_message = (
                "指令格式錯誤或時間已過\n\n"
                "正確格式：\n"
                "/MM-DD HH:mm 事情描述\n\n"
                "範例：\n"
                "/01-28 14:30 專案週會"
            )
            send_reply(reply_token, reply_message)
            return
        
        # 儲存到資料庫
        session = Session()
        try:
            # 檢查是否已存在相同的事件
            existing_event = session.query(Event).filter(
                Event.group_id == group_id,
                Event.event_datetime == parsed['event_datetime'],
                Event.description == parsed['description']
            ).first()
            
            if existing_event:
                # 已存在相同的事件
                time_str = format_datetime(parsed['event_datetime'])
                reply_message = f"⚠️ 此提醒已經存在！\n\n📅 時間：{time_str}\n📝 事項：{parsed['description']}"
                send_reply(reply_token, reply_message)
                logger.info(f"⚠️ 提醒已存在，未重複建立: 時間={time_str}")
                return
            
            new_event = Event(
                group_id=group_id,
                event_datetime=parsed['event_datetime'],
                description=parsed['description'],
                remind_level=0
            )
            session.add(new_event)
            session.commit()
            
            # 回覆成功訊息
            time_str = format_datetime(parsed['event_datetime'])
            reply_message = f"✅ 已設定提醒！\n\n📅 時間：{time_str}\n📝 事項：{parsed['description']}\n\n將在以下時間發送提醒：\n• 前 1 天\n• 前 60 分鐘\n• 前 30 分鐘\n• 整點時刻"
            
            send_reply(reply_token, reply_message)
            logger.info(f" 成功建立提醒: ID={new_event.id}, 時間={time_str}")
            
        except Exception as e:
            logger.error(f"儲存事件失敗: {e}", exc_info=True)
            session.rollback()
            send_reply(reply_token, "系統錯誤，請稍後再試")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"處理事件失敗: {e}", exc_info=True)
        if reply_token:
            try:
                send_reply(reply_token, "系統錯誤，請稍後再試")
            except:
                pass


def send_reply(reply_token, message_text):
    """發送回覆訊息（使用 requests 避免 OpenSSL 問題）"""
    try:
        payload = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        
        response = requests.post(
            LINE_REPLY_URL,
            headers=LINE_HEADERS,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("回覆訊息發送成功")
        else:
            logger.error(f"回覆訊息發送失敗: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"發送回覆失敗: {e}", exc_info=True)


def handle_list_command(reply_token, group_id):
    """處理 /list 指令，列出當前群組的所有行程"""
    session = Session()
    try:
        # 查詢該群組所有未完成的事件（remind_level < 4）
        events = session.query(Event).filter(
            Event.group_id == group_id,
            Event.remind_level < 4
        ).order_by(Event.event_datetime).all()
        
        if not events:
            reply_message = "📋 目前沒有任何行程"
            send_reply(reply_token, reply_message)
            return
        
        # 組合清單訊息
        reply_message = f"📋 目前有 {len(events)} 個行程：\n\n"
        
        for idx, event in enumerate(events, 1):
            time_str = format_datetime(event.event_datetime)
            # 狀態標記：0=未提醒, 1=已提醒1天, 2=已提醒60分, 3=已提醒30分
            if event.remind_level == 0:
                status_emoji = "⏳"
            elif event.remind_level == 1:
                status_emoji = "📅"
            elif event.remind_level == 2:
                status_emoji = "🔔"
            else:
                status_emoji = "⏰"
            reply_message += f"{status_emoji} {idx}. {time_str}\n   {event.description}\n\n"
        
        # LINE 訊息有長度限制，若超過 2000 字元則截斷
        if len(reply_message) > 1900:
            reply_message = reply_message[:1900] + "\n\n... (清單過長，已截斷)"
        
        send_reply(reply_token, reply_message)
        logger.info(f"✅ 已回覆行程清單: {len(events)} 個事件")
        
    except Exception as e:
        logger.error(f"處理 /list 指令失敗: {e}", exc_info=True)
        send_reply(reply_token, "❌ 查詢行程失敗，請稍後再試")
    finally:
        session.close()


def handle_remove_command(reply_token, group_id, user_message):
    """處理 /rm 指令，刪除指定的行程"""
    from utils import parse_remove_command
    
    # 解析刪除指令
    parsed = parse_remove_command(user_message)
    
    if parsed is None:
        reply_message = (
            "❌ 刪除指令格式錯誤\n\n"
            "正確格式：\n"
            "/rm MM-DD HH:mm 事情描述\n\n"
            "範例：\n"
            "/rm 01-29 15:00 重要會議"
        )
        send_reply(reply_token, reply_message)
        return
    
    session = Session()
    try:
        # 查詢符合條件的事件（相同群組、相同時間、相同描述）
        target_datetime = parsed['event_datetime']
        target_description = parsed['description']
        
        events = session.query(Event).filter(
            Event.group_id == group_id,
            Event.event_datetime == target_datetime,
            Event.description == target_description
        ).all()
        
        if not events:
            reply_message = f"❌ 找不到符合的行程\n\n📅 時間：{format_datetime(target_datetime)}\n📝 事項：{target_description}"
            send_reply(reply_token, reply_message)
            return
        
        # 刪除所有符合的事件
        deleted_count = len(events)
        for event in events:
            session.delete(event)
        
        session.commit()
        
        # 回覆成功訊息
        time_str = format_datetime(target_datetime)
        if deleted_count == 1:
            reply_message = f" 已刪除提醒\n\n 時間：{time_str}\n 事項：{target_description}"
        else:
            reply_message = f" 已刪除 {deleted_count} 個相同提醒\n\n 時間：{time_str}\n 事項：{target_description}"
        
        send_reply(reply_token, reply_message)
        logger.info(f" 成功刪除 {deleted_count} 個提醒: 時間={time_str}, 描述={target_description}")
        
    except Exception as e:
        logger.error(f"處理 /rm 指令失敗: {e}", exc_info=True)
        session.rollback()
        send_reply(reply_token, "刪除行程失敗")
    finally:
        session.close()


if __name__ == "__main__":
    # 本地開發時使用
    from models import init_database
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
