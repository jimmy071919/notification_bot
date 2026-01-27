# LINE 提醒機器人 - Docker 快速部署腳本 (PowerShell)

Write-Host "🚀 開始部署 LINE 提醒機器人..." -ForegroundColor Green

# 檢查 .env 文件
if (-not (Test-Path .env)) {
    Write-Host "⚠️  未找到 .env 文件，從範例複製..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "❗ 請編輯 .env 文件並填入你的 LINE Bot 憑證" -ForegroundColor Red
    Write-Host "   LINE_CHANNEL_ACCESS_TOKEN=你的token"
    Write-Host "   LINE_CHANNEL_SECRET=你的secret"
    exit 1
}

# 創建資料目錄
New-Item -ItemType Directory -Force -Path data | Out-Null
Write-Host "✅ 資料目錄已創建" -ForegroundColor Green

# 停止舊容器
Write-Host "🛑 停止舊容器..." -ForegroundColor Yellow
docker-compose down 2>$null

# 構建映像
Write-Host "🔨 構建 Docker 映像..." -ForegroundColor Cyan
docker-compose build

# 啟動服務
Write-Host "🚀 啟動服務..." -ForegroundColor Green
docker-compose up -d

# 等待服務啟動
Write-Host "⏳ 等待服務啟動..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 檢查服務狀態
$status = docker-compose ps
if ($status -match "Up") {
    Write-Host "✅ 服務已成功啟動！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 服務狀態：" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
    Write-Host "📝 查看日誌：" -ForegroundColor Cyan
    Write-Host "   docker-compose logs -f"
    Write-Host ""
    Write-Host "🌐 Webhook URL (本地測試需使用 ngrok)：" -ForegroundColor Cyan
    Write-Host "   http://你的網域或IP:5000/webhook"
} else {
    Write-Host "❌ 服務啟動失敗，請查看日誌：" -ForegroundColor Red
    docker-compose logs
    exit 1
}
