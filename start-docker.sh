#!/bin/bash
# LINE Bot Docker 快速啟動腳本

set -e

echo "========================================"
echo "LINE 提醒機器人 - Docker 快速啟動"
echo "========================================"
echo ""

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "❌ 錯誤：未檢測到 Docker"
    echo "請先安裝 Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 檢查 Docker Compose 是否可用
if ! docker compose version &> /dev/null; then
    echo "❌ 錯誤：未檢測到 Docker Compose"
    echo "請確保 Docker Compose 已安裝"
    exit 1
fi

echo "✅ Docker 環境檢查通過"
echo ""

# 檢查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 檔案"
    echo "正在從範本創建 .env 檔案..."
    
    if [ -f .env.docker ]; then
        cp .env.docker .env
        echo "✅ 已創建 .env 檔案（從 .env.docker）"
    elif [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ 已創建 .env 檔案（從 .env.example）"
    else
        echo "❌ 錯誤：找不到環境變數範本"
        exit 1
    fi
    
    echo ""
    echo "⚠️  請編輯 .env 檔案並填入你的 LINE Bot 憑證："
    echo "   - LINE_CHANNEL_ACCESS_TOKEN"
    echo "   - LINE_CHANNEL_SECRET"
    echo "   - SECRET_KEY"
    echo ""
    read -p "按 Enter 鍵繼續（完成設定後）..."
fi

echo "正在啟動 Docker 容器..."
echo ""

# 選擇配置文件
echo "請選擇部署模式："
echo "1) 開發模式（SQLite）"
echo "2) 生產模式（PostgreSQL）"
read -p "請選擇 [1-2]: " mode

case $mode in
    1)
        echo ""
        echo "🚀 啟動開發模式..."
        docker compose up -d
        ;;
    2)
        echo ""
        echo "🚀 啟動生產模式（PostgreSQL）..."
        docker compose -f docker-compose.prod.yml up -d
        ;;
    *)
        echo "❌ 無效的選擇"
        exit 1
        ;;
esac

echo ""
echo "等待服務啟動..."
sleep 5

# 檢查容器狀態
echo ""
echo "📊 容器狀態："
docker compose ps

echo ""
echo "✅ 啟動完成！"
echo ""
echo "📍 服務地址："
echo "   - LINE Bot: http://localhost:5000"
echo "   - Webhook URL: http://localhost:5000/webhook"
echo ""
echo "📝 常用指令："
echo "   - 查看日誌: docker compose logs -f"
echo "   - 停止服務: docker compose down"
echo "   - 重啟服務: docker compose restart"
echo ""
echo "📚 更多資訊請參考 DOCKER.md"
echo ""
