"""
本地測試腳本 - 模擬 LINE Webhook 請求
用於測試機器人功能而不需要實際的 LINE 環境
"""
import requests
import json
from datetime import datetime, timedelta
import pytz

# 設定測試參數
BASE_URL = "http://localhost:5000"
TEST_GROUP_ID = "test_group_123"

def test_webhook():
    """測試 webhook 端點"""
    print("=" * 60)
    print("測試 Webhook 端點")
    print("=" * 60)
    
    # 測試根路徑
    print("\n1. 測試根路徑 (GET /)...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   狀態碼: {response.status_code}")
    print(f"   回應: {response.text}")
    
    # 測試 webhook 路徑（無簽名，應該失敗）
    print("\n2. 測試 Webhook 路徑 (POST /webhook - 無簽名)...")
    response = requests.post(f"{BASE_URL}/webhook", json={})
    print(f"   狀態碼: {response.status_code} (預期: 400 Bad Request)")

def create_test_event():
    """創建測試提醒事件（直接操作資料庫）"""
    print("\n" + "=" * 60)
    print("創建測試提醒事件")
    print("=" * 60)
    
    from models import Session, Event
    from config import Config
    import pytz
    
    tz = pytz.timezone(Config.TIMEZONE)
    now = datetime.now(tz)
    
    # 創建三個測試事件
    test_events = [
        {
            "time_offset": 61,  # 61 分鐘後（測試 60 分鐘提醒）
            "description": "測試提醒 - 60分鐘"
        },
        {
            "time_offset": 31,  # 31 分鐘後（測試 30 分鐘提醒）
            "description": "測試提醒 - 30分鐘"
        },
        {
            "time_offset": 2,   # 2 分鐘後（測試整點提醒）
            "description": "測試提醒 - 整點"
        }
    ]
    
    session = Session()
    try:
        print("\n創建測試事件：")
        for i, event_data in enumerate(test_events, 1):
            event_time = now + timedelta(minutes=event_data["time_offset"])
            
            new_event = Event(
                group_id=TEST_GROUP_ID,
                event_datetime=event_time,
                description=event_data["description"],
                remind_level=0
            )
            session.add(new_event)
            
            print(f"{i}. {event_data['description']}")
            print(f"   時間: {event_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   ({event_data['time_offset']} 分鐘後)")
        
        session.commit()
        print("\n✅ 測試事件創建成功！")
        print("\n排程器會在以下時間發送提醒：")
        print(f"   - 約 1 分鐘後（60分鐘提醒）")
        print(f"   - 約 1 分鐘後（30分鐘提醒）")
        print(f"   - 約 2 分鐘後（整點提醒）")
        print("\n請觀察終端機日誌輸出...")
        
    except Exception as e:
        print(f"\n❌ 創建失敗: {e}")
        session.rollback()
    finally:
        session.close()

def list_events():
    """列出所有事件"""
    print("\n" + "=" * 60)
    print("資料庫中的所有事件")
    print("=" * 60)
    
    from models import Session, Event
    
    session = Session()
    try:
        events = session.query(Event).all()
        
        if not events:
            print("\n目前沒有任何事件")
            return
        
        print(f"\n共有 {len(events)} 個事件：\n")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.description}")
            print(f"   ID: {event.id}")
            print(f"   群組: {event.group_id}")
            print(f"   時間: {event.event_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   狀態: {['未提醒', '已發60分', '已發30分', '已完成'][event.remind_level]}")
            print()
            
    except Exception as e:
        print(f"\n❌ 查詢失敗: {e}")
    finally:
        session.close()

def clear_events():
    """清空所有事件"""
    print("\n" + "=" * 60)
    print("清空所有事件")
    print("=" * 60)
    
    from models import Session, Event
    
    session = Session()
    try:
        count = session.query(Event).delete()
        session.commit()
        print(f"\n✅ 已刪除 {count} 個事件")
    except Exception as e:
        print(f"\n❌ 刪除失敗: {e}")
        session.rollback()
    finally:
        session.close()

def test_command_parser():
    """測試指令解析"""
    print("\n" + "=" * 60)
    print("測試指令解析功能")
    print("=" * 60)
    
    from utils import parse_command
    from datetime import datetime
    import pytz
    
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    
    # 生成測試指令（2小時後）
    future_time = now + timedelta(hours=2)
    test_cmd = f"/{future_time.strftime('%m-%d %H:%M')} 測試會議"
    
    print(f"\n測試指令: {test_cmd}")
    result = parse_command(test_cmd)
    
    if result:
        print("✅ 解析成功")
        print(f"   時間: {result['event_datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   描述: {result['description']}")
    else:
        print("❌ 解析失敗")

def main():
    """主選單"""
    while True:
        print("\n" + "=" * 60)
        print("LINE 提醒機器人 - 測試工具")
        print("=" * 60)
        print("\n請選擇測試項目：")
        print("1. 測試 Webhook 端點")
        print("2. 測試指令解析")
        print("3. 創建測試提醒事件（自動觸發）")
        print("4. 列出所有事件")
        print("5. 清空所有事件")
        print("0. 退出")
        
        choice = input("\n請選擇 [0-5]: ").strip()
        
        if choice == "0":
            print("\n再見！")
            break
        elif choice == "1":
            test_webhook()
        elif choice == "2":
            test_command_parser()
        elif choice == "3":
            create_test_event()
        elif choice == "4":
            list_events()
        elif choice == "5":
            confirm = input("確定要清空所有事件嗎？(y/N): ").strip().lower()
            if confirm == 'y':
                clear_events()
        else:
            print("\n❌ 無效的選擇")
        
        input("\n按 Enter 繼續...")

if __name__ == "__main__":
    print("\n確保主程式 (main.py) 正在運行！\n")
    main()
