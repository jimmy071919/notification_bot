"""
測試腳本 - 用於測試指令解析和時間處理邏輯
"""
from datetime import datetime
import pytz
from utils import parse_command, format_datetime, get_remind_message


def test_parse_command():
    """測試指令解析功能"""
    print("=" * 60)
    print("測試指令解析功能")
    print("=" * 60)
    
    test_cases = [
        "/01-28 14:30 專案週會",
        "/12-31 23:59 跨年倒數",
        "/02-14 19:00 情人節晚餐",
        "/invalid format",
        "/13-32 25:99 錯誤的日期時間",
        "不是指令格式"
    ]
    
    for test_input in test_cases:
        print(f"\n輸入: {test_input}")
        result = parse_command(test_input)
        if result:
            print(f"解析成功")
            print(f"   時間: {format_datetime(result['event_datetime'])}")
            print(f"   描述: {result['description']}")
        else:
            print(f"解析失敗")


def test_year_logic():
    """測試年份處理邏輯"""
    print("\n" + "=" * 60)
    print("測試年份處理邏輯")
    print("=" * 60)
    
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    current_month = now.month
    
    print(f"\n當前時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"當前月份: {current_month}")
    
    # 測試當前月份之後的月份（應該是今年）
    future_month = (current_month % 12) + 1
    if future_month > current_month:
        test_cmd = f"/{future_month:02d}-15 12:00 測試未來月份"
        result = parse_command(test_cmd)
        if result:
            print(f"\n未來月份測試: {test_cmd}")
            print(f"結果年份: {result['event_datetime'].year} (預期: {now.year})")
    
    # 測試當前月份之前的月份（應該是明年）
    past_month = current_month - 1 if current_month > 1 else 12
    if past_month < current_month:
        test_cmd = f"/{past_month:02d}-15 12:00 測試過去月份"
        result = parse_command(test_cmd)
        if result:
            print(f"\n過去月份測試: {test_cmd}")
            print(f"結果年份: {result['event_datetime'].year} (預期: {now.year + 1})")


def test_remind_messages():
    """測試提醒訊息格式"""
    print("\n" + "=" * 60)
    print("測試提醒訊息格式")
    print("=" * 60)
    
    tz = pytz.timezone('Asia/Taipei')
    test_time = tz.localize(datetime(2026, 1, 28, 14, 30))
    test_desc = "專案週會"
    
    for remind_type in [60, 30, 0]:
        print(f"\n{remind_type} 分鐘提醒:")
        print("-" * 40)
        message = get_remind_message(test_desc, test_time, remind_type)
        print(message)


def test_time_validation():
    """測試時間驗證（已過期的時間應該被拒絕）"""
    print("\n" + "=" * 60)
    print("測試時間驗證")
    print("=" * 60)
    
    tz = pytz.timezone('Asia/Taipei')
    now = datetime.now(tz)
    
    # 測試過去的時間
    past_cmd = f"/{now.month:02d}-{now.day:02d} {(now.hour-1):02d}:{now.minute:02d} 過去的時間"
    print(f"\n測試過去時間: {past_cmd}")
    result = parse_command(past_cmd)
    if result:
        print("❌ 錯誤：過去的時間應該被拒絕")
    else:
        print("✅ 正確：過去的時間被正確拒絕")
    
    # 測試未來的時間
    future_hour = (now.hour + 2) % 24
    future_cmd = f"/{now.month:02d}-{now.day:02d} {future_hour:02d}:{now.minute:02d} 未來的時間"
    print(f"\n測試未來時間: {future_cmd}")
    result = parse_command(future_cmd)
    if result:
        print("✅ 正確：未來的時間被接受")
    else:
        print("❌ 錯誤：未來的時間應該被接受（或者日期設定有問題）")


if __name__ == "__main__":
    print("\n")
    print("🧪 LINE 提醒機器人測試腳本")
    print("=" * 60)
    
    test_parse_command()
    test_year_logic()
    test_remind_messages()
    test_time_validation()
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)
