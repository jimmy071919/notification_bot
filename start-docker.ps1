# LINE Bot Docker 快速啟動腳本 (Windows PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "LINE 提醒機器人 - Docker 快速啟動" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 檢查 Docker 是否安裝
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker 環境檢查通過" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ 錯誤：未檢測到 Docker" -ForegroundColor Red
    Write-Host "請先安裝 Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

# 檢查 Docker Compose 是否可用
try {
    $composeVersion = docker compose version
} catch {
    Write-Host "❌ 錯誤：未檢測到 Docker Compose" -ForegroundColor Red
    Write-Host "請確保 Docker Compose 已安裝"
    exit 1
}

# 檢查 .env 文件是否存在
if (-not (Test-Path .env)) {
    Write-Host "⚠️  未找到 .env 檔案" -ForegroundColor Yellow
    Write-Host "正在從範本創建 .env 檔案..."
    
    if (Test-Path .env.docker) {
        Copy-Item .env.docker .env
        Write-Host "✅ 已創建 .env 檔案（從 .env.docker）" -ForegroundColor Green
    } elseif (Test-Path .env.example) {
        Copy-Item .env.example .env
        Write-Host "✅ 已創建 .env 檔案（從 .env.example）" -ForegroundColor Green
    } else {
        Write-Host "❌ 錯誤：找不到環境變數範本" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "⚠️  請編輯 .env 檔案並填入你的 LINE Bot 憑證：" -ForegroundColor Yellow
    Write-Host "   - LINE_CHANNEL_ACCESS_TOKEN"
    Write-Host "   - LINE_CHANNEL_SECRET"
    Write-Host "   - SECRET_KEY"
    Write-Host ""
    Read-Host "按 Enter 鍵繼續（完成設定後）"
}

Write-Host "正在啟動 Docker 容器..." -ForegroundColor Cyan
Write-Host ""

# 選擇配置文件
Write-Host "請選擇部署模式：" -ForegroundColor Yellow
Write-Host "1) 開發模式（SQLite）"
Write-Host "2) 生產模式（PostgreSQL）"
$mode = Read-Host "請選擇 [1-2]"

Write-Host ""

switch ($mode) {
    "1" {
        Write-Host "🚀 啟動開發模式..." -ForegroundColor Green
        docker compose up -d
    }
    "2" {
        Write-Host "🚀 啟動生產模式（PostgreSQL）..." -ForegroundColor Green
        docker compose -f docker-compose.prod.yml up -d
    }
    default {
        Write-Host "❌ 無效的選擇" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "等待服務啟動..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# 檢查容器狀態
Write-Host ""
Write-Host "📊 容器狀態：" -ForegroundColor Cyan
docker compose ps

Write-Host ""
Write-Host "✅ 啟動完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📍 服務地址：" -ForegroundColor Cyan
Write-Host "   - LINE Bot: http://localhost:5000"
Write-Host "   - Webhook URL: http://localhost:5000/webhook"
Write-Host ""
Write-Host "📝 常用指令：" -ForegroundColor Cyan
Write-Host "   - 查看日誌: docker compose logs -f"
Write-Host "   - 停止服務: docker compose down"
Write-Host "   - 重啟服務: docker compose restart"
Write-Host ""
Write-Host "📚 更多資訊請參考 DOCKER.md" -ForegroundColor Cyan
Write-Host ""
