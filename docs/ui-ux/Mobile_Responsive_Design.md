# JobSpy v2 移動端響應式設計

## 📱 設計概述

### 設計目標
- **移動優先**：優先考慮移動端用戶體驗，確保核心功能在小螢幕上完美運行
- **觸控友好**：針對觸控操作優化，提供合適的點擊區域和手勢支援
- **性能優化**：針對移動端網路環境和設備性能進行優化
- **一致性體驗**：在不同設備間保持一致的品牌體驗和功能完整性
- **無障礙支援**：確保移動端的無障礙功能完善

### 技術要求
- **響應式框架**：Bootstrap 5 + 自訂 CSS Grid/Flexbox
- **斷點設計**：xs (< 576px), sm (≥ 576px), md (≥ 768px), lg (≥ 992px), xl (≥ 1200px), xxl (≥ 1400px)
- **觸控支援**：React Touch Events + Hammer.js
- **性能優化**：React.lazy + Suspense + Service Worker
- **PWA 支援**：Web App Manifest + Service Worker + Push Notifications

## 🎨 全域響應式設計系統

### 斷點策略
```css
/* 全域響應式變數 */
:root {
  /* 斷點 */
  --breakpoint-xs: 0;
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
  --breakpoint-xxl: 1400px;
  
  /* 移動端專用間距 */
  --mobile-padding: 1rem;
  --mobile-margin: 0.75rem;
  --mobile-gap: 0.5rem;
  
  /* 觸控目標尺寸 */
  --touch-target-min: 44px;
  --touch-target-comfortable: 48px;
  
  /* 移動端字體 */
  --mobile-font-xs: 0.75rem;
  --mobile-font-sm: 0.875rem;
  --mobile-font-base: 1rem;
  --mobile-font-lg: 1.125rem;
  --mobile-font-xl: 1.25rem;
  --mobile-font-2xl: 1.5rem;
  
  /* 移動端陰影 */
  --mobile-shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --mobile-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --mobile-shadow-lg: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 移動端基礎樣式 */
@media (max-width: 767.98px) {
  body {
    font-size: var(--mobile-font-base);
    line-height: 1.5;
    -webkit-text-size-adjust: 100%;
    -webkit-tap-highlight-color: transparent;
  }
  
  /* 移動端容器 */
  .container-fluid {
    padding-left: var(--mobile-padding);
    padding-right: var(--mobile-padding);
  }
  
  /* 觸控目標最小尺寸 */
  .btn, .form-control, .form-select, 
  .nav-link, .dropdown-item, 
  .pagination .page-link {
    min-height: var(--touch-target-min);
    min-width: var(--touch-target-min);
  }
  
  /* 移動端卡片間距 */
  .card {
    margin-bottom: var(--mobile-margin);
    border-radius: 0.5rem;
    box-shadow: var(--mobile-shadow);
  }
  
  /* 移動端表單優化 */
  .form-control, .form-select {
    font-size: var(--mobile-font-base);
    padding: 0.75rem;
  }
  
  /* 移動端按鈕優化 */
  .btn {
    padding: 0.75rem 1.5rem;
    font-size: var(--mobile-font-base);
    border-radius: 0.5rem;
  }
  
  .btn-sm {
    padding: 0.5rem 1rem;
    font-size: var(--mobile-font-sm);
  }
  
  .btn-lg {
    padding: 1rem 2rem;
    font-size: var(--mobile-font-lg);
  }
}
```

## 📄 職位詳情頁移動端設計

### 移動端職位詳情佈局
```html
<!-- 移動端職位詳情 -->
<div class="mobile-job-details">
  <!-- 返回導航 -->
  <div class="mobile-detail-header">
    <div class="container-fluid py-3">
      <div class="d-flex align-items-center gap-3">
        <button class="btn btn-outline-secondary btn-sm" onclick="history.back()">
          <i class="fas fa-arrow-left"></i>
        </button>
        <h1 class="h6 fw-bold mb-0 flex-grow-1 text-truncate">職位詳情</h1>
        <button class="btn btn-outline-warning btn-sm">
          <i class="fas fa-bookmark"></i>
        </button>
        <button class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#shareModal">
          <i class="fas fa-share-alt"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- 職位標題區域 -->
  <div class="mobile-job-header">
    <div class="container-fluid py-4">
      <div class="text-center mb-4">
        <img src="/company-logo.jpg" alt="Company" class="rounded mb-3" width="80" height="80">
        <h1 class="h4 fw-bold mb-2">前端工程師 (React)</h1>
        <p class="text-muted mb-3">科技創新公司 • 台北市信義區</p>
        
        <div class="d-flex justify-content-center gap-3 mb-3">
          <div class="text-center">
            <div class="text-success fw-bold">NT$ 60K - 80K</div>
            <small class="text-muted">月薪</small>
          </div>
          <div class="text-center">
            <div class="fw-bold">3-5 年</div>
            <small class="text-muted">經驗</small>
          </div>
          <div class="text-center">
            <div class="fw-bold">全職</div>
            <small class="text-muted">類型</small>
          </div>
        </div>
        
        <div class="d-flex flex-wrap justify-content-center gap-2 mb-4">
          <span class="badge bg-primary-subtle text-primary">React</span>
          <span class="badge bg-primary-subtle text-primary">TypeScript</span>
          <span class="badge bg-primary-subtle text-primary">Node.js</span>
          <span class="badge bg-primary-subtle text-primary">MongoDB</span>
        </div>
        
        <div class="d-flex gap-2">
          <button class="btn btn-primary flex-grow-1">
            <i class="fas fa-paper-plane me-2"></i>立即申請
          </button>
          <button class="btn btn-outline-primary">
            <i class="fas fa-comments"></i>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 職位內容 -->
  <div class="mobile-job-content">
    <div class="container-fluid">
      <!-- 標籤導航 -->
      <ul class="nav nav-pills nav-fill mb-4" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#description" type="button">職位描述</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" data-bs-toggle="pill" data-bs-target="#requirements" type="button">職位要求</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link" data-bs-toggle="pill" data-bs-target="#company" type="button">公司資訊</button>
        </li>
      </ul>
      
      <!-- 標籤內容 -->
      <div class="tab-content">
        <!-- 職位描述 -->
        <div class="tab-pane fade show active" id="description">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <h5 class="card-title mb-3">工作內容</h5>
              <div class="job-description">
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="fas fa-check text-success me-2"></i>
                    負責前端網頁開發與維護
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check text-success me-2"></i>
                    與 UI/UX 設計師協作，實現設計稿
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check text-success me-2"></i>
                    優化網站性能與用戶體驗
                  </li>
                  <li class="mb-2">
                    <i class="fas fa-check text-success me-2"></i>
                    參與產品功能規劃與技術討論
                  </li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <h5 class="card-title mb-3">福利待遇</h5>
              <div class="row g-3">
                <div class="col-6">
                  <div class="d-flex align-items-center gap-2">
                    <i class="fas fa-calendar-alt text-primary"></i>
                    <span class="small">彈性工時</span>
                  </div>
                </div>
                <div class="col-6">
                  <div class="d-flex align-items-center gap-2">
                    <i class="fas fa-home text-primary"></i>
                    <span class="small">遠端工作</span>
                  </div>
                </div>
                <div class="col-6">
                  <div class="d-flex align-items-center gap-2">
                    <i class="fas fa-graduation-cap text-primary"></i>
                    <span class="small">教育訓練</span>
                  </div>
                </div>
                <div class="col-6">
                  <div class="d-flex align-items-center gap-2">
                    <i class="fas fa-heartbeat text-primary"></i>
                    <span class="small">健康保險</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 職位要求 -->
        <div class="tab-pane fade" id="requirements">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <h5 class="card-title mb-3">必備技能</h5>
              <div class="requirements-list">
                <div class="mb-3">
                  <h6 class="fw-medium mb-2">程式語言</h6>
                  <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-success-subtle text-success">JavaScript</span>
                    <span class="badge bg-success-subtle text-success">TypeScript</span>
                    <span class="badge bg-success-subtle text-success">HTML5</span>
                    <span class="badge bg-success-subtle text-success">CSS3</span>
                  </div>
                </div>
                
                <div class="mb-3">
                  <h6 class="fw-medium mb-2">框架/函式庫</h6>
                  <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-primary-subtle text-primary">React</span>
                    <span class="badge bg-primary-subtle text-primary">Next.js</span>
                    <span class="badge bg-primary-subtle text-primary">Redux</span>
                  </div>
                </div>
                
                <div class="mb-3">
                  <h6 class="fw-medium mb-2">工具</h6>
                  <div class="d-flex flex-wrap gap-2">
                    <span class="badge bg-warning-subtle text-warning">Git</span>
                    <span class="badge bg-warning-subtle text-warning">Webpack</span>
                    <span class="badge bg-warning-subtle text-warning">Docker</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <h5 class="card-title mb-3">加分條件</h5>
              <ul class="list-unstyled">
                <li class="mb-2">
                  <i class="fas fa-plus text-warning me-2"></i>
                  有 Node.js 後端開發經驗
                </li>
                <li class="mb-2">
                  <i class="fas fa-plus text-warning me-2"></i>
                  熟悉 AWS 或 GCP 雲端服務
                </li>
                <li class="mb-2">
                  <i class="fas fa-plus text-warning me-2"></i>
                  有開源專案貢獻經驗
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- 公司資訊 -->
        <div class="tab-pane fade" id="company">
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <div class="d-flex align-items-center gap-3 mb-3">
                <img src="/company-logo.jpg" alt="Company" class="rounded" width="60" height="60">
                <div>
                  <h5 class="mb-1">科技創新公司</h5>
                  <p class="text-muted mb-0 small">軟體開發 • 100-500 人</p>
                </div>
              </div>
              
              <div class="row g-3 mb-4">
                <div class="col-4 text-center">
                  <div class="fw-bold text-primary">4.5</div>
                  <small class="text-muted">公司評分</small>
                </div>
                <div class="col-4 text-center">
                  <div class="fw-bold text-success">25</div>
                  <small class="text-muted">開放職位</small>
                </div>
                <div class="col-4 text-center">
                  <div class="fw-bold text-info">2018</div>
                  <small class="text-muted">成立年份</small>
                </div>
              </div>
              
              <p class="text-muted mb-3">
                我們是一家專注於創新技術的軟體開發公司，致力於為客戶提供最優質的數位解決方案。
                公司文化開放包容，重視員工成長與工作生活平衡。
              </p>
              
              <div class="d-flex gap-2">
                <button class="btn btn-outline-primary btn-sm flex-grow-1">
                  <i class="fas fa-building me-1"></i>查看公司
                </button>
                <button class="btn btn-outline-secondary btn-sm flex-grow-1">
                  <i class="fas fa-briefcase me-1"></i>更多職位
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 相關職位 -->
  <div class="mobile-related-jobs">
    <div class="container-fluid py-4">
      <h5 class="fw-bold mb-3">相關職位推薦</h5>
      
      <div class="row g-3">
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body p-3">
              <div class="d-flex align-items-center gap-3">
                <img src="/company2.jpg" alt="Company" class="rounded" width="40" height="40">
                <div class="flex-grow-1 min-w-0">
                  <h6 class="mb-1 text-truncate">React 開發工程師</h6>
                  <p class="text-muted mb-1 small">另一家科技公司</p>
                  <span class="text-success small fw-medium">NT$ 55K - 75K</span>
                </div>
                <button class="btn btn-outline-primary btn-sm">
                  查看
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- 更多相關職位... -->
      </div>
    </div>
  </div>

  <!-- 固定申請按鈕 -->
  <div class="mobile-apply-fixed">
    <div class="container-fluid py-3">
      <div class="d-flex gap-2">
        <button class="btn btn-outline-warning flex-shrink-0">
          <i class="fas fa-bookmark"></i>
        </button>
        <button class="btn btn-primary flex-grow-1">
          <i class="fas fa-paper-plane me-2"></i>立即申請這個職位
        </button>
      </div>
    </div>
  </div>
</div>
```

### 移動端職位詳情樣式
```css
/* 移動端職位詳情樣式 */
@media (max-width: 767.98px) {
  .mobile-job-details {
    padding-top: 60px;
    padding-bottom: 80px;
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  /* 詳情頁標題 */
  .mobile-detail-header {
    background: #ffffff;
    border-bottom: 1px solid #e9ecef;
    position: sticky;
    top: 60px;
    z-index: 1020;
  }
  
  /* 職位標題區域 */
  .mobile-job-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .mobile-job-header .badge {
    background: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }
  
  .mobile-job-header .btn-primary {
    background: #ffffff;
    color: #667eea;
    border: none;
    font-weight: 600;
  }
  
  .mobile-job-header .btn-outline-primary {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.5);
  }
  
  /* 內容區域 */
  .mobile-job-content {
    background: #f8f9fa;
    padding: 1.5rem 0;
  }
  
  .mobile-job-content .nav-pills .nav-link {
    font-size: var(--mobile-font-sm);
    padding: 0.5rem 0.75rem;
    border-radius: 1rem;
  }
  
  .mobile-job-content .card {
    border-radius: 1rem;
  }
  
  .mobile-job-content .badge {
    font-size: 0.625rem;
    padding: 0.375rem 0.75rem;
    border-radius: 1rem;
  }
  
  /* 相關職位 */
  .mobile-related-jobs {
    background: #ffffff;
    border-top: 1px solid #e9ecef;
  }
  
  /* 固定申請按鈕 */
  .mobile-apply-fixed {
    position: fixed;
    bottom: 70px;
    left: 0;
    right: 0;
    background: #ffffff;
    border-top: 1px solid #e9ecef;
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
    z-index: 1030;
  }
  
  .mobile-apply-fixed .btn {
    font-weight: 600;
  }
}
```

## 👤 用戶資料頁移動端設計

### 移動端用戶資料佈局
```html
<!-- 移動端用戶資料 -->
<div class="mobile-user-profile">
  <!-- 個人資料標題 -->
  <div class="mobile-profile-header">
    <div class="container-fluid py-4">
      <div class="text-center">
        <div class="position-relative d-inline-block mb-3">
          <img src="/avatar.jpg" alt="Avatar" class="rounded-circle" width="100" height="100">
          <button class="btn btn-primary btn-sm position-absolute bottom-0 end-0 rounded-circle" style="width: 32px; height: 32px;">
            <i class="fas fa-camera"></i>
          </button>
        </div>
        <h1 class="h4 fw-bold mb-1">張小明</h1>
        <p class="text-muted mb-3">前端工程師 • 3 年經驗</p>
        
        <div class="row g-3 mb-4">
          <div class="col-4 text-center">
            <div class="fw-bold text-primary">15</div>
            <small class="text-muted">已申請</small>
          </div>
          <div class="col-4 text-center">
            <div class="fw-bold text-success">8</div>
            <small class="text-muted">面試邀請</small>
          </div>
          <div class="col-4 text-center">
            <div class="fw-bold text-warning">23</div>
            <small class="text-muted">收藏職位</small>
          </div>
        </div>
        
        <button class="btn btn-outline-primary">
          <i class="fas fa-edit me-2"></i>編輯個人資料
        </button>
      </div>
    </div>
  </div>

  <!-- 個人資料內容 -->
  <div class="mobile-profile-content">
    <div class="container-fluid">
      <!-- 基本資訊 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0 pb-0">
          <div class="d-flex align-items-center justify-content-between">
            <h5 class="card-title mb-0">基本資訊</h5>
            <button class="btn btn-outline-secondary btn-sm">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </div>
        <div class="card-body pt-3">
          <div class="row g-3">
            <div class="col-12">
              <label class="form-label small text-muted">電子郵件</label>
              <p class="mb-0">zhang.xiaoming@email.com</p>
            </div>
            <div class="col-6">
              <label class="form-label small text-muted">電話號碼</label>
              <p class="mb-0">0912-345-678</p>
            </div>
            <div class="col-6">
              <label class="form-label small text-muted">生日</label>
              <p class="mb-0">1990/05/15</p>
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">居住地址</label>
              <p class="mb-0">台北市信義區</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 工作經歷 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0 pb-0">
          <div class="d-flex align-items-center justify-content-between">
            <h5 class="card-title mb-0">工作經歷</h5>
            <button class="btn btn-outline-secondary btn-sm">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
        <div class="card-body pt-3">
          <div class="timeline">
            <div class="timeline-item mb-4">
              <div class="d-flex gap-3">
                <div class="flex-shrink-0">
                  <img src="/company-logo.jpg" alt="Company" class="rounded" width="48" height="48">
                </div>
                <div class="flex-grow-1">
                  <h6 class="mb-1">前端工程師</h6>
                  <p class="text-muted mb-1 small">科技創新公司</p>
                  <p class="text-muted mb-2 small">2021/03 - 現在 • 2 年 8 個月</p>
                  <p class="mb-0 small">負責前端開發與維護，使用 React、TypeScript 等技術...</p>
                </div>
              </div>
            </div>
            
            <div class="timeline-item">
              <div class="d-flex gap-3">
                <div class="flex-shrink-0">
                  <img src="/company2.jpg" alt="Company" class="rounded" width="48" height="48">
                </div>
                <div class="flex-grow-1">
                  <h6 class="mb-1">初級前端工程師</h6>
                  <p class="text-muted mb-1 small">新創公司</p>
                  <p class="text-muted mb-2 small">2020/06 - 2021/02 • 8 個月</p>
                  <p class="mb-0 small">參與網站開發專案，學習前端開發技術...</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 技能專長 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0 pb-0">
          <div class="d-flex align-items-center justify-content-between">
            <h5 class="card-title mb-0">技能專長</h5>
            <button class="btn btn-outline-secondary btn-sm">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </div>
        <div class="card-body pt-3">
          <div class="mb-3">
            <h6 class="fw-medium mb-2">程式語言</h6>
            <div class="d-flex flex-wrap gap-2">
              <span class="badge bg-primary-subtle text-primary">JavaScript</span>
              <span class="badge bg-primary-subtle text-primary">TypeScript</span>
              <span class="badge bg-primary-subtle text-primary">Python</span>
            </div>
          </div>
          
          <div class="mb-3">
            <h6 class="fw-medium mb-2">框架/函式庫</h6>
            <div class="d-flex flex-wrap gap-2">
              <span class="badge bg-success-subtle text-success">React</span>
              <span class="badge bg-success-subtle text-success">Vue.js</span>
              <span class="badge bg-success-subtle text-success">Next.js</span>
            </div>
          </div>
          
          <div class="mb-3">
            <h6 class="fw-medium mb-2">工具</h6>
            <div class="d-flex flex-wrap gap-2">
              <span class="badge bg-warning-subtle text-warning">Git</span>
              <span class="badge bg-warning-subtle text-warning">Docker</span>
              <span class="badge bg-warning-subtle text-warning">AWS</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 求職偏好 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0 pb-0">
          <div class="d-flex align-items-center justify-content-between">
            <h5 class="card-title mb-0">求職偏好</h5>
            <button class="btn btn-outline-secondary btn-sm">
              <i class="fas fa-edit"></i>
            </button>
          </div>
        </div>
        <div class="card-body pt-3">
          <div class="row g-3">
            <div class="col-6">
              <label class="form-label small text-muted">期望職位</label>
              <p class="mb-0">前端工程師</p>
            </div>
            <div class="col-6">
              <label class="form-label small text-muted">期望薪資</label>
              <p class="mb-0">NT$ 70K - 90K</p>
            </div>
            <div class="col-6">
              <label class="form-label small text-muted">工作地點</label>
              <p class="mb-0">台北市</p>
            </div>
            <div class="col-6">
              <label class="form-label small text-muted">工作類型</label>
              <p class="mb-0">全職</p>
            </div>
            <div class="col-12">
              <label class="form-label small text-muted">求職狀態</label>
              <div class="d-flex align-items-center gap-2">
                <span class="badge bg-success">積極求職中</span>
                <small class="text-muted">對新機會保持開放</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 移動端用戶資料樣式
```css
/* 移動端用戶資料樣式 */
@media (max-width: 767.98px) {
  .mobile-user-profile {
    padding-top: 60px;
    padding-bottom: 70px;
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  /* 個人資料標題 */
  .mobile-profile-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .mobile-profile-header .btn-outline-primary {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.1);
  }
  
  .mobile-profile-header .btn-outline-primary:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.7);
  }
  
  /* 個人資料內容 */
  .mobile-profile-content {
    padding: 1.5rem 0;
  }
  
  .mobile-profile-content .card {
    border-radius: 1rem;
  }
  
  .mobile-profile-content .card-title {
    font-size: var(--mobile-font-lg);
  }
  
  /* 時間軸 */
  .timeline-item {
    position: relative;
  }
  
  .timeline-item:not(:last-child)::after {
    content: '';
    position: absolute;
    left: 24px;
    top: 60px;
    bottom: -16px;
    width: 2px;
    background: #e9ecef;
  }
  
  /* 技能標籤 */
  .mobile-profile-content .badge {
    font-size: 0.625rem;
    padding: 0.375rem 0.75rem;
    border-radius: 1rem;
  }
}
```

## 🔐 登入註冊頁移動端設計

### 移動端登入頁佈局
```html
<!-- 移動端登入頁 -->
<div class="mobile-auth-page">
  <div class="mobile-auth-container">
    <!-- 品牌區域 -->
    <div class="mobile-auth-header">
      <div class="text-center py-5">
        <img src="/logo.svg" alt="JobSpy" height="60" class="mb-4">
        <h1 class="h3 fw-bold mb-2">歡迎回來</h1>
        <p class="text-muted">登入您的帳戶繼續求職之旅</p>
      </div>
    </div>

    <!-- 登入表單 -->
    <div class="mobile-auth-form">
      <div class="container-fluid px-4">
        <form class="needs-validation" novalidate>
          <div class="mb-4">
            <label for="email" class="form-label">電子郵件</label>
            <input type="email" class="form-control form-control-lg" id="email" placeholder="請輸入您的電子郵件" required>
            <div class="invalid-feedback">
              請輸入有效的電子郵件地址
            </div>
          </div>
          
          <div class="mb-4">
            <label for="password" class="form-label">密碼</label>
            <div class="input-group">
              <input type="password" class="form-control form-control-lg" id="password" placeholder="請輸入您的密碼" required>
              <button class="btn btn-outline-secondary" type="button" id="togglePassword">
                <i class="fas fa-eye"></i>
              </button>
            </div>
            <div class="invalid-feedback">
              請輸入密碼
            </div>
          </div>
          
          <div class="d-flex justify-content-between align-items-center mb-4">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="rememberMe">
              <label class="form-check-label" for="rememberMe">
                記住我
              </label>
            </div>
            <a href="/forgot-password" class="text-decoration-none small">忘記密碼？</a>
          </div>
          
          <button type="submit" class="btn btn-primary btn-lg w-100 mb-4">
            <i class="fas fa-sign-in-alt me-2"></i>登入
          </button>
          
          <div class="text-center mb-4">
            <span class="text-muted small">或使用以下方式登入</span>
          </div>
          
          <div class="d-grid gap-2 mb-4">
            <button type="button" class="btn btn-outline-danger">
              <i class="fab fa-google me-2"></i>使用 Google 登入
            </button>
            <button type="button" class="btn btn-outline-primary">
              <i class="fab fa-facebook-f me-2"></i>使用 Facebook 登入
            </button>
          </div>
          
          <div class="text-center">
            <span class="text-muted">還沒有帳戶？</span>
            <a href="/register" class="text-decoration-none fw-medium">立即註冊</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
```

### 移動端註冊頁佈局
```html
<!-- 移動端註冊頁 -->
<div class="mobile-auth-page">
  <div class="mobile-auth-container">
    <!-- 品牌區域 -->
    <div class="mobile-auth-header">
      <div class="text-center py-4">
        <img src="/logo.svg" alt="JobSpy" height="50" class="mb-3">
        <h1 class="h4 fw-bold mb-2">加入 JobSpy</h1>
        <p class="text-muted small">開始您的求職之旅</p>
      </div>
    </div>

    <!-- 註冊表單 -->
    <div class="mobile-auth-form">
      <div class="container-fluid px-4">
        <form class="needs-validation" novalidate>
          <div class="row g-3 mb-3">
            <div class="col-6">
              <label for="firstName" class="form-label">姓氏</label>
              <input type="text" class="form-control" id="firstName" placeholder="姓氏" required>
            </div>
            <div class="col-6">
              <label for="lastName" class="form-label">名字</label>
              <input type="text" class="form-control" id="lastName" placeholder="名字" required>
            </div>
          </div>
          
          <div class="mb-3">
            <label for="email" class="form-label">電子郵件</label>
            <input type="email" class="form-control" id="email" placeholder="請輸入您的電子郵件" required>
            <div class="invalid-feedback">
              請輸入有效的電子郵件地址
            </div>
          </div>
          
          <div class="mb-3">
            <label for="phone" class="form-label">手機號碼</label>
            <input type="tel" class="form-control" id="phone" placeholder="請輸入您的手機號碼" required>
          </div>
          
          <div class="mb-3">
            <label for="password" class="form-label">密碼</label>
            <div class="input-group">
              <input type="password" class="form-control" id="password" placeholder="請設定您的密碼" required>
              <button class="btn btn-outline-secondary" type="button">
                <i class="fas fa-eye"></i>
              </button>
            </div>
            <div class="form-text small">
              密碼至少需要 8 個字元，包含英文字母和數字
            </div>
          </div>
          
          <div class="mb-3">
            <label for="confirmPassword" class="form-label">確認密碼</label>
            <input type="password" class="form-control" id="confirmPassword" placeholder="請再次輸入密碼" required>
          </div>
          
          <div class="mb-4">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" id="agreeTerms" required>
              <label class="form-check-label small" for="agreeTerms">
                我同意 <a href="/terms" class="text-decoration-none">服務條款</a> 和 <a href="/privacy" class="text-decoration-none">隱私政策</a>
              </label>
            </div>
          </div>
          
          <button type="submit" class="btn btn-primary btn-lg w-100 mb-4">
            <i class="fas fa-user-plus me-2"></i>建立帳戶
          </button>
          
          <div class="text-center mb-4">
            <span class="text-muted small">或使用以下方式註冊</span>
          </div>
          
          <div class="d-grid gap-2 mb-4">
            <button type="button" class="btn btn-outline-danger">
              <i class="fab fa-google me-2"></i>使用 Google 註冊
            </button>
            <button type="button" class="btn btn-outline-primary">
              <i class="fab fa-facebook-f me-2"></i>使用 Facebook 註冊
            </button>
          </div>
          
          <div class="text-center">
            <span class="text-muted">已經有帳戶了？</span>
            <a href="/login" class="text-decoration-none fw-medium">立即登入</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>
```

### 移動端登入註冊樣式
```css
/* 移動端登入註冊樣式 */
@media (max-width: 767.98px) {
  .mobile-auth-page {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    padding: 1rem 0;
  }
  
  .mobile-auth-container {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }
  
  .mobile-auth-header {
    color: white;
    text-align: center;
  }
  
  .mobile-auth-form {
    background: #ffffff;
    border-radius: 1.5rem 1.5rem 0 0;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
    padding: 2rem 0;
    min-height: 60vh;
  }
  
  .mobile-auth-form .form-control {
    border-radius: 0.75rem;
    border: 2px solid #e9ecef;
    padding: 0.75rem 1rem;
    font-size: var(--mobile-font-base);
    transition: all 0.2s ease;
  }
  
  .mobile-auth-form .form-control:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
  }
  
  .mobile-auth-form .form-control-lg {
    padding: 1rem 1.25rem;
    font-size: var(--mobile-font-lg);
  }
  
  .mobile-auth-form .btn {
    border-radius: 0.75rem;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.2s ease;
  }
  
  .mobile-auth-form .btn-lg {
    padding: 1rem 2rem;
    font-size: var(--mobile-font-lg);
  }
  
  .mobile-auth-form .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
  }
  
  .mobile-auth-form .btn-outline-danger {
    border-color: #dc3545;
    color: #dc3545;
  }
  
  .mobile-auth-form .btn-outline-danger:hover {
    background: #dc3545;
    color: white;
  }
  
  .mobile-auth-form .btn-outline-primary {
    border-color: #1877f2;
    color: #1877f2;
  }
  
  .mobile-auth-form .btn-outline-primary:hover {
    background: #1877f2;
    color: white;
  }
  
  .mobile-auth-form .form-check-input {
    border-radius: 0.25rem;
  }
  
  .mobile-auth-form .form-check-input:checked {
    background-color: #667eea;
    border-color: #667eea;
  }
  
  .mobile-auth-form a {
    color: #667eea;
  }
  
  .mobile-auth-form a:hover {
    color: #5a67d8;
  }
}
```

## 🔧 後台管理頁移動端設計

### 移動端後台管理佈局
```html
<!-- 移動端後台管理 -->
<div class="mobile-admin-dashboard">
  <!-- 管理員導航 -->
  <div class="mobile-admin-header">
    <div class="container-fluid py-3">
      <div class="d-flex align-items-center justify-content-between">
        <div class="d-flex align-items-center gap-3">
          <button class="btn btn-outline-light btn-sm" data-bs-toggle="offcanvas" data-bs-target="#adminSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <h1 class="h6 fw-bold mb-0 text-white">管理後台</h1>
        </div>
        <div class="d-flex align-items-center gap-2">
          <button class="btn btn-outline-light btn-sm">
            <i class="fas fa-bell"></i>
            <span class="badge bg-danger position-absolute top-0 start-100 translate-middle rounded-pill">3</span>
          </button>
          <div class="dropdown">
            <button class="btn btn-outline-light btn-sm dropdown-toggle" data-bs-toggle="dropdown">
              <img src="/admin-avatar.jpg" alt="Admin" class="rounded-circle" width="24" height="24">
            </button>
            <ul class="dropdown-menu dropdown-menu-end">
              <li><a class="dropdown-item" href="#">個人設定</a></li>
              <li><a class="dropdown-item" href="#">系統設定</a></li>
              <li><hr class="dropdown-divider"></li>
              <li><a class="dropdown-item" href="#">登出</a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 側邊欄 -->
  <div class="offcanvas offcanvas-start" tabindex="-1" id="adminSidebar">
    <div class="offcanvas-header">
      <h5 class="offcanvas-title">管理選單</h5>
      <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
    </div>
    <div class="offcanvas-body p-0">
      <nav class="nav flex-column">
        <a class="nav-link active" href="#dashboard">
          <i class="fas fa-tachometer-alt me-2"></i>儀表板
        </a>
        <a class="nav-link" href="#users">
          <i class="fas fa-users me-2"></i>用戶管理
        </a>
        <a class="nav-link" href="#jobs">
          <i class="fas fa-briefcase me-2"></i>職位管理
        </a>
        <a class="nav-link" href="#companies">
          <i class="fas fa-building me-2"></i>公司管理
        </a>
        <a class="nav-link" href="#applications">
          <i class="fas fa-file-alt me-2"></i>申請管理
        </a>
        <a class="nav-link" href="#analytics">
          <i class="fas fa-chart-bar me-2"></i>數據分析
        </a>
        <a class="nav-link" href="#settings">
          <i class="fas fa-cog me-2"></i>系統設定
        </a>
      </nav>
    </div>
  </div>

  <!-- 主要內容 -->
  <div class="mobile-admin-content">
    <div class="container-fluid py-4">
      <!-- 統計卡片 -->
      <div class="row g-3 mb-4">
        <div class="col-6">
          <div class="card border-0 shadow-sm text-center">
            <div class="card-body py-3">
              <div class="text-primary mb-2">
                <i class="fas fa-users fa-2x"></i>
              </div>
              <h3 class="h5 fw-bold mb-1">1,234</h3>
              <p class="text-muted small mb-0">總用戶數</p>
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="card border-0 shadow-sm text-center">
            <div class="card-body py-3">
              <div class="text-success mb-2">
                <i class="fas fa-briefcase fa-2x"></i>
              </div>
              <h3 class="h5 fw-bold mb-1">567</h3>
              <p class="text-muted small mb-0">活躍職位</p>
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="card border-0 shadow-sm text-center">
            <div class="card-body py-3">
              <div class="text-warning mb-2">
                <i class="fas fa-file-alt fa-2x"></i>
              </div>
              <h3 class="h5 fw-bold mb-1">890</h3>
              <p class="text-muted small mb-0">本月申請</p>
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="card border-0 shadow-sm text-center">
            <div class="card-body py-3">
              <div class="text-info mb-2">
                <i class="fas fa-building fa-2x"></i>
              </div>
              <h3 class="h5 fw-bold mb-1">123</h3>
              <p class="text-muted small mb-0">合作公司</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 快速操作 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0">
          <h5 class="card-title mb-0">快速操作</h5>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-6">
              <button class="btn btn-outline-primary w-100">
                <i class="fas fa-plus me-2"></i>新增職位
              </button>
            </div>
            <div class="col-6">
              <button class="btn btn-outline-success w-100">
                <i class="fas fa-user-plus me-2"></i>新增用戶
              </button>
            </div>
            <div class="col-6">
              <button class="btn btn-outline-warning w-100">
                <i class="fas fa-building me-2"></i>新增公司
              </button>
            </div>
            <div class="col-6">
              <button class="btn btn-outline-info w-100">
                <i class="fas fa-chart-line me-2"></i>查看報表
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最近活動 -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-header bg-transparent border-0">
          <div class="d-flex align-items-center justify-content-between">
            <h5 class="card-title mb-0">最近活動</h5>
            <button class="btn btn-outline-secondary btn-sm">查看全部</button>
          </div>
        </div>
        <div class="card-body p-0">
          <div class="list-group list-group-flush">
            <div class="list-group-item border-0">
              <div class="d-flex align-items-center gap-3">
                <div class="flex-shrink-0">
                  <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <i class="fas fa-user text-white"></i>
                  </div>
                </div>
                <div class="flex-grow-1 min-w-0">
                  <h6 class="mb-1 text-truncate">新用戶註冊</h6>
                  <p class="text-muted mb-0 small">張小明 剛剛註冊了帳戶</p>
                </div>
                <small class="text-muted">2分鐘前</small>
              </div>
            </div>
            
            <div class="list-group-item border-0">
              <div class="d-flex align-items-center gap-3">
                <div class="flex-shrink-0">
                  <div class="bg-success rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <i class="fas fa-briefcase text-white"></i>
                  </div>
                </div>
                <div class="flex-grow-1 min-w-0">
                  <h6 class="mb-1 text-truncate">新職位發布</h6>
                  <p class="text-muted mb-0 small">科技公司發布了前端工程師職位</p>
                </div>
                <small class="text-muted">15分鐘前</small>
              </div>
            </div>
            
            <div class="list-group-item border-0">
              <div class="d-flex align-items-center gap-3">
                <div class="flex-shrink-0">
                  <div class="bg-warning rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <i class="fas fa-file-alt text-white"></i>
                  </div>
                </div>
                <div class="flex-grow-1 min-w-0">
                  <h6 class="mb-1 text-truncate">新的申請</h6>
                  <p class="text-muted mb-0 small">李小華申請了後端工程師職位</p>
                </div>
                <small class="text-muted">30分鐘前</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 系統狀態 -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-transparent border-0">
          <h5 class="card-title mb-0">系統狀態</h5>
        </div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <span class="small">伺服器狀態</span>
                <span class="badge bg-success">正常</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" style="width: 95%"></div>
              </div>
            </div>
            
            <div class="col-12">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <span class="small">資料庫連線</span>
                <span class="badge bg-success">正常</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-success" style="width: 98%"></div>
              </div>
            </div>
            
            <div class="col-12">
              <div class="d-flex align-items-center justify-content-between mb-2">
                <span class="small">API 回應時間</span>
                <span class="badge bg-warning">稍慢</span>
              </div>
              <div class="progress" style="height: 6px;">
                <div class="progress-bar bg-warning" style="width: 75%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 移動端後台管理樣式
```css
/* 移動端後台管理樣式 */
@media (max-width: 767.98px) {
  .mobile-admin-dashboard {
    padding-top: 60px;
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  /* 管理員標題 */
  .mobile-admin-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1030;
  }
  
  .mobile-admin-header .btn-outline-light {
    border-color: rgba(255, 255, 255, 0.5);
    color: white;
  }
  
  .mobile-admin-header .btn-outline-light:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.7);
  }
  
  /* 側邊欄 */
  .offcanvas .nav-link {
    padding: 1rem 1.5rem;
    color: #495057;
    border-bottom: 1px solid #e9ecef;
    transition: all 0.2s ease;
  }
  
  .offcanvas .nav-link:hover,
  .offcanvas .nav-link.active {
    background: #667eea;
    color: white;
  }
  
  .offcanvas .nav-link i {
    width: 20px;
    text-align: center;
  }
  
  /* 主要內容 */
  .mobile-admin-content {
    padding-top: 1rem;
  }
  
  .mobile-admin-content .card {
    border-radius: 1rem;
  }
  
  .mobile-admin-content .card-title {
    font-size: var(--mobile-font-lg);
  }
  
  /* 統計卡片 */
  .mobile-admin-content .card .fa-2x {
    font-size: 1.5rem;
  }
  
  /* 活動列表 */
  .list-group-item {
    padding: 1rem;
  }
  
  /* 進度條 */
  .progress {
    border-radius: 1rem;
  }
  
  .progress-bar {
    border-radius: 1rem;
  }
}
```

## 📱 移動端交互體驗優化

### 觸控手勢支援
```javascript
// 移動端手勢處理
class MobileGestureHandler {
  constructor() {
    this.initSwipeGestures();
    this.initPullToRefresh();
    this.initInfiniteScroll();
  }
  
  // 滑動手勢
  initSwipeGestures() {
    let startX, startY, endX, endY;
    
    document.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
      startY = e.touches[0].clientY;
    });
    
    document.addEventListener('touchend', (e) => {
      endX = e.changedTouches[0].clientX;
      endY = e.changedTouches[0].clientY;
      
      const deltaX = endX - startX;
      const deltaY = endY - startY;
      
      // 水平滑動
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          this.handleSwipeRight();
        } else {
          this.handleSwipeLeft();
        }
      }
      
      // 垂直滑動
      if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > 50) {
        if (deltaY > 0) {
          this.handleSwipeDown();
        } else {
          this.handleSwipeUp();
        }
      }
    });
  }
  
  // 下拉刷新
  initPullToRefresh() {
    let startY = 0;
    let currentY = 0;
    let isPulling = false;
    
    const refreshContainer = document.querySelector('.mobile-pull-refresh');
    const refreshIndicator = document.querySelector('.refresh-indicator');
    
    document.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        startY = e.touches[0].clientY;
        isPulling = true;
      }
    });
    
    document.addEventListener('touchmove', (e) => {
      if (isPulling) {
        currentY = e.touches[0].clientY;
        const pullDistance = currentY - startY;
        
        if (pullDistance > 0 && pullDistance < 100) {
          refreshContainer.style.transform = `translateY(${pullDistance}px)`;
          refreshIndicator.style.opacity = pullDistance / 100;
        }
      }
    });
    
    document.addEventListener('touchend', () => {
      if (isPulling) {
        const pullDistance = currentY - startY;
        
        if (pullDistance > 60) {
          this.triggerRefresh();
        }
        
        refreshContainer.style.transform = 'translateY(0)';
        refreshIndicator.style.opacity = '0';
        isPulling = false;
      }
    });
  }
  
  // 無限滾動
  initInfiniteScroll() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          this.loadMoreContent();
        }
      });
    }, {
      rootMargin: '100px'
    });
    
    const loadMoreTrigger = document.querySelector('.load-more-trigger');
    if (loadMoreTrigger) {
      observer.observe(loadMoreTrigger);
    }
  }
  
  handleSwipeRight() {
    // 右滑返回上一頁
    if (window.history.length > 1) {
      window.history.back();
    }
  }
  
  handleSwipeLeft() {
    // 左滑打開側邊欄或下一頁
    const sidebar = document.querySelector('.offcanvas');
    if (sidebar) {
      const bsOffcanvas = new bootstrap.Offcanvas(sidebar);
      bsOffcanvas.show();
    }
  }
  
  handleSwipeDown() {
    // 下滑刷新
    if (window.scrollY === 0) {
      this.triggerRefresh();
    }
  }
  
  handleSwipeUp() {
    // 上滑隱藏導航欄
    const navbar = document.querySelector('.mobile-navbar');
    if (navbar) {
      navbar.style.transform = 'translateY(-100%)';
    }
  }
  
  triggerRefresh() {
    // 觸發頁面刷新
    const refreshEvent = new CustomEvent('pullToRefresh');
    document.dispatchEvent(refreshEvent);
  }
  
  loadMoreContent() {
    // 載入更多內容
    const loadMoreEvent = new CustomEvent('loadMore');
    document.dispatchEvent(loadMoreEvent);
  }
}

// 初始化手勢處理
if (window.innerWidth <= 768) {
  new MobileGestureHandler();
}
```

### 移動端性能優化
```javascript
// 移動端性能優化
class MobilePerformanceOptimizer {
  constructor() {
    this.initLazyLoading();
    this.initImageOptimization();
    this.initVirtualScrolling();
    this.initServiceWorker();
  }
  
  // 懶加載
  initLazyLoading() {
    const imageObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
      imageObserver.observe(img);
    });
  }
  
  // 圖片優化
  initImageOptimization() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      // 根據設備像素比選擇合適的圖片
      const devicePixelRatio = window.devicePixelRatio || 1;
      const originalSrc = img.src;
      
      if (devicePixelRatio > 1) {
        img.src = originalSrc.replace('.jpg', '@2x.jpg');
      }
      
      // 圖片載入失敗時的備用方案
      img.onerror = () => {
        img.src = '/placeholder.svg';
      };
    });
  }
  
  // 虛擬滾動
  initVirtualScrolling() {
    const virtualList = document.querySelector('.virtual-scroll-list');
    if (!virtualList) return;
    
    const itemHeight = 80; // 每個項目的高度
    const containerHeight = virtualList.clientHeight;
    const visibleItems = Math.ceil(containerHeight / itemHeight);
    const buffer = 5; // 緩衝區項目數
    
    let scrollTop = 0;
    let startIndex = 0;
    let endIndex = visibleItems + buffer;
    
    virtualList.addEventListener('scroll', () => {
      scrollTop = virtualList.scrollTop;
      startIndex = Math.floor(scrollTop / itemHeight);
      endIndex = Math.min(startIndex + visibleItems + buffer, this.totalItems);
      
      this.renderVisibleItems(startIndex, endIndex);
    });
  }
  
  // Service Worker
  initServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(registration => {
          console.log('SW registered: ', registration);
        })
        .catch(registrationError => {
          console.log('SW registration failed: ', registrationError);
        });
    }
  }
  
  renderVisibleItems(startIndex, endIndex) {
    // 渲染可見項目的邏輯
    const virtualList = document.querySelector('.virtual-scroll-list');
    const items = this.getItemsInRange(startIndex, endIndex);
    
    virtualList.innerHTML = items.map(item => `
      <div class="virtual-item" style="transform: translateY(${item.index * 80}px)">
        ${item.content}
      </div>
    `).join('');
  }
}

// 初始化性能優化
if (window.innerWidth <= 768) {
  new MobilePerformanceOptimizer();
}
```

### 移動端導航系統
```css
/* 移動端導航系統 */
@media (max-width: 767.98px) {
  /* 頂部導航 */
  .mobile-navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1030;
    background: white;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
  }
  
  .mobile-navbar.hidden {
    transform: translateY(-100%);
  }
  
  /* 底部導航 */
  .mobile-bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1030;
    background: white;
    border-top: 1px solid #e9ecef;
    padding: var(--mobile-spacing-sm) 0;
  }
  
  .mobile-bottom-nav .nav-item {
    flex: 1;
    text-align: center;
  }
  
  .mobile-bottom-nav .nav-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--mobile-spacing-xs);
    color: #6c757d;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .mobile-bottom-nav .nav-link.active,
  .mobile-bottom-nav .nav-link:hover {
    color: var(--primary-color);
  }
  
  .mobile-bottom-nav .nav-link i {
    font-size: 1.2rem;
    margin-bottom: 0.25rem;
  }
  
  .mobile-bottom-nav .nav-link span {
    font-size: 0.75rem;
    font-weight: 500;
  }
}
```

## 🚀 PWA 支援

### Service Worker 實現
```javascript
// sw.js - Service Worker
const CACHE_NAME = 'jobspy-v2-cache';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/logo.svg',
  '/manifest.json'
];

// 安裝 Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// 攔截網路請求
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 如果快取中有資源，返回快取版本
        if (response) {
          return response;
        }
        
        // 否則從網路獲取
        return fetch(event.request).then((response) => {
          // 檢查是否為有效回應
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // 複製回應並加入快取
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            });
          
          return response;
        });
      })
  );
});

// 更新 Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
```

### PWA Manifest
```json
{
  "name": "JobSpy v2 - 智能求職平台",
  "short_name": "JobSpy",
  "description": "智能化求職平台，幫助您找到理想工作",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#667eea",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "categories": ["business", "productivity"],
  "lang": "zh-TW",
  "dir": "ltr"
}
```

## 📊 移動端測試策略

### 設備測試矩陣
```javascript
// 移動端測試配置
const mobileTestConfig = {
  devices: [
    {
      name: 'iPhone SE',
      viewport: { width: 375, height: 667 },
      userAgent: 'iPhone'
    },
    {
      name: 'iPhone 12',
      viewport: { width: 390, height: 844 },
      userAgent: 'iPhone'
    },
    {
      name: 'Samsung Galaxy S21',
      viewport: { width: 384, height: 854 },
      userAgent: 'Android'
    },
    {
      name: 'iPad',
      viewport: { width: 768, height: 1024 },
      userAgent: 'iPad'
    }
  ],
  
  testScenarios: [
    'navigation_functionality',
    'search_and_filter',
    'job_application_flow',
    'user_profile_management',
    'responsive_layout',
    'touch_interactions',
    'performance_metrics'
  ]
};

// Playwright 移動端測試
const { test, expect } = require('@playwright/test');

mobileTestConfig.devices.forEach(device => {
  test.describe(`Mobile Tests - ${device.name}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize(device.viewport);
      await page.setUserAgent(device.userAgent);
    });
    
    test('should display mobile navigation correctly', async ({ page }) => {
      await page.goto('/');
      
      // 檢查移動端導航是否正確顯示
      const mobileNav = page.locator('.mobile-navbar');
      await expect(mobileNav).toBeVisible();
      
      // 檢查底部導航
      const bottomNav = page.locator('.mobile-bottom-nav');
      await expect(bottomNav).toBeVisible();
      
      // 檢查導航項目
      const navItems = page.locator('.mobile-bottom-nav .nav-item');
      await expect(navItems).toHaveCount(5);
    });
    
    test('should handle touch interactions', async ({ page }) => {
      await page.goto('/search');
      
      // 測試觸控滑動
      const searchResults = page.locator('.search-results');
      await searchResults.hover();
      
      // 模擬滑動手勢
      await page.touchscreen.tap(200, 300);
      await page.touchscreen.tap(200, 200);
      
      // 檢查滑動效果
      await expect(page.locator('.job-card').first()).toBeVisible();
    });
    
    test('should maintain performance on mobile', async ({ page }) => {
      await page.goto('/');
      
      // 測試頁面載入時間
      const startTime = Date.now();
      await page.waitForLoadState('networkidle');
      const loadTime = Date.now() - startTime;
      
      expect(loadTime).toBeLessThan(3000); // 3秒內載入完成
      
      // 檢查 Core Web Vitals
      const metrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            resolve(entries);
          }).observe({ entryTypes: ['navigation', 'paint'] });
        });
      });
      
      expect(metrics).toBeDefined();
    });
  });
});
```

## 🎯 成功指標與監控

### 移動端 KPI
```javascript
// 移動端性能監控
class MobileAnalytics {
  constructor() {
    this.initPerformanceMonitoring();
    this.initUserBehaviorTracking();
    this.initErrorTracking();
  }
  
  // 性能監控
  initPerformanceMonitoring() {
    // Core Web Vitals
    new PerformanceObserver((list) => {
      list.getEntries().forEach((entry) => {
        if (entry.entryType === 'largest-contentful-paint') {
          this.trackMetric('LCP', entry.startTime);
        }
        if (entry.entryType === 'first-input') {
          this.trackMetric('FID', entry.processingStart - entry.startTime);
        }
        if (entry.entryType === 'layout-shift') {
          this.trackMetric('CLS', entry.value);
        }
      });
    }).observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
    
    // 頁面載入時間
    window.addEventListener('load', () => {
      const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
      this.trackMetric('PageLoadTime', loadTime);
    });
  }
  
  // 用戶行為追蹤
  initUserBehaviorTracking() {
    // 觸控事件
    document.addEventListener('touchstart', (e) => {
      this.trackEvent('touch_interaction', {
        element: e.target.tagName,
        timestamp: Date.now()
      });
    });
    
    // 滾動行為
    let scrollTimeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => {
        this.trackEvent('scroll_depth', {
          depth: Math.round((window.scrollY / document.body.scrollHeight) * 100)
        });
      }, 100);
    });
    
    // 頁面可見性
    document.addEventListener('visibilitychange', () => {
      this.trackEvent('page_visibility', {
        hidden: document.hidden
      });
    });
  }
  
  // 錯誤追蹤
  initErrorTracking() {
    window.addEventListener('error', (e) => {
      this.trackError('javascript_error', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno
      });
    });
    
    window.addEventListener('unhandledrejection', (e) => {
      this.trackError('promise_rejection', {
        reason: e.reason
      });
    });
  }
  
  trackMetric(name, value) {
    // 發送性能指標到分析服務
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/analytics/metrics', JSON.stringify({
        metric: name,
        value: value,
        timestamp: Date.now(),
        userAgent: navigator.userAgent,
        viewport: {
          width: window.innerWidth,
          height: window.innerHeight
        }
      }));
    }
  }
  
  trackEvent(event, data) {
    // 發送事件到分析服務
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/analytics/events', JSON.stringify({
        event: event,
        data: data,
        timestamp: Date.now()
      }));
    }
  }
  
  trackError(type, error) {
    // 發送錯誤到監控服務
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/analytics/errors', JSON.stringify({
        type: type,
        error: error,
        timestamp: Date.now(),
        url: window.location.href
      }));
    }
  }
}

// 初始化移動端分析
if (window.innerWidth <= 768) {
  new MobileAnalytics();
}
```

## 📈 持續優化計劃

### 階段性改進
1. **第一階段（1-2週）**
   - 基礎響應式佈局實現
   - 核心功能移動端適配
   - 基本觸控交互

2. **第二階段（3-4週）**
   - 高級手勢支援
   - 性能優化
   - PWA 功能實現

3. **第三階段（5-6週）**
   - 用戶體驗優化
   - 無障碍功能完善
   - 深度分析與監控

### 未來功能擴展
- **語音搜索**：整合語音識別 API
- **AR 功能**：公司位置 AR 導航
- **離線模式**：關鍵功能離線可用
- **推送通知**：智能職位推薦通知
- **生物識別**：指紋/面部識別登入

---

**移動端響應式設計完成！** 🎉

這個設計方案提供了完整的移動端用戶體驗，包括響應式佈局、觸控優化、性能優化和 PWA 支援，確保 JobSpy v2 在所有移動設備上都能提供優秀的用戶體驗。
/* 移動端頂部導航 */
.mobile-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1030;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: var(--mobile-shadow);
  height: 60px;
}

.mobile-navbar .navbar-brand {
  font-size: var(--mobile-font-lg);
  font-weight: 600;
}

.mobile-navbar .navbar-toggler {
  border: none;
  padding: 0.5rem;
  font-size: var(--mobile-font-lg);
}

/* 移動端側邊欄 */
.mobile-sidebar {
  position: fixed;
  top: 60px;
  left: -100%;
  width: 280px;
  height: calc(100vh - 60px);
  background: #ffffff;
  border-right: 1px solid #e9ecef;
  transition: left 0.3s ease;
  z-index: 1025;
  overflow-y: auto;
}

.mobile-sidebar.show {
  left: 0;
}

.mobile-sidebar-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1020;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.mobile-sidebar-overlay.show {
  opacity: 1;
  visibility: visible;
}

/* 移動端底部導航 */
.mobile-bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #ffffff;
  border-top: 1px solid #e9ecef;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1030;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0.5rem;
}

.mobile-bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #6c757d;
  font-size: var(--mobile-font-xs);
  min-width: var(--touch-target-min);
  min-height: var(--touch-target-min);
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.mobile-bottom-nav-item:hover,
.mobile-bottom-nav-item.active {
  color: #0d6efd;
  background: rgba(13, 110, 253, 0.1);
  text-decoration: none;
}

.mobile-bottom-nav-item i {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
}

.mobile-bottom-nav-item .badge {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  font-size: 0.625rem;
  min-width: 1rem;
  height: 1rem;
  border-radius: 0.5rem;
}
```

## 📱 首頁移動端設計

### 移動端首頁佈局
```html
<!-- 移動端首頁結構 -->
<div class="mobile-homepage">
  <!-- 移動端導航 -->
  <nav class="mobile-navbar">
    <div class="container-fluid">
      <div class="d-flex align-items-center justify-content-between">
        <a class="navbar-brand" href="/">
          <img src="/logo-mobile.svg" alt="JobSpy" height="32">
        </a>
        <div class="d-flex align-items-center gap-2">
          <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#searchModal">
            <i class="fas fa-search"></i>
          </button>
          <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#mobileMenu">
            <i class="fas fa-bars"></i>
          </button>
        </div>
      </div>
    </div>
  </nav>

  <!-- 主要內容 -->
  <main class="mobile-main" style="margin-top: 60px; margin-bottom: 70px;">
    <!-- 搜尋區域 -->
    <section class="mobile-search-hero">
      <div class="container-fluid py-4">
        <div class="text-center mb-4">
          <h1 class="h3 fw-bold text-primary mb-2">找到理想工作</h1>
          <p class="text-muted mb-0">超過 10,000+ 職位等你探索</p>
        </div>
        
        <!-- 快速搜尋 -->
        <div class="mobile-quick-search">
          <div class="input-group mb-3">
            <input type="text" class="form-control" placeholder="搜尋職位、公司或技能">
            <button class="btn btn-primary" type="button">
              <i class="fas fa-search"></i>
            </button>
          </div>
          
          <!-- 熱門搜尋標籤 -->
          <div class="mobile-popular-tags">
            <small class="text-muted d-block mb-2">熱門搜尋：</small>
            <div class="d-flex flex-wrap gap-2">
              <span class="badge bg-light text-dark">前端工程師</span>
              <span class="badge bg-light text-dark">後端工程師</span>
              <span class="badge bg-light text-dark">UI/UX 設計師</span>
              <span class="badge bg-light text-dark">產品經理</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 職位分類 -->
    <section class="mobile-job-categories">
      <div class="container-fluid py-4">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h2 class="h5 fw-bold mb-0">熱門職位分類</h2>
          <a href="/categories" class="btn btn-outline-primary btn-sm">查看全部</a>
        </div>
        
        <div class="row g-3">
          <div class="col-6">
            <div class="card h-100 border-0 bg-light">
              <div class="card-body text-center p-3">
                <div class="mb-2">
                  <i class="fas fa-code text-primary" style="font-size: 2rem;"></i>
                </div>
                <h6 class="card-title mb-1">軟體開發</h6>
                <small class="text-muted">1,234 個職位</small>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="card h-100 border-0 bg-light">
              <div class="card-body text-center p-3">
                <div class="mb-2">
                  <i class="fas fa-palette text-success" style="font-size: 2rem;"></i>
                </div>
                <h6 class="card-title mb-1">設計創意</h6>
                <small class="text-muted">567 個職位</small>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="card h-100 border-0 bg-light">
              <div class="card-body text-center p-3">
                <div class="mb-2">
                  <i class="fas fa-chart-line text-warning" style="font-size: 2rem;"></i>
                </div>
                <h6 class="card-title mb-1">行銷企劃</h6>
                <small class="text-muted">890 個職位</small>
              </div>
            </div>
          </div>
          <div class="col-6">
            <div class="card h-100 border-0 bg-light">
              <div class="card-body text-center p-3">
                <div class="mb-2">
                  <i class="fas fa-users text-info" style="font-size: 2rem;"></i>
                </div>
                <h6 class="card-title mb-1">人力資源</h6>
                <small class="text-muted">345 個職位</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 推薦職位 -->
    <section class="mobile-featured-jobs">
      <div class="container-fluid py-4">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h2 class="h5 fw-bold mb-0">推薦職位</h2>
          <a href="/jobs" class="btn btn-outline-primary btn-sm">查看更多</a>
        </div>
        
        <!-- 職位卡片 -->
        <div class="mobile-job-cards">
          <div class="card mb-3 border-0 shadow-sm">
            <div class="card-body p-3">
              <div class="d-flex align-items-start gap-3">
                <img src="/company-logo.jpg" alt="Company" class="rounded" width="48" height="48">
                <div class="flex-grow-1 min-w-0">
                  <h6 class="card-title mb-1 text-truncate">前端工程師</h6>
                  <p class="text-muted mb-1 small">科技公司 • 台北市</p>
                  <div class="d-flex align-items-center gap-2 mb-2">
                    <span class="badge bg-primary-subtle text-primary">React</span>
                    <span class="badge bg-primary-subtle text-primary">TypeScript</span>
                  </div>
                  <div class="d-flex align-items-center justify-content-between">
                    <span class="text-success fw-medium">NT$ 60K - 80K</span>
                    <small class="text-muted">2 天前</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 更多職位卡片... -->
        </div>
      </div>
    </section>

    <!-- 公司推薦 -->
    <section class="mobile-featured-companies">
      <div class="container-fluid py-4">
        <div class="d-flex align-items-center justify-content-between mb-3">
          <h2 class="h5 fw-bold mb-0">熱門公司</h2>
          <a href="/companies" class="btn btn-outline-primary btn-sm">查看更多</a>
        </div>
        
        <div class="row g-3">
          <div class="col-6">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-3">
                <img src="/company1.jpg" alt="Company" class="rounded mb-2" width="48" height="48">
                <h6 class="card-title mb-1">科技公司</h6>
                <small class="text-muted">25 個職位</small>
              </div>
            </div>
          </div>
          <!-- 更多公司卡片... -->
        </div>
      </div>
    </section>
  </main>

  <!-- 移動端底部導航 -->
  <nav class="mobile-bottom-nav">
    <a href="/" class="mobile-bottom-nav-item active">
      <i class="fas fa-home"></i>
      <span>首頁</span>
    </a>
    <a href="/search" class="mobile-bottom-nav-item">
      <i class="fas fa-search"></i>
      <span>搜尋</span>
    </a>
    <a href="/saved" class="mobile-bottom-nav-item">
      <i class="fas fa-bookmark"></i>
      <span>收藏</span>
      <span class="badge bg-danger">3</span>
    </a>
    <a href="/applications" class="mobile-bottom-nav-item">
      <i class="fas fa-file-alt"></i>
      <span>申請</span>
    </a>
    <a href="/profile" class="mobile-bottom-nav-item">
      <i class="fas fa-user"></i>
      <span>我的</span>
    </a>
  </nav>
</div>
```

### 移動端首頁樣式
```css
/* 移動端首頁專用樣式 */
@media (max-width: 767.98px) {
  .mobile-homepage {
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  /* 搜尋英雄區域 */
  .mobile-search-hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  
  .mobile-search-hero .form-control {
    border: none;
    box-shadow: var(--mobile-shadow);
  }
  
  .mobile-search-hero .btn-primary {
    background: #ffffff;
    color: #667eea;
    border: none;
  }
  
  .mobile-popular-tags .badge {
    font-size: var(--mobile-font-xs);
    padding: 0.375rem 0.75rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .mobile-popular-tags .badge:hover {
    background: #e9ecef !important;
    transform: translateY(-1px);
  }
  
  /* 職位分類卡片 */
  .mobile-job-categories .card {
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .mobile-job-categories .card:hover {
    transform: translateY(-2px);
    box-shadow: var(--mobile-shadow-lg);
  }
  
  /* 職位卡片 */
  .mobile-job-cards .card {
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .mobile-job-cards .card:hover {
    transform: translateY(-1px);
    box-shadow: var(--mobile-shadow-lg);
  }
  
  .mobile-job-cards .badge {
    font-size: 0.625rem;
    padding: 0.25rem 0.5rem;
  }
  
  /* 公司卡片 */
  .mobile-featured-companies .card {
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .mobile-featured-companies .card:hover {
    transform: translateY(-2px);
    box-shadow: var(--mobile-shadow-lg);
  }
}
```

## 🔍 搜尋結果頁移動端設計

### 移動端搜尋結果佈局
```html
<!-- 移動端搜尋結果 -->
<div class="mobile-search-results">
  <!-- 移動端搜尋欄 -->
  <div class="mobile-search-bar">
    <div class="container-fluid py-3">
      <div class="input-group">
        <input type="text" class="form-control" placeholder="搜尋職位..." value="前端工程師">
        <button class="btn btn-primary" type="button">
          <i class="fas fa-search"></i>
        </button>
      </div>
    </div>
  </div>

  <!-- 移動端篩選器 -->
  <div class="mobile-filters">
    <div class="container-fluid py-2">
      <div class="d-flex align-items-center gap-2 overflow-auto">
        <button class="btn btn-outline-primary btn-sm flex-shrink-0" data-bs-toggle="modal" data-bs-target="#filtersModal">
          <i class="fas fa-filter me-1"></i>篩選
        </button>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0">
          <i class="fas fa-map-marker-alt me-1"></i>台北市
        </button>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0">
          <i class="fas fa-dollar-sign me-1"></i>50K-80K
        </button>
        <button class="btn btn-outline-secondary btn-sm flex-shrink-0">
          <i class="fas fa-clock me-1"></i>全職
        </button>
      </div>
    </div>
  </div>

  <!-- 結果統計 -->
  <div class="mobile-results-info">
    <div class="container-fluid py-2">
      <div class="d-flex align-items-center justify-content-between">
        <span class="text-muted small">找到 1,234 個職位</span>
        <div class="dropdown">
          <button class="btn btn-outline-secondary btn-sm dropdown-toggle" data-bs-toggle="dropdown">
            <i class="fas fa-sort me-1"></i>相關性
          </button>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item" href="#">相關性</a></li>
            <li><a class="dropdown-item" href="#">發布時間</a></li>
            <li><a class="dropdown-item" href="#">薪資高低</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <!-- 職位列表 -->
  <div class="mobile-job-list">
    <div class="container-fluid">
      <!-- 職位卡片 -->
      <div class="mobile-job-card">
        <div class="card mb-3 border-0 shadow-sm">
          <div class="card-body p-3">
            <div class="d-flex align-items-start gap-3">
              <img src="/company-logo.jpg" alt="Company" class="rounded flex-shrink-0" width="48" height="48">
              <div class="flex-grow-1 min-w-0">
                <div class="d-flex align-items-start justify-content-between mb-2">
                  <div class="flex-grow-1 min-w-0">
                    <h6 class="card-title mb-1 text-truncate">前端工程師 (React)</h6>
                    <p class="text-muted mb-0 small">科技創新公司</p>
                  </div>
                  <button class="btn btn-outline-warning btn-sm ms-2 flex-shrink-0">
                    <i class="fas fa-bookmark"></i>
                  </button>
                </div>
                
                <div class="mb-2">
                  <div class="d-flex align-items-center gap-1 mb-1">
                    <i class="fas fa-map-marker-alt text-muted small"></i>
                    <span class="text-muted small">台北市信義區</span>
                  </div>
                  <div class="d-flex align-items-center gap-1">
                    <i class="fas fa-dollar-sign text-success small"></i>
                    <span class="text-success fw-medium small">NT$ 60,000 - 80,000</span>
                  </div>
                </div>
                
                <div class="d-flex flex-wrap gap-1 mb-2">
                  <span class="badge bg-primary-subtle text-primary">React</span>
                  <span class="badge bg-primary-subtle text-primary">TypeScript</span>
                  <span class="badge bg-primary-subtle text-primary">Node.js</span>
                </div>
                
                <div class="d-flex align-items-center justify-content-between">
                  <div class="d-flex align-items-center gap-3">
                    <small class="text-muted">
                      <i class="fas fa-eye me-1"></i>128 次瀏覽
                    </small>
                    <small class="text-muted">
                      <i class="fas fa-clock me-1"></i>2 天前
                    </small>
                  </div>
                  <button class="btn btn-primary btn-sm">
                    申請
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 更多職位卡片... -->
    </div>
  </div>

  <!-- 載入更多 -->
  <div class="mobile-load-more">
    <div class="container-fluid py-3">
      <div class="text-center">
        <button class="btn btn-outline-primary">
          <i class="fas fa-spinner fa-spin me-2 d-none"></i>
          載入更多職位
        </button>
      </div>
    </div>
  </div>
</div>

<!-- 移動端篩選器模態框 -->
<div class="modal fade" id="filtersModal" tabindex="-1">
  <div class="modal-dialog modal-fullscreen-sm-down">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">篩選條件</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <!-- 地點篩選 -->
        <div class="mb-4">
          <h6 class="fw-bold mb-3">工作地點</h6>
          <div class="form-check mb-2">
            <input class="form-check-input" type="checkbox" id="location-taipei">
            <label class="form-check-label" for="location-taipei">
              台北市 <span class="text-muted">(456)</span>
            </label>
          </div>
          <div class="form-check mb-2">
            <input class="form-check-input" type="checkbox" id="location-taichung">
            <label class="form-check-label" for="location-taichung">
              台中市 <span class="text-muted">(123)</span>
            </label>
          </div>
          <!-- 更多地點選項... -->
        </div>
        
        <!-- 薪資範圍 -->
        <div class="mb-4">
          <h6 class="fw-bold mb-3">薪資範圍</h6>
          <div class="range-slider">
            <input type="range" class="form-range" min="20000" max="150000" step="5000" value="60000">
            <div class="d-flex justify-content-between mt-2">
              <span class="small text-muted">20K</span>
              <span class="small fw-medium">60K - 80K</span>
              <span class="small text-muted">150K+</span>
            </div>
          </div>
        </div>
        
        <!-- 工作類型 -->
        <div class="mb-4">
          <h6 class="fw-bold mb-3">工作類型</h6>
          <div class="form-check mb-2">
            <input class="form-check-input" type="checkbox" id="type-fulltime" checked>
            <label class="form-check-label" for="type-fulltime">
              全職 <span class="text-muted">(890)</span>
            </label>
          </div>
          <div class="form-check mb-2">
            <input class="form-check-input" type="checkbox" id="type-parttime">
            <label class="form-check-label" for="type-parttime">
              兼職 <span class="text-muted">(234)</span>
            </label>
          </div>
          <!-- 更多類型選項... -->
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">取消</button>
        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">套用篩選</button>
      </div>
    </div>
  </div>
</div>
```

### 移動端搜尋結果樣式
```css
/* 移動端搜尋結果樣式 */
@media (max-width: 767.98px) {
  .mobile-search-results {
    padding-top: 60px;
    padding-bottom: 70px;
    min-height: 100vh;
    background: #f8f9fa;
  }
  
  /* 搜尋欄 */
  .mobile-search-bar {
    background: #ffffff;
    border-bottom: 1px solid #e9ecef;
    position: sticky;
    top: 60px;
    z-index: 1020;
  }
  
  /* 篩選器 */
  .mobile-filters {
    background: #ffffff;
    border-bottom: 1px solid #e9ecef;
    position: sticky;
    top: calc(60px + 70px);
    z-index: 1019;
  }
  
  .mobile-filters .btn {
    white-space: nowrap;
    font-size: var(--mobile-font-sm);
  }
  
  /* 結果資訊 */
  .mobile-results-info {
    background: #ffffff;
    border-bottom: 1px solid #e9ecef;
  }
  
  /* 職位卡片 */
  .mobile-job-card .card {
    transition: all 0.2s ease;
    cursor: pointer;
  }
  
  .mobile-job-card .card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .mobile-job-card .badge {
    font-size: 0.625rem;
    padding: 0.25rem 0.5rem;
  }
  
  .mobile-job-card .btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: var(--mobile-font-sm);
  }
  
  /* 載入更多 */
  .mobile-load-more {
    background: #ffffff;
  }
  
  /* 篩選器模態框 */
  .modal-fullscreen-sm-down .modal-content {
    border-radius: 0;
  }
  
  .modal-fullscreen-sm-down .modal-body {
    padding: 1.5rem;
  }
  
  .form-check-label {
    font-size: var(--mobile-font-base);
    cursor: pointer;
  }
  
  .range-slider {
    padding: 0 0.5rem;
  }
  
  .form-range {
    height: 0.5rem;
  }
}
```