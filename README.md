# 🤖 LINE 群組提醒機器人 (LGSB)

自動化的 LINE 群組提醒機器人，可在指定時間前自動發送提醒訊息。

## 功能特色

- ✅ 支援 `/MM-DD HH:mm 事情描述` 格式的指令
- ⏰ 自動在事件前 60分鐘、30分鐘和整點發送提醒
- 🗓️ 智能年份處理（自動處理跨年情境）
- 🌏 台灣時區 (UTC+8)

## 安裝步驟

### 🐳 使用 Docker Compose（推薦）

1. **設定環境變數：**
   ```bash
   cp .env.docker .env
   ```
   編輯 `.env` 檔案，填入你的 LINE Bot 憑證。

2. **啟動服務：**
   ```bash
   docker compose up -d
   ```

3. **查看日誌：**
   ```bash
   docker compose logs -f
   ```

詳細說明請參考 [DOCKER.md](DOCKER.md)

### 📦 傳統安裝方式

1. **安裝依賴套件：**
   ```bash
   pip install -r requirements.txt
   ```

2. **設定環境變數：**
   ```bash
   cp .env.example .env
   ```
   編輯 `.env` 檔案，填入你的 LINE Bot 憑證。

3. **初始化資料庫：**
   ```bash
   python init_db.py
   ```

4. **啟動應用：**
   ```bash
   python main.py
   ```

## 使用方式

在 LINE 群組中輸入：
```
/01-28 14:30 專案週會
```

機器人將自動在以下時間發送提醒：
- 2026-01-28 13:30 （前 60 分鐘）
- 2026-01-28 14:00 （前 30 分鐘）
- 2026-01-28 14:30 （整點）

## 部署

### 🐳 Docker Compose 部署（推薦）

最簡單的部署方式，支援一鍵啟動：

```bash
docker compose up -d
```

完整指南請參考 [DOCKER.md](DOCKER.md)

### ☁️ 雲端平台部署

#### Render 部署

1. 將代碼推送到 GitHub
2. 在 Render 創建新的 Web Service
3. 連接你的 GitHub repository
4. 添加環境變數
5. 部署！

#### Railway 部署

1. 將代碼推送到 GitHub
2. 在 Railway 創建新專案
3. 連接你的 GitHub repository
4. 添加環境變數
5. 部署！

詳細步驟請參考 [DEPLOYMENT.md](DEPLOYMENT.md)

## 技術架構

- **後端框架：** Flask
- **資料庫：** SQLite (可改用 PostgreSQL)
- **排程任務：** APScheduler
- **LINE SDK：** line-bot-sdk

## 授權

MIT License
