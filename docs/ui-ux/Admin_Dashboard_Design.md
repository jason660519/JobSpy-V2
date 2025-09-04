# 後台管理頁面設計規格

## 📋 設計概述

### 設計目標
- **數據驅動** - 提供全面的數據分析和監控儀表板
- **權限管理** - 細粒度的角色權限控制系統
- **操作效率** - 簡化管理員日常操作流程
- **系統監控** - 即時系統狀態和性能監控
- **用戶管理** - 完整的用戶生命週期管理

### 技術要求
- **框架**: React 18 + TypeScript + Bootstrap 5
- **圖表庫**: Chart.js / Recharts
- **表格組件**: React Table
- **狀態管理**: Zustand
- **API 整合**: TanStack Query
- **國際化**: i18next
- **圖標**: Lucide React

## 🎨 整體佈局設計

### 管理後台架構

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              頂部導航欄                                         │
│  [Logo] JobSpy Admin    [搜尋]    [通知🔔]  [用戶頭像▼]  [設定⚙️]  [登出]      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ ┌─────────────────┐ ┌─────────────────────────────────────────────────────────┐ │
│ │                 │ │                                                         │ │
│ │   左側導航欄     │ │                   主內容區域                            │ │
│ │                 │ │                                                         │ │
│ │ 📊 儀表板        │ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ 👥 用戶管理      │ │ │                                                     │ │ │
│ │ 💼 職位管理      │ │ │                 動態內容區                          │ │ │
│ │ 📈 數據分析      │ │ │                                                     │ │ │
│ │ ⚙️ 系統設定      │ │ │                                                     │ │ │
│ │ 🔐 權限管理      │ │ │                                                     │ │ │
│ │ 📝 內容管理      │ │ │                                                     │ │ │
│ │ 🔔 通知中心      │ │ │                                                     │ │ │
│ │ 📋 審核管理      │ │ │                                                     │ │ │
│ │ 🛠️ 系統監控      │ │ │                                                     │ │ │
│ │ 📊 報表中心      │ │ │                                                     │ │ │
│ │ 🔧 API 管理      │ │ │                                                     │ │ │
│ │                 │ │ └─────────────────────────────────────────────────────┘ │ │
│ │ ───────────────  │ │                                                         │ │
│ │ 🏠 返回前台      │ │                                                         │ │
│ │ 📚 說明文件      │ │                                                         │ │
│ │ 🆘 技術支援      │ │                                                         │ │
│ └─────────────────┘ └─────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              狀態欄                                             │
│  系統狀態: 🟢 正常  |  在線用戶: 1,234  |  CPU: 45%  |  記憶體: 67%  |  最後更新: 2分鐘前 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 色彩方案

```css
/* 管理後台專用色彩 */
:root {
  --admin-primary: #1e40af;
  --admin-primary-hover: #1d4ed8;
  --admin-secondary: #64748b;
  --admin-success: #059669;
  --admin-warning: #d97706;
  --admin-danger: #dc2626;
  --admin-info: #0284c7;
  
  --admin-bg-primary: #f8fafc;
  --admin-bg-secondary: #ffffff;
  --admin-bg-dark: #0f172a;
  
  --admin-sidebar-bg: #1e293b;
  --admin-sidebar-text: #cbd5e1;
  --admin-sidebar-active: #3b82f6;
  
  --admin-border: #e2e8f0;
  --admin-text-primary: #1e293b;
  --admin-text-secondary: #64748b;
  --admin-text-muted: #94a3b8;
}
```

## 📊 儀表板設計

### 主儀表板佈局

```html
<div className="dashboard-container">
  <!-- 關鍵指標卡片 -->
  <div className="row g-4 mb-4">
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center">
            <div className="flex-shrink-0">
              <div className="bg-primary bg-opacity-10 rounded-3 p-3">
                <i className="lucide-users text-primary fs-4"></i>
              </div>
            </div>
            <div className="flex-grow-1 ms-3">
              <h6 className="text-muted mb-1">總用戶數</h6>
              <h3 className="mb-0">12,847</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +12.5% 本月
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center">
            <div className="flex-shrink-0">
              <div className="bg-success bg-opacity-10 rounded-3 p-3">
                <i className="lucide-briefcase text-success fs-4"></i>
              </div>
            </div>
            <div className="flex-grow-1 ms-3">
              <h6 className="text-muted mb-1">活躍職位</h6>
              <h3 className="mb-0">3,456</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +8.2% 本週
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center">
            <div className="flex-shrink-0">
              <div className="bg-warning bg-opacity-10 rounded-3 p-3">
                <i className="lucide-search text-warning fs-4"></i>
              </div>
            </div>
            <div className="flex-grow-1 ms-3">
              <h6 className="text-muted mb-1">今日搜尋</h6>
              <h3 className="mb-0">8,923</h3>
              <small className="text-danger">
                <i className="lucide-trending-down me-1"></i>
                -3.1% 昨日
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center">
            <div className="flex-shrink-0">
              <div className="bg-info bg-opacity-10 rounded-3 p-3">
                <i className="lucide-dollar-sign text-info fs-4"></i>
              </div>
            </div>
            <div className="flex-grow-1 ms-3">
              <h6 className="text-muted mb-1">月收入</h6>
              <h3 className="mb-0">$45,678</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +15.3% 上月
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 圖表區域 -->
  <div className="row g-4 mb-4">
    <div className="col-xl-8">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0 pb-0">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="card-title mb-0">用戶增長趨勢</h5>
            <div className="dropdown">
              <button className="btn btn-outline-secondary btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                最近 30 天
              </button>
              <ul className="dropdown-menu">
                <li><a className="dropdown-item" href="#">最近 7 天</a></li>
                <li><a className="dropdown-item" href="#">最近 30 天</a></li>
                <li><a className="dropdown-item" href="#">最近 90 天</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="card-body">
          <canvas id="userGrowthChart" height="300"></canvas>
        </div>
      </div>
    </div>
    
    <div className="col-xl-4">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0 pb-0">
          <h5 className="card-title mb-0">平台分佈</h5>
        </div>
        <div className="card-body">
          <canvas id="platformChart" height="300"></canvas>
          <div className="mt-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="d-flex align-items-center">
                <span className="badge bg-primary rounded-circle p-1 me-2"></span>
                104 人力銀行
              </span>
              <span className="fw-semibold">45.2%</span>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="d-flex align-items-center">
                <span className="badge bg-success rounded-circle p-1 me-2"></span>
                1111 人力銀行
              </span>
              <span className="fw-semibold">28.7%</span>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-2">
              <span className="d-flex align-items-center">
                <span className="badge bg-warning rounded-circle p-1 me-2"></span>
                LinkedIn
              </span>
              <span className="fw-semibold">16.3%</span>
            </div>
            <div className="d-flex justify-content-between align-items-center">
              <span className="d-flex align-items-center">
                <span className="badge bg-info rounded-circle p-1 me-2"></span>
                其他
              </span>
              <span className="fw-semibold">9.8%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 最新活動和系統狀態 -->
  <div className="row g-4">
    <div className="col-xl-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0 pb-0">
          <h5 className="card-title mb-0">最新活動</h5>
        </div>
        <div className="card-body">
          <div className="activity-timeline">
            <div className="activity-item">
              <div className="activity-icon bg-success">
                <i className="lucide-user-plus"></i>
              </div>
              <div className="activity-content">
                <p className="mb-1">新用戶註冊: <strong>張小明</strong></p>
                <small className="text-muted">2 分鐘前</small>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon bg-primary">
                <i className="lucide-briefcase"></i>
              </div>
              <div className="activity-content">
                <p className="mb-1">新職位發布: <strong>前端工程師</strong></p>
                <small className="text-muted">15 分鐘前</small>
              </div>
            </div>
            <div className="activity-item">
              <div className="activity-icon bg-warning">
                <i className="lucide-alert-triangle"></i>
              </div>
              <div className="activity-content">
                <p className="mb-1">系統警告: API 回應時間過長</p>
                <small className="text-muted">1 小時前</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0 pb-0">
          <h5 className="card-title mb-0">系統狀態</h5>
        </div>
        <div className="card-body">
          <div className="system-status">
            <div className="status-item">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>API 服務</span>
                <span className="badge bg-success">正常</span>
              </div>
              <div className="progress" style="height: 6px;">
                <div className="progress-bar bg-success" style="width: 98%"></div>
              </div>
              <small className="text-muted">回應時間: 120ms</small>
            </div>
            
            <div className="status-item mt-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>資料庫</span>
                <span className="badge bg-success">正常</span>
              </div>
              <div className="progress" style="height: 6px;">
                <div className="progress-bar bg-success" style="width: 95%"></div>
              </div>
              <small className="text-muted">連線數: 45/100</small>
            </div>
            
            <div className="status-item mt-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span>Redis 快取</span>
                <span className="badge bg-warning">警告</span>
              </div>
              <div className="progress" style="height: 6px;">
                <div className="progress-bar bg-warning" style="width: 78%"></div>
              </div>
              <small className="text-muted">記憶體使用: 78%</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 👥 用戶管理設計

### 用戶列表頁面

```html
<div className="user-management">
  <!-- 頁面標題和操作 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">用戶管理</h2>
      <p className="text-muted mb-0">管理系統中的所有用戶帳號</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-download me-2"></i>
        匯出用戶
      </button>
      <button className="btn btn-primary">
        <i className="lucide-user-plus me-2"></i>
        新增用戶
      </button>
    </div>
  </div>
  
  <!-- 篩選和搜尋 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-4">
          <div className="form-floating">
            <input type="text" className="form-control" id="searchUser" placeholder="搜尋用戶">
            <label for="searchUser">
              <i className="lucide-search me-2"></i>
              搜尋用戶
            </label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <select className="form-select" id="userStatus">
              <option value="">全部狀態</option>
              <option value="active">啟用</option>
              <option value="inactive">停用</option>
              <option value="pending">待驗證</option>
            </select>
            <label for="userStatus">狀態</label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <select className="form-select" id="userRole">
              <option value="">全部角色</option>
              <option value="user">一般用戶</option>
              <option value="premium">付費用戶</option>
              <option value="admin">管理員</option>
            </select>
            <label for="userRole">角色</label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <input type="date" className="form-control" id="dateFrom">
            <label for="dateFrom">註冊日期從</label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="d-flex gap-2 h-100">
            <button className="btn btn-primary flex-fill">
              <i className="lucide-filter"></i>
            </button>
            <button className="btn btn-outline-secondary flex-fill">
              <i className="lucide-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 用戶表格 -->
  <div className="card border-0 shadow-sm">
    <div className="card-body p-0">
      <div className="table-responsive">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>
                <div className="form-check">
                  <input className="form-check-input" type="checkbox" id="selectAll">
                </div>
              </th>
              <th>用戶</th>
              <th>角色</th>
              <th>狀態</th>
              <th>註冊日期</th>
              <th>最後登入</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div className="form-check">
                  <input className="form-check-input" type="checkbox">
                </div>
              </td>
              <td>
                <div className="d-flex align-items-center">
                  <img src="https://via.placeholder.com/40" className="rounded-circle me-3" alt="用戶頭像">
                  <div>
                    <h6 className="mb-0">張小明</h6>
                    <small className="text-muted">zhang@example.com</small>
                  </div>
                </div>
              </td>
              <td>
                <span className="badge bg-primary">付費用戶</span>
              </td>
              <td>
                <span className="badge bg-success">啟用</span>
              </td>
              <td>
                <span className="text-muted">2024-01-15</span>
              </td>
              <td>
                <span className="text-muted">2 小時前</span>
              </td>
              <td>
                <div className="dropdown">
                  <button className="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    操作
                  </button>
                  <ul className="dropdown-menu">
                    <li><a className="dropdown-item" href="#"><i className="lucide-eye me-2"></i>查看詳情</a></li>
                    <li><a className="dropdown-item" href="#"><i className="lucide-edit me-2"></i>編輯用戶</a></li>
                    <li><a className="dropdown-item" href="#"><i className="lucide-key me-2"></i>重設密碼</a></li>
                    <li><hr className="dropdown-divider"></li>
                    <li><a className="dropdown-item text-warning" href="#"><i className="lucide-user-x me-2"></i>停用帳號</a></li>
                    <li><a className="dropdown-item text-danger" href="#"><i className="lucide-trash-2 me-2"></i>刪除用戶</a></li>
                  </ul>
                </div>
              </td>
            </tr>
            <!-- 更多用戶行... -->
          </tbody>
        </table>
      </div>
      
      <!-- 分頁 -->
      <div className="d-flex justify-content-between align-items-center p-3 border-top">
        <div className="text-muted">
          顯示 1-20 筆，共 1,247 筆記錄
        </div>
        <nav>
          <ul className="pagination pagination-sm mb-0">
            <li className="page-item disabled">
              <a className="page-link" href="#">上一頁</a>
            </li>
            <li className="page-item active">
              <a className="page-link" href="#">1</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">2</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">3</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">下一頁</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</div>
```

### 用戶詳情頁面

```html
<div className="user-detail">
  <!-- 用戶基本資訊 -->
  <div className="row g-4 mb-4">
    <div className="col-md-4">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <img src="https://via.placeholder.com/120" className="rounded-circle mb-3" alt="用戶頭像">
          <h5 className="mb-1">張小明</h5>
          <p className="text-muted mb-3">前端工程師</p>
          <div className="d-flex justify-content-center gap-2 mb-3">
            <span className="badge bg-success">啟用</span>
            <span className="badge bg-primary">付費用戶</span>
          </div>
          <div className="d-grid gap-2">
            <button className="btn btn-primary">
              <i className="lucide-mail me-2"></i>
              發送郵件
            </button>
            <button className="btn btn-outline-secondary">
              <i className="lucide-edit me-2"></i>
              編輯資料
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-md-8">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">基本資訊</h5>
        </div>
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-6">
              <label className="form-label text-muted">電子郵件</label>
              <p className="mb-0">zhang@example.com</p>
            </div>
            <div className="col-md-6">
              <label className="form-label text-muted">電話號碼</label>
              <p className="mb-0">+886 912-345-678</p>
            </div>
            <div className="col-md-6">
              <label className="form-label text-muted">註冊日期</label>
              <p className="mb-0">2024-01-15 14:30:25</p>
            </div>
            <div className="col-md-6">
              <label className="form-label text-muted">最後登入</label>
              <p className="mb-0">2024-03-20 09:15:42</p>
            </div>
            <div className="col-md-6">
              <label className="form-label text-muted">登入次數</label>
              <p className="mb-0">127 次</p>
            </div>
            <div className="col-md-6">
              <label className="form-label text-muted">IP 地址</label>
              <p className="mb-0">192.168.1.100</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 活動記錄和統計 -->
  <div className="row g-4">
    <div className="col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">活動統計</h5>
        </div>
        <div className="card-body">
          <div className="row g-3 text-center">
            <div className="col-6">
              <div className="border rounded p-3">
                <h4 className="text-primary mb-1">156</h4>
                <small className="text-muted">搜尋次數</small>
              </div>
            </div>
            <div className="col-6">
              <div className="border rounded p-3">
                <h4 className="text-success mb-1">23</h4>
                <small className="text-muted">收藏職位</small>
              </div>
            </div>
            <div className="col-6">
              <div className="border rounded p-3">
                <h4 className="text-warning mb-1">8</h4>
                <small className="text-muted">申請職位</small>
              </div>
            </div>
            <div className="col-6">
              <div className="border rounded p-3">
                <h4 className="text-info mb-1">45</h4>
                <small className="text-muted">瀏覽時間(小時)</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">最近活動</h5>
        </div>
        <div className="card-body">
          <div className="activity-list">
            <div className="activity-item d-flex align-items-start mb-3">
              <div className="activity-icon bg-primary me-3">
                <i className="lucide-search"></i>
              </div>
              <div className="flex-grow-1">
                <p className="mb-1">搜尋「React 工程師」</p>
                <small className="text-muted">2 小時前</small>
              </div>
            </div>
            <div className="activity-item d-flex align-items-start mb-3">
              <div className="activity-icon bg-success me-3">
                <i className="lucide-heart"></i>
              </div>
              <div className="flex-grow-1">
                <p className="mb-1">收藏職位「前端工程師 - 台北」</p>
                <small className="text-muted">1 天前</small>
              </div>
            </div>
            <div className="activity-item d-flex align-items-start">
              <div className="activity-icon bg-info me-3">
                <i className="lucide-user"></i>
              </div>
              <div className="flex-grow-1">
                <p className="mb-1">更新個人資料</p>
                <small className="text-muted">3 天前</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 💼 職位管理設計

### 職位列表頁面

```html
<div className="job-management">
  <!-- 頁面標題和操作 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">職位管理</h2>
      <p className="text-muted mb-0">管理平台上的所有職位資訊</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-refresh-cw me-2"></i>
        同步職位
      </button>
      <button className="btn btn-primary">
        <i className="lucide-plus me-2"></i>
        手動新增
      </button>
    </div>
  </div>
  
  <!-- 統計卡片 -->
  <div className="row g-4 mb-4">
    <div className="col-md-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <h3 className="text-primary mb-1">3,456</h3>
          <p className="text-muted mb-0">總職位數</p>
        </div>
      </div>
    </div>
    <div className="col-md-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <h3 className="text-success mb-1">2,891</h3>
          <p className="text-muted mb-0">啟用職位</p>
        </div>
      </div>
    </div>
    <div className="col-md-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <h3 className="text-warning mb-1">234</h3>
          <p className="text-muted mb-0">待審核</p>
        </div>
      </div>
    </div>
    <div className="col-md-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <h3 className="text-danger mb-1">331</h3>
          <p className="text-muted mb-0">已過期</p>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 篩選和搜尋 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-3">
          <div className="form-floating">
            <input type="text" className="form-control" id="searchJob" placeholder="搜尋職位">
            <label for="searchJob">
              <i className="lucide-search me-2"></i>
              搜尋職位
            </label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <select className="form-select" id="jobStatus">
              <option value="">全部狀態</option>
              <option value="active">啟用</option>
              <option value="pending">待審核</option>
              <option value="expired">已過期</option>
              <option value="disabled">停用</option>
            </select>
            <label for="jobStatus">狀態</label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <select className="form-select" id="jobPlatform">
              <option value="">全部平台</option>
              <option value="104">104 人力銀行</option>
              <option value="1111">1111 人力銀行</option>
              <option value="linkedin">LinkedIn</option>
              <option value="yourator">Yourator</option>
            </select>
            <label for="jobPlatform">來源平台</label>
          </div>
        </div>
        <div className="col-md-2">
          <div className="form-floating">
            <select className="form-select" id="jobCategory">
              <option value="">全部類別</option>
              <option value="engineering">工程技術</option>
              <option value="design">設計創意</option>
              <option value="marketing">行銷企劃</option>
              <option value="sales">業務銷售</option>
            </select>
            <label for="jobCategory">職位類別</label>
          </div>
        </div>
        <div className="col-md-3">
          <div className="d-flex gap-2">
            <button className="btn btn-primary flex-fill">
              <i className="lucide-filter me-2"></i>
              篩選
            </button>
            <button className="btn btn-outline-secondary">
              <i className="lucide-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 職位表格 -->
  <div className="card border-0 shadow-sm">
    <div className="card-body p-0">
      <div className="table-responsive">
        <table className="table table-hover mb-0">
          <thead className="table-light">
            <tr>
              <th>
                <div className="form-check">
                  <input className="form-check-input" type="checkbox" id="selectAllJobs">
                </div>
              </th>
              <th>職位資訊</th>
              <th>公司</th>
              <th>來源平台</th>
              <th>薪資範圍</th>
              <th>狀態</th>
              <th>發布日期</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <div className="form-check">
                  <input className="form-check-input" type="checkbox">
                </div>
              </td>
              <td>
                <div>
                  <h6 className="mb-1">前端工程師 (React)</h6>
                  <small className="text-muted">台北市信義區 • 3-5年經驗</small>
                </div>
              </td>
              <td>
                <div className="d-flex align-items-center">
                  <img src="https://via.placeholder.com/32" className="rounded me-2" alt="公司 Logo">
                  <span>科技公司 A</span>
                </div>
              </td>
              <td>
                <span className="badge bg-primary">104 人力銀行</span>
              </td>
              <td>
                <span className="fw-semibold">60K - 90K</span>
              </td>
              <td>
                <span className="badge bg-success">啟用</span>
              </td>
              <td>
                <span className="text-muted">2024-03-18</span>
              </td>
              <td>
                <div className="dropdown">
                  <button className="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    操作
                  </button>
                  <ul className="dropdown-menu">
                    <li><a className="dropdown-item" href="#"><i className="lucide-eye me-2"></i>查看詳情</a></li>
                    <li><a className="dropdown-item" href="#"><i className="lucide-edit me-2"></i>編輯職位</a></li>
                    <li><a className="dropdown-item" href="#"><i className="lucide-external-link me-2"></i>查看原始</a></li>
                    <li><hr className="dropdown-divider"></li>
                    <li><a className="dropdown-item text-warning" href="#"><i className="lucide-pause me-2"></i>停用職位</a></li>
                    <li><a className="dropdown-item text-danger" href="#"><i className="lucide-trash-2 me-2"></i>刪除職位</a></li>
                  </ul>
                </div>
              </td>
            </tr>
            <!-- 更多職位行... -->
          </tbody>
        </table>
      </div>
      
      <!-- 批量操作和分頁 -->
      <div className="d-flex justify-content-between align-items-center p-3 border-top">
        <div className="d-flex align-items-center gap-3">
          <span className="text-muted">已選擇 0 筆</span>
          <div className="btn-group">
            <button className="btn btn-sm btn-outline-secondary" disabled>
              批量啟用
            </button>
            <button className="btn btn-sm btn-outline-warning" disabled>
              批量停用
            </button>
            <button className="btn btn-sm btn-outline-danger" disabled>
              批量刪除
            </button>
          </div>
        </div>
        <nav>
          <ul className="pagination pagination-sm mb-0">
            <li className="page-item disabled">
              <a className="page-link" href="#">上一頁</a>
            </li>
            <li className="page-item active">
              <a className="page-link" href="#">1</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">2</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">3</a>
            </li>
            <li className="page-item">
              <a className="page-link" href="#">下一頁</a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  </div>
</div>
```

## 📈 數據分析設計

### 分析儀表板

```html
<div className="analytics-dashboard">
  <!-- 時間範圍選擇 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">數據分析</h2>
      <p className="text-muted mb-0">深入了解平台使用情況和趨勢</p>
    </div>
    <div className="d-flex gap-2">
      <div className="btn-group" role="group">
        <input type="radio" className="btn-check" name="timeRange" id="today" autocomplete="off">
        <label className="btn btn-outline-primary" for="today">今日</label>
        
        <input type="radio" className="btn-check" name="timeRange" id="week" autocomplete="off" checked>
        <label className="btn btn-outline-primary" for="week">本週</label>
        
        <input type="radio" className="btn-check" name="timeRange" id="month" autocomplete="off">
        <label className="btn btn-outline-primary" for="month">本月</label>
        
        <input type="radio" className="btn-check" name="timeRange" id="quarter" autocomplete="off">
        <label className="btn btn-outline-primary" for="quarter">本季</label>
      </div>
      <button className="btn btn-outline-secondary">
        <i className="lucide-download me-2"></i>
        匯出報表
      </button>
    </div>
  </div>
  
  <!-- 核心指標 -->
  <div className="row g-4 mb-4">
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <h6 className="text-muted mb-1">總搜尋次數</h6>
              <h3 className="mb-0">45,678</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +12.5% vs 上週
              </small>
            </div>
            <div className="bg-primary bg-opacity-10 rounded-3 p-3">
              <i className="lucide-search text-primary fs-4"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <h6 className="text-muted mb-1">活躍用戶</h6>
              <h3 className="mb-0">8,923</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +8.2% vs 上週
              </small>
            </div>
            <div className="bg-success bg-opacity-10 rounded-3 p-3">
              <i className="lucide-users text-success fs-4"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <h6 className="text-muted mb-1">平均停留時間</h6>
              <h3 className="mb-0">4m 32s</h3>
              <small className="text-danger">
                <i className="lucide-trending-down me-1"></i>
                -3.1% vs 上週
              </small>
            </div>
            <div className="bg-warning bg-opacity-10 rounded-3 p-3">
              <i className="lucide-clock text-warning fs-4"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-3 col-md-6">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="d-flex align-items-center justify-content-between">
            <div>
              <h6 className="text-muted mb-1">轉換率</h6>
              <h3 className="mb-0">23.4%</h3>
              <small className="text-success">
                <i className="lucide-trending-up me-1"></i>
                +5.7% vs 上週
              </small>
            </div>
            <div className="bg-info bg-opacity-10 rounded-3 p-3">
              <i className="lucide-target text-info fs-4"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 圖表區域 -->
  <div className="row g-4 mb-4">
    <div className="col-xl-8">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="card-title mb-0">搜尋趨勢分析</h5>
            <div className="btn-group btn-group-sm" role="group">
              <input type="radio" className="btn-check" name="chartType" id="line" autocomplete="off" checked>
              <label className="btn btn-outline-secondary" for="line">線圖</label>
              
              <input type="radio" className="btn-check" name="chartType" id="bar" autocomplete="off">
              <label className="btn btn-outline-secondary" for="bar">柱狀圖</label>
            </div>
          </div>
        </div>
        <div className="card-body">
          <canvas id="searchTrendChart" height="300"></canvas>
        </div>
      </div>
    </div>
    
    <div className="col-xl-4">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">熱門搜尋關鍵字</h5>
        </div>
        <div className="card-body">
          <div className="keyword-list">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center">
                <span className="badge bg-primary rounded-pill me-2">1</span>
                <span>React 工程師</span>
              </div>
              <span className="text-muted">2,345</span>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center">
                <span className="badge bg-secondary rounded-pill me-2">2</span>
                <span>前端開發</span>
              </div>
              <span className="text-muted">1,876</span>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center">
                <span className="badge bg-warning rounded-pill me-2">3</span>
                <span>Node.js</span>
              </div>
              <span className="text-muted">1,234</span>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div className="d-flex align-items-center">
                <span className="badge bg-info rounded-pill me-2">4</span>
                <span>Python 工程師</span>
              </div>
              <span className="text-muted">987</span>
            </div>
            <div className="d-flex justify-content-between align-items-center">
              <div className="d-flex align-items-center">
                <span className="badge bg-success rounded-pill me-2">5</span>
                <span>UI/UX 設計師</span>
              </div>
              <span className="text-muted">756</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 地理分佈和設備分析 -->
  <div className="row g-4">
    <div className="col-xl-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">地理分佈</h5>
        </div>
        <div className="card-body">
          <div className="region-stats">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <span>台北市</span>
              <div className="d-flex align-items-center">
                <div className="progress me-3" style="width: 100px; height: 8px;">
                  <div className="progress-bar bg-primary" style="width: 45%"></div>
                </div>
                <span className="text-muted">45.2%</span>
              </div>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <span>新北市</span>
              <div className="d-flex align-items-center">
                <div className="progress me-3" style="width: 100px; height: 8px;">
                  <div className="progress-bar bg-success" style="width: 28%"></div>
                </div>
                <span className="text-muted">28.7%</span>
              </div>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <span>桃園市</span>
              <div className="d-flex align-items-center">
                <div className="progress me-3" style="width: 100px; height: 8px;">
                  <div className="progress-bar bg-warning" style="width: 12%"></div>
                </div>
                <span className="text-muted">12.3%</span>
              </div>
            </div>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <span>台中市</span>
              <div className="d-flex align-items-center">
                <div className="progress me-3" style="width: 100px; height: 8px;">
                  <div className="progress-bar bg-info" style="width: 8%"></div>
                </div>
                <span className="text-muted">8.1%</span>
              </div>
            </div>
            <div className="d-flex justify-content-between align-items-center">
              <span>其他</span>
              <div className="d-flex align-items-center">
                <div className="progress me-3" style="width: 100px; height: 8px;">
                  <div className="progress-bar bg-secondary" style="width: 6%"></div>
                </div>
                <span className="text-muted">5.7%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="col-xl-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">設備分析</h5>
        </div>
        <div className="card-body">
          <canvas id="deviceChart" height="200"></canvas>
          <div className="device-stats mt-3">
            <div className="row text-center">
              <div className="col-4">
                <h5 className="text-primary mb-1">67.3%</h5>
                <small className="text-muted">桌面電腦</small>
              </div>
              <div className="col-4">
                <h5 className="text-success mb-1">28.9%</h5>
                <small className="text-muted">手機</small>
              </div>
              <div className="col-4">
                <h5 className="text-warning mb-1">3.8%</h5>
                <small className="text-muted">平板</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## ⚙️ 系統設定設計

### 系統配置頁面

```html
<div className="system-settings">
  <div className="row g-4">
    <!-- 左側導航 -->
    <div className="col-md-3">
      <div className="card border-0 shadow-sm">
        <div className="card-body p-0">
          <div className="list-group list-group-flush">
            <a href="#general" className="list-group-item list-group-item-action active">
              <i className="lucide-settings me-2"></i>
              一般設定
            </a>
            <a href="#email" className="list-group-item list-group-item-action">
              <i className="lucide-mail me-2"></i>
              郵件設定
            </a>
            <a href="#api" className="list-group-item list-group-item-action">
              <i className="lucide-code me-2"></i>
              API 設定
            </a>
            <a href="#security" className="list-group-item list-group-item-action">
              <i className="lucide-shield me-2"></i>
              安全設定
            </a>
            <a href="#backup" className="list-group-item list-group-item-action">
              <i className="lucide-database me-2"></i>
              備份設定
            </a>
            <a href="#maintenance" className="list-group-item list-group-item-action">
              <i className="lucide-wrench me-2"></i>
              維護模式
            </a>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右側內容 -->
    <div className="col-md-9">
      <!-- 一般設定 -->
      <div className="card border-0 shadow-sm mb-4" id="general">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">一般設定</h5>
        </div>
        <div className="card-body">
          <form>
            <div className="row g-3">
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="text" className="form-control" id="siteName" value="JobSpy">
                  <label for="siteName">網站名稱</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="url" className="form-control" id="siteUrl" value="https://jobspy.com">
                  <label for="siteUrl">網站網址</label>
                </div>
              </div>
              <div className="col-12">
                <div className="form-floating">
                  <textarea className="form-control" id="siteDescription" style="height: 100px;">智能求職平台，AI 驅動的職位搜尋服務</textarea>
                  <label for="siteDescription">網站描述</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <select className="form-select" id="defaultLanguage">
                    <option value="zh">繁體中文</option>
                    <option value="en">English</option>
                    <option value="ja">日本語</option>
                  </select>
                  <label for="defaultLanguage">預設語言</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <select className="form-select" id="timezone">
                    <option value="Asia/Taipei">台北時間 (UTC+8)</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">紐約時間 (UTC-5)</option>
                  </select>
                  <label for="timezone">時區設定</label>
                </div>
              </div>
              <div className="col-12">
                <div className="d-flex justify-content-end">
                  <button type="submit" className="btn btn-primary">
                    <i className="lucide-save me-2"></i>
                    儲存設定
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 郵件設定 -->
      <div className="card border-0 shadow-sm mb-4" id="email">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">郵件設定</h5>
        </div>
        <div className="card-body">
          <form>
            <div className="row g-3">
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="text" className="form-control" id="smtpHost" placeholder="SMTP 主機">
                  <label for="smtpHost">SMTP 主機</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="number" className="form-control" id="smtpPort" value="587">
                  <label for="smtpPort">SMTP 埠號</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="email" className="form-control" id="smtpUsername" placeholder="SMTP 用戶名">
                  <label for="smtpUsername">SMTP 用戶名</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="password" className="form-control" id="smtpPassword" placeholder="SMTP 密碼">
                  <label for="smtpPassword">SMTP 密碼</label>
                </div>
              </div>
              <div className="col-12">
                <div className="form-check">
                  <input className="form-check-input" type="checkbox" id="enableSSL" checked>
                  <label className="form-check-label" for="enableSSL">
                    啟用 SSL/TLS 加密
                  </label>
                </div>
              </div>
              <div className="col-12">
                <div className="d-flex justify-content-between">
                  <button type="button" className="btn btn-outline-secondary">
                    <i className="lucide-send me-2"></i>
                    測試郵件
                  </button>
                  <button type="submit" className="btn btn-primary">
                    <i className="lucide-save me-2"></i>
                    儲存設定
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 🔐 權限管理設計

### 角色權限矩陣

| 功能模組 | 超級管理員 | 系統管理員 | 內容管理員 | 客服人員 | 分析師 |
|---------|-----------|-----------|-----------|----------|--------|
| 用戶管理 | ✅ | ✅ | ❌ | 👁️ | 👁️ |
| 職位管理 | ✅ | ✅ | ✅ | 👁️ | 👁️ |
| 系統設定 | ✅ | ✅ | ❌ | ❌ | ❌ |
| 數據分析 | ✅ | ✅ | 👁️ | 👁️ | ✅ |
| 權限管理 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 審核管理 | ✅ | ✅ | ✅ | ✅ | ❌ |
| 系統監控 | ✅ | ✅ | ❌ | ❌ | 👁️ |

**圖例**: ✅ 完整權限 | 👁️ 僅查看 | ❌ 無權限

## 📱 響應式設計

### 移動端適配

```css
/* 移動端後台適配 */
@media (max-width: 768px) {
  .admin-sidebar {
    position: fixed;
    top: 0;
    left: -250px;
    width: 250px;
    height: 100vh;
    z-index: 1050;
    transition: left 0.3s ease;
  }
  
  .admin-sidebar.show {
    left: 0;
  }
  
  .admin-main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .dashboard-cards {
    grid-template-columns: 1fr;
  }
  
  .table-responsive {
    font-size: 0.875rem;
  }
}
```

## 🚀 技術實現

### 核心組件結構

```typescript
// AdminLayout.tsx
interface AdminLayoutProps {
  children: React.ReactNode;
}

const AdminLayout: React.FC<AdminLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user, permissions } = useAuth();
  
  return (
    <div className="admin-layout">
      <AdminHeader onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      <AdminSidebar isOpen={sidebarOpen} permissions={permissions} />
      <main className="admin-main-content">
        {children}
      </main>
      <AdminStatusBar />
    </div>
  );
};

// Dashboard.tsx
const Dashboard: React.FC = () => {
  const { data: stats } = useQuery('dashboard-stats', fetchDashboardStats);
  const { data: chartData } = useQuery('chart-data', fetchChartData);
  
  return (
    <div className="dashboard">
      <DashboardStats stats={stats} />
      <DashboardCharts data={chartData} />
      <RecentActivity />
      <SystemStatus />
    </div>
  );
};
```

### 狀態管理

```typescript
// stores/adminStore.ts
interface AdminState {
  currentUser: User | null;
  permissions: Permission[];
  sidebarCollapsed: boolean;
  notifications: Notification[];
}

const useAdminStore = create<AdminState>((set) => ({
  currentUser: null,
  permissions: [],
  sidebarCollapsed: false,
  notifications: [],
  
  setCurrentUser: (user: User) => set({ currentUser: user }),
  toggleSidebar: () => set((state) => ({ 
    sidebarCollapsed: !state.sidebarCollapsed 
  })),
  addNotification: (notification: Notification) => set((state) => ({
    notifications: [...state.notifications, notification]
  })),
}));
```

## 🎯 實施計劃

### 第一階段 (2週)
- ✅ 基礎佈局和導航系統
- ✅ 儀表板核心功能
- ✅ 用戶管理基本功能
- ✅ 權限控制系統

### 第二階段 (2週)
- 📋 職位管理完整功能
- 📋 數據分析儀表板
- 📋 系統設定頁面
- 📋 移動端響應式優化

### 第三階段 (1週)
- 📋 高級篩選和搜尋
- 📋 批量操作功能
- 📋 報表匯出功能
- 📋 系統監控和警報

## 🔒 安全性考量

### 訪問控制
- JWT Token 驗證
- 角色基礎權限控制 (RBAC)
- API 端點權限檢查
- 敏感操作二次驗證

### 數據保護
- 敏感數據加密存儲
- 操作日誌記錄
- 定期安全掃描
- CSRF 保護機制

### 監控和審計
- 用戶操作日誌
- 系統訪問記錄
- 異常行為檢測
- 定期安全報告

---

**設計完成日期**: 2024年3月20日  
**版本**: v1.0  
**設計師**: UI/UX 團隊