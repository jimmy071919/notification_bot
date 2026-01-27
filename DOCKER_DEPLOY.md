# Docker Compose 部署指南

## 📋 前置準備

### 1. 安裝 Docker 和 Docker Compose
- Windows: 安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: 
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  sudo apt install docker-compose
  ```

### 2. 準備環境變數
複製 `.env.example` 為 `.env` 並填入你的 LINE Bot 憑證：

```bash
cp .env.example .env
```

編輯 `.env` 文件：
```env
# LINE Bot 設定 (必填)
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret

# Flask 設定
FLASK_ENV=production
SECRET_KEY=請更換為隨機字串

# 資料庫設定
DATABASE_URL=sqlite:////app/data/reminders.db

# 時區設定
TIMEZONE=Asia/Taipei
```

## 🚀 部署步驟

### 方法一：使用 Docker Compose（推薦）

1. **啟動服務**
   ```bash
   docker-compose up -d
   ```

2. **查看日誌**
   ```bash
   docker-compose logs -f
   ```

3. **停止服務**
   ```bash
   docker-compose down
   ```

4. **重新部署（重建映像）**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### 方法二：手動 Docker 指令

1. **構建映像**
   ```bash
   docker build -t line-reminder-bot .
   ```

2. **運行容器**
   ```bash
   docker run -d \
     --name line-reminder-bot \
     -p 5000:5000 \
     -v $(pwd)/data:/app/data \
     --env-file .env \
     --restart unless-stopped \
     line-reminder-bot
   ```

3. **查看日誌**
   ```bash
   docker logs -f line-reminder-bot
   ```

## 🔧 管理指令

### 查看運行狀態
```bash
docker-compose ps
```

### 進入容器
```bash
docker-compose exec linebot bash
```

### 查看資料庫
```bash
docker-compose exec linebot python -c "from models import Session, Event; print([e.to_dict() for e in Session().query(Event).all()])"
```

### 重啟服務
```bash
docker-compose restart
```

### 更新代碼後重新部署
```bash
docker-compose down
docker-compose build
docker-compose up -d
```

## 📊 監控

### 檢查容器健康狀態
```bash
docker inspect --format='{{.State.Health.Status}}' line-reminder-bot
```

### 查看容器資源使用
```bash
docker stats line-reminder-bot
```

## 🌐 設定 LINE Webhook URL

1. 確認服務正常運行
2. 如果部署在本地，使用 ngrok 建立隧道：
   ```bash
   ngrok http 5000
   ```
3. 前往 [LINE Developers Console](https://developers.line.biz/console/)
4. 設定 Webhook URL: `https://你的網域或ngrok網址/webhook`
5. 啟用 "Use webhook"
6. 點擊 "Verify" 驗證

## 🗂️ 資料持久化

資料庫檔案儲存在 `./data/reminders.db`，即使容器重啟也不會遺失資料。

### 備份資料庫
```bash
cp ./data/reminders.db ./data/reminders.db.backup
```

### 還原資料庫
```bash
cp ./data/reminders.db.backup ./data/reminders.db
docker-compose restart
```

## ⚠️ 故障排除

### 服務無法啟動
```bash
# 查看詳細錯誤訊息
docker-compose logs linebot

# 檢查環境變數是否正確
docker-compose exec linebot env | grep LINE
```

### 無法連接到資料庫
```bash
# 檢查資料目錄權限
ls -la ./data

# 重新初始化資料庫
docker-compose exec linebot python init_db.py
```

### 記憶體不足
編輯 `docker-compose.yml`，添加資源限制：
```yaml
services:
  linebot:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## 🔒 安全建議

1. **不要將 `.env` 文件提交到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **定期更新映像**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

3. **使用強密碼作為 SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## 📝 生產環境建議

1. **使用反向代理（Nginx）**
2. **啟用 HTTPS（Let's Encrypt）**
3. **設定自動備份**
4. **監控日誌和警報**
5. **定期更新依賴套件**

## 🎯 快速測試

部署完成後，在 LINE 群組中發送：
```
/01-28 15:00 測試提醒
/list
```

應該會收到確認訊息和行程清單。
