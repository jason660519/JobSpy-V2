#!/bin/bash

# MinIO Bucket 初始化腳本
# 用於自動創建 JobSpy 項目所需的數據分層 buckets

echo "正在初始化 MinIO buckets..."

# 等待 MinIO 服務啟動
sleep 10

# 設置 MinIO 客戶端別名
mc alias set myminio http://localhost:9000 admin password123

# 創建數據分層的 buckets
echo "創建 raw-data bucket (存儲爬蟲原始數據)..."
mc mb myminio/raw-data

echo "創建 ai-processed bucket (存儲 AI 解析後的 JSON)..."
mc mb myminio/ai-processed

echo "創建 cleaned-data bucket (存儲清理後的一致格式 JSON)..."
mc mb myminio/cleaned-data

echo "創建 backups bucket (存儲備份數據)..."
mc mb myminio/backups

# 設置 bucket 策略（可選）
echo "設置 bucket 訪問策略..."
mc policy set public myminio/raw-data
mc policy set public myminio/ai-processed
mc policy set public myminio/cleaned-data
mc policy set private myminio/backups

echo "MinIO buckets 初始化完成！"
echo "可用的 buckets:"
mc ls myminio