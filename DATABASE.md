# 資料庫管理文件

## 概述

本專案使用 SQLAlchemy ORM 框架進行資料庫管理，預設使用 SQLite，支援切換至 PostgreSQL、MySQL 等其他資料庫。

## 資料庫架構

### ORM 框架：SQLAlchemy

- **引擎建立**：在 `models.py` 中建立資料庫引擎
  ```python
  engine = create_engine(Config.DATABASE_URL, echo=False)
  Session = sessionmaker(bind=engine)
  Base = declarative_base()
  ```

### 資料庫配置

在 `config.py` 中設定：

```python
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reminders.db')
```

- **預設**：SQLite 本地檔案 `reminders.db`
- **自訂**：透過環境變數 `DATABASE_URL` 設定其他資料庫
- **範例**：
  - PostgreSQL: `postgresql://user:password@localhost/dbname`
  - MySQL: `mysql://user:password@localhost/dbname`

## 資料表結構

### Event 表 (events)

儲存所有提醒事件的資料表。

| 欄位名稱 | 類型 | 說明 | 特性 |
|---------|------|------|------|
| `id` | Integer | 事件唯一識別碼 | Primary Key, AutoIncrement |
| `group_id` | String(100) | LINE 群組/聊天室/使用者 ID | Not Null, Indexed |
| `event_datetime` | DateTime | 事件發生時間 | Not Null, Indexed |
| `description` | Text | 事件描述內容 | Not Null |
| `remind_level` | Integer | 提醒進度等級 (0-4) | Not Null, Default=0 |
| `created_at` | DateTime | 記錄建立時間 | Default=now() |

### remind_level 狀態說明

提醒進度採用狀態機制，依序遞增：

- **0**：未提醒（初始狀態）
- **1**：已發送 24 小時前提醒
- **2**：已發送 60 分鐘前提醒
- **3**：已發送 30 分鐘前提醒
- **4**：已發送整點提醒（完成狀態）

## 資料庫初始化

### 方法一：使用 init_db.py 腳本

```bash
python init_db.py
```

此腳本會呼叫 `init_database()` 函數建立所有資料表。

### 方法二：直接呼叫 models.py

```bash
python models.py
```

`models.py` 內建初始化功能，可直接執行。

### 初始化函數

```python
def init_database():
    """初始化資料庫"""
    Base.metadata.create_all(engine)
    print("資料庫初始化完成！")
```

此函數會根據 `Base` 繼承的所有模型自動建立對應的資料表。

## 資料庫操作

### Session 管理

所有資料庫操作都透過 Session 進行：

```python
from models import Session, Event

session = Session()
try:
    # 執行資料庫操作
    # ...
    session.commit()
finally:
    session.close()
```

### 常見操作範例

#### 1. 新增事件

```python
from datetime import datetime
from models import Session, Event

session = Session()
try:
    new_event = Event(
        group_id='G123456789',
        event_datetime=datetime(2026, 2, 1, 15, 30),
        description='團隊會議',
        remind_level=0
    )
    session.add(new_event)
    session.commit()
    print(f"已新增事件 ID: {new_event.id}")
finally:
    session.close()
```

#### 2. 查詢事件

```python
# 查詢特定群組的所有事件
events = session.query(Event).filter(
    Event.group_id == 'G123456789'
).all()

# 查詢未完成的提醒（remind_level < 4）
pending_events = session.query(Event).filter(
    Event.remind_level < 4
).all()

# 查詢特定時間範圍的事件
from datetime import datetime, timedelta
start_time = datetime.now()
end_time = start_time + timedelta(days=7)

events_in_range = session.query(Event).filter(
    Event.event_datetime >= start_time,
    Event.event_datetime <= end_time
).all()
```

#### 3. 更新事件

```python
# 更新提醒等級
event = session.query(Event).filter(Event.id == 1).first()
if event:
    event.remind_level = 1
    session.commit()
```

#### 4. 刪除事件

```python
# 刪除單一事件
event = session.query(Event).filter(Event.id == 1).first()
if event:
    session.delete(event)
    session.commit()

# 刪除已完成的事件
session.query(Event).filter(Event.remind_level == 4).delete()
session.commit()
```

#### 5. 轉換為字典

```python
event = session.query(Event).first()
event_dict = event.to_dict()
# 輸出: {'id': 1, 'group_id': 'G123...', 'event_datetime': '2026-02-01T15:30:00', ...}
```

## 提醒機制

### 排程檢查邏輯

`scheduler.py` 中的 `check_and_send_reminders()` 函數每分鐘執行一次：

```python
def check_and_send_reminders():
    session = Session()
    try:
        now = datetime.now(tz)
        
        # 查詢所有未完成的事件
        events = session.query(Event).filter(
            Event.remind_level < 4
        ).all()
        
        for event in events:
            time_diff = (event_datetime - now).total_seconds() / 60
            
            # 根據 time_diff 和 remind_level 決定是否發送提醒
            # ...
    finally:
        session.close()
```

### 提醒時間點

| 提醒階段 | remind_level | 觸發條件 | 時間範圍 |
|---------|-------------|---------|---------|
| 24 小時前 | 0 → 1 | 距離事件 1440 分鐘 | 1430-1450 分鐘 |
| 60 分鐘前 | 1 → 2 | 距離事件 60 分鐘 | 58-62 分鐘 |
| 30 分鐘前 | 2 → 3 | 距離事件 30 分鐘 | 28-32 分鐘 |
| 整點時刻 | 3 → 4 | 距離事件 0 分鐘 | -2 到 +2 分鐘 |

### 跳過機制

如果事件新增時已接近提醒時間，系統會自動跳過已過時的提醒階段：

- 若距離事件不足 24 小時但超過 60 分鐘 → 跳至 `remind_level = 1`
- 若距離事件不足 60 分鐘但超過 30 分鐘 → 跳至 `remind_level = 2`
- 若距離事件不足 30 分鐘 → 跳至 `remind_level = 3`

## 索引優化

為提升查詢效能，在以下欄位建立索引：

- `group_id`：快速查詢特定群組的事件
- `event_datetime`：快速查詢特定時間範圍的事件

這些索引對於排程器的定期掃描特別重要，能有效減少查詢時間。

## 資料庫遷移

目前專案未使用遷移工具（如 Alembic）。若需要修改資料表結構：

### 開發環境（SQLite）

1. 備份現有資料庫：`cp reminders.db reminders.db.backup`
2. 刪除資料庫檔案：`rm reminders.db`
3. 修改 `models.py` 中的模型定義
4. 重新初始化：`python init_db.py`

### 生產環境

建議使用 Alembic 進行資料庫遷移：

```bash
# 安裝 Alembic
pip install alembic

# 初始化遷移環境
alembic init alembic

# 產生遷移腳本
alembic revision --autogenerate -m "描述變更內容"

# 執行遷移
alembic upgrade head
```

## 注意事項

1. **Session 管理**：務必在操作完成後關閉 Session，避免連線洩漏
2. **時區處理**：事件時間統一使用設定的時區（預設 `Asia/Taipei`）
3. **並發控制**：SQLite 對並發寫入支援有限，生產環境建議使用 PostgreSQL
4. **備份策略**：定期備份資料庫檔案或使用資料庫內建的備份功能
5. **錯誤處理**：所有資料庫操作應包含 try-except 區塊，避免程式崩潰

## 相關檔案

- `models.py`：資料模型定義
- `init_db.py`：資料庫初始化腳本
- `config.py`：資料庫連線設定
- `scheduler.py`：排程器與資料查詢邏輯
- `app.py`：Flask 應用與事件 CRUD 操作
