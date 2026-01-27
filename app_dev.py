"""
開發版本 - 跳過簽名驗證（僅用於本地測試）
"""
from flask import Flask, request
from config import Config
from models import Session, Event
from utils import parse_command, format_datetime
import logging
import json
import requests

# 初始化 Flask 應用
app = Flask(__name__)
app.config.from_object(Config)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LINE API 端點
LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Config.LINE_CHANNEL_ACCESS_TOKEN}"
}


@app.route("/", methods=['GET'])
def home():
    """健康檢查端點"""
    return "LINE 提醒機器人運行中 🤖", 200


@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook 回調端點（開發版本 - 跳過簽名驗證）"""
    try:
        # 取得請求內容
        body = request.get_json()
        logger.info(f"收到 Webhook: {json.dumps(body, ensure_ascii=False)}")
        
        # 處理事件
        if 'events' in body:
            for event_data in body['events']:
                handle_event(event_data)
        
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"處理 Webhook 時發生錯誤: {e}", exc_info=True)
        return 'Error', 500


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
        
        # 解析指令 - 添加額外的錯誤處理
        try:
            parsed = parse_command(user_message)
        except Exception as parse_error:
            logger.error(f"解析指令時發生錯誤: {parse_error}", exc_info=True)
            send_reply(reply_token, "❌ 解析指令時發生錯誤，請稍後再試")
            return
        
        if parsed is None:
            # 指令格式錯誤
            reply_message = (
                "❌ 指令格式錯誤或時間已過\n\n"
                "正確格式：\n"
                "/MM-DD HH:mm 事情描述\n\n"
                "範例：\n"
                "/01-28 14:30 專案週會"
            )
            send_reply(reply_token, reply_message)
            return
        
        # 儲存到資料庫 - 添加額外的錯誤處理
        session = Session()
        try:
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
            reply_message = f"✅ 已設定提醒！\n\n📅 時間：{time_str}\n📝 事項：{parsed['description']}\n\n將在以下時間發送提醒：\n• 前 60 分鐘\n• 前 30 分鐘\n• 整點時刻"
            
            send_reply(reply_token, reply_message)
            logger.info(f"✅ 成功建立提醒: ID={new_event.id}, 時間={time_str}")
            
        except Exception as db_error:
            logger.error(f"儲存事件失敗: {db_error}", exc_info=True)
            session.rollback()
            send_reply(reply_token, "❌ 系統錯誤，請稍後再試")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"處理事件失敗: {e}", exc_info=True)
        if reply_token:
            try:
                send_reply(reply_token, "❌ 系統錯誤，請稍後再試")
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
            logger.info("✅ 回覆訊息發送成功")
        else:
            logger.error(f"❌ 回覆訊息發送失敗: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"發送回覆失敗: {e}", exc_info=True)


if __name__ == "__main__":
    from models import init_database
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
