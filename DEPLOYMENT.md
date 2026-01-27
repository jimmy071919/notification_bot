# 🚀 部署指南

## 前置準備

### 1. 建立 LINE Bot

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider（如果還沒有）
3. 建立新的 Messaging API Channel
4. 在 Channel 設定頁面獲取：
   - **Channel Secret**
   - **Channel Access Token**（Long-lived）

### 2. 設定 LINE Bot

在 LINE Developers Console 中：
- 啟用 **Webhook**
- 關閉 **Auto-reply messages**
- 關閉 **Greeting messages**
- 將 Webhook URL 設為：`https://your-domain.com/webhook`

---

## 本地開發部署

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp .env.example .env
```

編輯 `.env` 檔案：

```env
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here
SECRET_KEY=your_secret_key_here
```

### 3. 初始化資料庫

```bash
python init_db.py
```

### 4. 啟動應用

```bash
python main.py
```

### 5. 使用 ngrok 測試

```bash
ngrok http 5000
```

將 ngrok 提供的 HTTPS URL 設定到 LINE Developers Console 的 Webhook URL。

---

## Render 雲端部署

### 1. 準備 GitHub Repository

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin your-github-repo-url
git push -u origin main
```

### 2. 在 Render 創建 Web Service

1. 登入 [Render](https://render.com/)
2. 點擊 **New** → **Web Service**
3. 連接你的 GitHub repository
4. 設定：
   - **Name**: line-reminder-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn main:app --timeout 120 --workers 1`

### 3. 設定環境變數

在 Render Dashboard 的 Environment 頁面添加：

```
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here
SECRET_KEY=random_secret_key_here
TIMEZONE=Asia/Taipei
```

### 4. 部署

點擊 **Create Web Service**，Render 會自動部署。

### 5. 更新 LINE Webhook URL

部署完成後，將 Render 提供的 URL 設定到 LINE Developers Console：

```
https://your-app-name.onrender.com/webhook
```

---

## Railway 雲端部署

### 1. 準備 GitHub Repository（同上）

### 2. 在 Railway 創建專案

1. 登入 [Railway](https://railway.app/)
2. 點擊 **New Project** → **Deploy from GitHub repo**
3. 選擇你的 repository

### 3. 設定環境變數

在 Railway 的 Variables 頁面添加：

```
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_CHANNEL_SECRET=your_secret_here
SECRET_KEY=random_secret_key_here
TIMEZONE=Asia/Taipei
```

### 4. 部署設定

Railway 會自動檢測到 Procfile 並部署。

### 5. 更新 LINE Webhook URL

```
https://your-app-name.railway.app/webhook
```

---

## Heroku 雲端部署

### 1. 安裝 Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Windows
# 下載安裝程式：https://devcenter.heroku.com/articles/heroku-cli
```

### 2. 登入並創建應用

```bash
heroku login
heroku create your-app-name
```

### 3. 設定環境變數

```bash
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_token_here
heroku config:set LINE_CHANNEL_SECRET=your_secret_here
heroku config:set SECRET_KEY=random_secret_key_here
heroku config:set TIMEZONE=Asia/Taipei
```

### 4. 部署

```bash
git push heroku main
```

### 5. 更新 LINE Webhook URL

```
https://your-app-name.herokuapp.com/webhook
```

---

## 驗證部署

### 1. 檢查服務狀態

訪問：`https://your-domain.com/`

應該看到：`LINE 提醒機器人運行中 🤖`

### 2. 測試 Webhook

在 LINE Developers Console 點擊 **Verify** 按鈕測試 Webhook 連接。

### 3. 加入機器人到群組

1. 在 LINE Developers Console 找到 QR Code
2. 掃描 QR Code 加好友
3. 將機器人加入測試群組

### 4. 測試指令

在群組中發送：

```
/01-28 14:30 測試提醒
```

應該收到確認訊息。

---

## 監控與維護

### 查看日誌

**Render:**
```
在 Dashboard → Logs 查看
```

**Railway:**
```
在 Dashboard → Deployments → View Logs
```

**Heroku:**
```bash
heroku logs --tail
```

### 常見問題

**Q: Webhook 驗證失敗？**
- 確認 HTTPS URL 正確
- 確認 Channel Secret 正確
- 檢查伺服器日誌

**Q: 機器人沒有回應？**
- 確認 Channel Access Token 正確
- 確認關閉了自動回覆
- 檢查機器人是否在群組中

**Q: 提醒沒有發送？**
- 確認排程器正在運行
- 檢查資料庫中的事件
- 確認時區設定正確（Asia/Taipei）

---

## 進階設定

### 使用 PostgreSQL（推薦用於生產環境）

在 `.env` 中修改：

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

需要額外安裝：

```bash
pip install psycopg2-binary
```

### 啟用 SSL（PostgreSQL）

```python
# 在 models.py 修改
engine = create_engine(
    Config.DATABASE_URL,
    connect_args={"sslmode": "require"}
)
```

---

## 安全建議

1. ✅ 永遠不要將 `.env` 提交到 Git
2. ✅ 使用強隨機的 SECRET_KEY
3. ✅ 定期輪換 LINE Access Token
4. ✅ 在生產環境使用 PostgreSQL
5. ✅ 啟用 HTTPS（雲端平台自動提供）
6. ✅ 限制 Webhook 來源 IP（可選）

---

祝部署順利！🎉
