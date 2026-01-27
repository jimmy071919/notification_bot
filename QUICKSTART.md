# 🚀 快速開始指南

## 第一步：安裝依賴

```bash
pip install -r requirements.txt
```

## 第二步：設定環境變數

1. 複製環境變數範本：
```bash
copy .env.example .env
```

2. 編輯 `.env` 檔案，填入你的 LINE Bot 憑證：
```env
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
SECRET_KEY=隨機生成的密鑰
```

### 如何取得 LINE Bot 憑證？

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 登入並創建新的 Provider（如果還沒有）
3. 創建新的 **Messaging API** Channel
4. 在 Basic Settings 中取得 **Channel Secret**
5. 在 Messaging API 中發行 **Channel Access Token**

## 第三步：初始化資料庫

```bash
python init_db.py
```

應該看到：`✅ 資料庫初始化完成！`

## 第四步：測試功能

運行測試腳本確認邏輯正常：

```bash
python test.py
```

## 第五步：本地測試（使用 ngrok）

### A. 啟動應用

```bash
python main.py
```

應該看到：
```
初始化資料庫...
✅ 資料庫初始化完成！
啟動排程器...
✅ 排程器已啟動，每分鐘檢查一次提醒
啟動 Flask 應用...
 * Running on http://0.0.0.0:5000
```

### B. 使用 ngrok 建立隧道

開啟另一個終端機視窗：

```bash
ngrok http 5000
```

你會看到類似這樣的輸出：
```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5000
```

### C. 設定 LINE Webhook URL

1. 回到 LINE Developers Console
2. 進入你的 Channel 設定頁面
3. 找到 **Messaging API** 標籤
4. 設定 Webhook URL 為：`https://你的ngrok網址.ngrok-free.app/webhook`
5. 啟用 **Use webhook**
6. 點擊 **Verify** 確認連接成功
7. 關閉 **Auto-reply messages**（重要！）
8. 關閉 **Greeting messages**

## 第六步：測試機器人

### A. 加入機器人為好友

在 LINE Developers Console 的 Messaging API 頁面找到 QR Code，掃描加入好友。

### B. 創建測試群組

1. 在 LINE 中創建一個新的群組
2. 將機器人加入群組
3. 在群組中發送測試指令

### C. 測試指令

在群組中發送：

```
/01-28 14:30 專案週會
```

你應該會收到確認訊息：
```
✅ 已設定提醒！

📅 時間：2026-01-28 14:30
📝 事項：專案週會

將在以下時間發送提醒：
• 前 60 分鐘
• 前 30 分鐘
• 整點時刻
```

### D. 測試提醒功能

為了快速測試，可以設定一個 2 小時後的提醒：

```
/01-27 22:00 測試提醒
```

然後等待提醒發送。

## 常見問題

### ❓ 機器人沒有回應？

檢查清單：
- ✅ ngrok 是否正在運行？
- ✅ Webhook URL 是否正確設定？
- ✅ Webhook 驗證是否成功？
- ✅ 是否關閉了自動回覆？
- ✅ LINE_CHANNEL_ACCESS_TOKEN 是否正確？
- ✅ LINE_CHANNEL_SECRET 是否正確？

### ❓ 指令格式錯誤？

正確格式：`/MM-DD HH:mm 事情描述`

注意：
- 月份和日期必須是兩位數（例如：01、09）
- 時間必須是兩位數（例如：09:00、14:30）
- `/` 和時間之間有空格
- 時間和描述之間有空格

### ❓ 提醒沒有發送？

檢查清單：
- ✅ 主程式是否持續運行？
- ✅ 排程器是否啟動？（查看日誌）
- ✅ 時區設定是否正確？（Asia/Taipei）
- ✅ 設定的時間是否在未來？

### ❓ 如何查看日誌？

主程式會在終端機輸出日誌：
```
2026-01-27 20:00:00 - scheduler - INFO - [排程] 開始檢查提醒
2026-01-27 20:00:00 - scheduler - INFO - [排程] 找到 1 個待處理事件
```

## 下一步：部署到雲端

本地測試成功後，參考 [DEPLOYMENT.md](DEPLOYMENT.md) 將機器人部署到 Render、Railway 或 Heroku。

---

需要幫助？查看完整文檔：
- [README.md](README.md) - 專案概覽
- [DEPLOYMENT.md](DEPLOYMENT.md) - 詳細部署指南

祝使用愉快！🎉
