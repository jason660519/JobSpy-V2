# JobSpy v2 - AI-Enhanced Job Search Platform

## 項目概述

JobSpy v2 是一個現代化的 AI 增強型求職平台，提供智能職位匹配、個性化推薦和全面的求職管理功能。

## 🚀 快速開始

### 服務地址
- **前端**: http://localhost:3000
- **後端 API**: http://localhost:8000
- **API 文檔**: http://localhost:8000/docs

### 啟動服務

#### 前端服務
```bash
cd frontend
npm run dev
```

#### 後端服務
```bash
cd backend
python -m uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload
```

## Modern Architecture

This is the modernized version of JobSpy, featuring:

- FastAPI Backend: High-performance async API
- React + TypeScript Frontend: Modern, responsive UI  
- AI Vision Integration: OpenAI GPT-4V for intelligent scraping
- Microservices Architecture: Scalable and maintainable
- Docker Support: Easy development and deployment

## Project Structure

    JobSpy-v2/
    |-- backend/           # FastAPI backend application
    |   |-- app/
    |   |   |-- api/       # API 路由
    |   |   |-- core/      # 核心配置 (包含MinIO客戶端)
    |   |   |-- models/    # 數據模型
    |   |   |-- services/  # 業務邏輯 (包含存儲服務)
    |-- frontend/          # React TypeScript frontend
    |   |-- src/
    |   |   |-- components/ # React 組件
    |   |   |-- pages/     # 頁面組件
    |   |   |-- hooks/     # 自定義 Hooks
    |   |   |-- utils/     # 工具函數
    |-- shared/            # Shared types and utilities
    |-- docker/            # Docker configurations
    |-- scripts/           # Utility scripts
    |   |-- minio-init/    # MinIO 初始化腳本
    |-- docs/              # Documentation

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- OpenAI API Key (for AI features)
- MinIO (對象存儲)

### Quick Start

1. Clone and setup:
   git clone <repository>
   cd JobSpy-v2
   cp .env.example .env

2. Start with Docker:
   docker-compose up -d

3. Access applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Configuration

Create .env file with:

    DATABASE_URL=postgresql://jobspy:password@localhost:5432/jobspy
    REDIS_URL=redis://localhost:6379
    MINIO_ENDPOINT=localhost:9000
    MINIO_ACCESS_KEY=admin
    MINIO_SECRET_KEY=password123
    MINIO_SECURE=false
    OPENAI_API_KEY=your_openai_api_key_here
    SECRET_KEY=your_secret_key_here

## 📦 MinIO 對象存儲

### MinIO 使用方式

JobSpy v2 使用 MinIO 作為對象存儲解決方案，實現數據分層存儲架構：

#### 存儲桶結構
- **raw-data**: 存儲爬蟲原始數據檔案
- **ai-processed**: 存儲 AI 解析後的 JSON 檔案
- **cleaned-data**: 存儲清理後的一致格式 JSON 檔案
- **backups**: 存儲備份數據

#### 訪問 MinIO 控制台
```bash
# 啟動服務後訪問
http://localhost:9001
# 登入憑證: admin / password123
```

#### MinIO 初始化
```bash
# 自動創建所需的存儲桶
docker-compose up -d minio
# 等待服務啟動後執行初始化腳本
./scripts/minio-init/setup-buckets.sh
```

## 🔄 ETL Pipeline 運作流程

### 數據處理流程

```mermaid
graph TD
    A[爬蟲抓取] --> B[原始數據存儲]
    B --> C[AI 解析處理]
    C --> D[解析數據存儲]
    D --> E[數據清理]
    E --> F[清理數據存儲]
    F --> G[數據庫載入]
    G --> H[CSV 導出]
```

### 詳細處理階段

1. **原始數據抓取階段**
   - 爬蟲程式抓取各平台職缺資料
   - 原始 HTML/JSON 數據存儲至 `raw-data` 桶
   - 檔案路徑格式: `{platform}/{date}/{search_query}.raw`

2. **AI 解析處理階段**
   - 使用 OpenAI GPT-4 Vision 解析原始數據
   - 結構化 JSON 數據存儲至 `ai-processed` 桶
   - 檔案路徑格式: `{platform}/{date}/{search_query}_ai_processed.json`

3. **數據清理階段**
   - 標準化數據格式和欄位
   - 去重和數據驗證
   - 清理後數據存儲至 `cleaned-data` 桶
   - 檔案路徑格式: `{platform}/{date}/{search_query}_cleaned.json`

4. **數據庫載入階段**
   - 將清理後的數據載入 PostgreSQL
   - 建立索引和關聯關係
   - 支援增量更新

5. **CSV 導出階段**
   - 從數據庫查詢數據
   - 導出為 CSV 格式供下載
   - 支援自定義欄位和篩選條件

### 檔案存放位置

#### 原始檔案 (Raw Files)
```
MinIO Bucket: raw-data
路徑結構: {platform}/{date}/{search_query}.raw
範例: linkedin/2024-01-20/software_engineer.raw
```

#### 解析後 JSON 檔案 (Parsed JSON)
```
MinIO Bucket: ai-processed
路徑結構: {platform}/{date}/{search_query}_ai_processed.json
範例: linkedin/2024-01-20/software_engineer_ai_processed.json
```

#### 整理後 CSV 檔案 (Processed CSV)
```
本地存儲: ./exports/csv/
路徑結構: jobs_export_{timestamp}.csv
範例: jobs_export_20240120_143022.csv

或透過 API 動態生成下載
```

#### 清理後 JSON 檔案 (Cleaned JSON)
```
MinIO Bucket: cleaned-data
路徑結構: {platform}/{date}/{search_query}_cleaned.json
範例: linkedin/2024-01-20/software_engineer_cleaned.json
```

## Testing

    # Backend tests
    cd backend
    pytest
    
    # Frontend tests
    cd frontend
    npm test
    
    # MinIO 連接測試
    curl http://localhost:8000/api/v1/storage/buckets

## Key Features

- AI-Enhanced Scraping with GPT-4 Vision
- Real-time search results
- Progressive Web App support
- Responsive design
- Advanced filtering
- Async processing
- Redis caching
- Database indexing

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - see LICENSE file

## Migration from v1

If migrating from original JobSpy:

1. Run migration script: python scripts/migration/migrate_legacy.py
2. Copy any custom configurations
3. Test functionality with new API endpoints
4. Update any integrations