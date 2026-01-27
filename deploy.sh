#!/bin/bash

# LINE 提醒機器人 - Docker 快速部署腳本
set -e

echo "🚀 開始部署 LINE 提醒機器人..."

# 檢查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，從範例複製..."
    cp .env.example .env
    echo "❗ 請編輯 .env 文件並填入你的 LINE Bot 憑證"
    echo "   LINE_CHANNEL_ACCESS_TOKEN=你的token"
    echo "   LINE_CHANNEL_SECRET=你的secret"
    exit 1
fi

# 創建資料目錄
mkdir -p data
echo "✅ 資料目錄已創建"

# 停止舊容器
echo "🛑 停止舊容器..."
docker-compose down 2>/dev/null || true

# 構建映像
echo "🔨 構建 Docker 映像..."
docker-compose build

# 啟動服務
echo "🚀 啟動服務..."
docker-compose up -d

# 等待服務啟動
echo "⏳ 等待服務啟動..."
sleep 5

# 檢查服務狀態
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服務已成功啟動！"
    echo ""
    echo "📊 服務狀態："
    docker-compose ps
    echo ""
    echo "📝 查看日誌："
    echo "   docker-compose logs -f"
    echo ""
    echo "🌐 Webhook URL (本地測試需使用 ngrok)："
    echo "   http://你的網域或IP:5000/webhook"
else
    echo "❌ 服務啟動失敗，請查看日誌："
    docker-compose logs
    exit 1
fi
