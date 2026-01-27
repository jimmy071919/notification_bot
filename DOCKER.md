# 🐳 Docker Compose 部署指南

## 前置準備

### 1. 安裝 Docker

**Windows:**
- 下載並安裝 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
- 安裝後重啟電腦

**macOS:**
- 下載並安裝 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安裝 Docker Compose
sudo apt-get install docker-compose-plugin
```

### 2. 驗證安裝

```bash
docker --version
docker compose version
```

---

## 快速開始

### 1. 設定環境變數

複製環境變數範本：

```bash
# Windows PowerShell
copy .env.docker .env

# Linux/macOS
cp .env.docker .env
```

編輯 `.env` 檔案，填入你的 LINE Bot 憑證：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_Channel_Secret
SECRET_KEY=隨機生成的密鑰
```

### 2. 啟動服務

```bash
docker compose up -d
```

第一次啟動會自動構建映像，需要幾分鐘時間。

### 3. 查看日誌

```bash
# 查看即時日誌
docker compose logs -f

# 查看最近 100 行日誌
docker compose logs --tail=100
```

### 4. 驗證運行狀態

訪問 `http://localhost:5000`，應該看到：
```
LINE 提醒機器人運行中 🤖
```

### 5. 設定 LINE Webhook

如果是本地開發，使用 ngrok：

```bash
ngrok http 5000
```

將 ngrok 提供的 HTTPS URL 設定到 LINE Developers Console：
```
https://your-ngrok-url.ngrok-free.app/webhook
```

---

## 常用指令

### 啟動服務

```bash
# 啟動（背景運行）
docker compose up -d

# 啟動（前景運行，可看到日誌）
docker compose up

# 重新構建並啟動
docker compose up -d --build
```

### 停止服務

```bash
# 停止服務
docker compose stop

# 停止並移除容器
docker compose down

# 停止並移除容器、網路、映像
docker compose down --rmi all

# 停止並移除所有（包含資料庫）
docker compose down -v
```

### 查看狀態

```bash
# 查看運行中的容器
docker compose ps

# 查看日誌
docker compose logs

# 即時查看日誌
docker compose logs -f

# 查看特定服務的日誌
docker compose logs -f linebot
```

### 重啟服務

```bash
# 重啟所有服務
docker compose restart

# 重啟特定服務
docker compose restart linebot
```

### 進入容器

```bash
# 進入容器的 Shell
docker compose exec linebot /bin/bash

# 執行單一指令
docker compose exec linebot python test.py
```

### 更新應用

```bash
# 拉取最新代碼後
git pull

# 重新構建並啟動
docker compose up -d --build
```

---

## 資料持久化

資料庫檔案保存在 `./data/reminders.db`，即使容器刪除，資料也不會丟失。

### 備份資料庫

```bash
# 複製資料庫檔案
cp ./data/reminders.db ./data/reminders.db.backup

# 或使用日期標記
cp ./data/reminders.db ./data/reminders_$(date +%Y%m%d_%H%M%S).db
```

### 還原資料庫

```bash
# 停止服務
docker compose down

# 還原備份
cp ./data/reminders.db.backup ./data/reminders.db

# 重新啟動
docker compose up -d
```

---

## 開發模式

如果你想在開發時即時更新代碼（不需重新構建），編輯 `docker-compose.yml`：

```yaml
services:
  linebot:
    # ... 其他設定
    volumes:
      - ./data:/app/data
      - .:/app  # 取消此行註解
    environment:
      - FLASK_ENV=development  # 改為 development
```

然後重啟：

```bash
docker compose down
docker compose up -d
```

---

## 生產環境部署

### 使用 PostgreSQL（推薦）

創建 `docker-compose.prod.yml`：

```yaml
version: '3.8'

services:
  linebot:
    build: .
    container_name: line-reminder-bot
    restart: unless-stopped
    ports:
      - "5000:5000"
    environment:
      - LINE_CHANNEL_ACCESS_TOKEN=${LINE_CHANNEL_ACCESS_TOKEN}
      - LINE_CHANNEL_SECRET=${LINE_CHANNEL_SECRET}
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://linebot:linebot123@postgres:5432/linebot
      - TIMEZONE=Asia/Taipei
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - linebot-network

  postgres:
    image: postgres:15-alpine
    container_name: line-reminder-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=linebot
      - POSTGRES_PASSWORD=linebot123
      - POSTGRES_DB=linebot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - linebot-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U linebot"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  linebot-network:
    driver: bridge

volumes:
  postgres_data:
```

啟動生產環境：

```bash
docker compose -f docker-compose.prod.yml up -d
```

記得在 `requirements.txt` 添加：
```
psycopg2-binary==2.9.9
```

### 使用 Nginx 反向代理

創建 `docker-compose.nginx.yml`：

```yaml
version: '3.8'

services:
  linebot:
    # ... 同上
    expose:
      - "5000"
    # 移除 ports 映射

  nginx:
    image: nginx:alpine
    container_name: line-reminder-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - linebot
    networks:
      - linebot-network
```

---

## 監控與日誌

### 查看資源使用

```bash
# 查看容器資源使用情況
docker stats

# 查看磁碟使用
docker system df
```

### 清理未使用的資源

```bash
# 清理未使用的映像
docker image prune -a

# 清理所有未使用的資源
docker system prune -a
```

### 日誌輪替

Docker Compose 已配置日誌輪替：
- 每個日誌檔案最大 10MB
- 保留最近 3 個日誌檔案

---

## 疑難排解

### 容器無法啟動

```bash
# 查看詳細日誌
docker compose logs linebot

# 檢查容器狀態
docker compose ps -a
```

### 端口被佔用

如果 5000 端口被佔用，修改 `docker-compose.yml`：

```yaml
ports:
  - "8000:5000"  # 將本機端口改為 8000
```

### 權限問題（Linux）

```bash
# 給予資料目錄適當權限
sudo chown -R $USER:$USER ./data
chmod 755 ./data
```

### 記憶體不足

調整 Docker Desktop 設定：
- 開啟 Docker Desktop
- Settings → Resources → Memory
- 增加記憶體限制（建議至少 2GB）

### 無法連接到資料庫

```bash
# 檢查資料庫檔案權限
ls -la ./data/

# 重建資料庫
docker compose down
rm -f ./data/reminders.db
docker compose up -d
```

---

## 安全建議

1. ✅ 永遠不要提交 `.env` 到 Git
2. ✅ 使用強隨機的 `SECRET_KEY`
3. ✅ 定期更新 Docker 映像
4. ✅ 生產環境使用 PostgreSQL
5. ✅ 使用 HTTPS（Nginx + Let's Encrypt）
6. ✅ 限制容器資源使用

生成隨機 SECRET_KEY：

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

---

## 效能優化

### 減少映像大小

Dockerfile 已使用 `python:3.11-slim` 基礎映像。

查看映像大小：
```bash
docker images | grep line-reminder-bot
```

### 多階段構建（可選）

如果需要進一步優化，可以使用多階段構建：

```dockerfile
# 構建階段
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 運行階段
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", "main:app", ...]
```

---

## 升級指南

### 升級 Python 版本

1. 修改 `Dockerfile` 第一行：
   ```dockerfile
   FROM python:3.12-slim
   ```

2. 修改 `runtime.txt`（如果有）

3. 重新構建：
   ```bash
   docker compose up -d --build
   ```

### 升級依賴套件

1. 更新 `requirements.txt`
2. 重新構建映像
3. 測試新版本
4. 部署

---

需要幫助？查看其他文檔：
- [README.md](README.md) - 專案概覽
- [QUICKSTART.md](QUICKSTART.md) - 快速開始
- [DEPLOYMENT.md](DEPLOYMENT.md) - 雲端部署

祝部署順利！🐳
