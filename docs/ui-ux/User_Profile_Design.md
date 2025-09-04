# 用戶個人資料頁面設計規格

## 📋 設計概述

### 設計目標
- **個人化體驗** - 提供完整的個人資料管理功能
- **求職優化** - 智能求職偏好設定和推薦
- **履歷管理** - 線上履歷編輯和管理系統
- **隱私控制** - 細粒度的隱私設定選項
- **數據洞察** - 個人求職數據分析和建議

### 技術要求
- **框架**: React 18 + TypeScript + Bootstrap 5
- **表單處理**: React Hook Form + Zod
- **狀態管理**: Zustand
- **API 整合**: TanStack Query
- **國際化**: i18next
- **圖標**: Lucide React
- **文件上傳**: React Dropzone

## 🎨 整體佈局設計

### 個人資料頁面架構

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              頂部導航欄                                         │
│  [Logo] JobSpy    [搜尋]    [通知🔔]  [用戶頭像▼]  [設定⚙️]  [登出]           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│ ┌─────────────────┐ ┌─────────────────────────────────────────────────────────┐ │
│ │                 │ │                                                         │ │
│ │   左側導航欄     │ │                   主內容區域                            │ │
│ │                 │ │                                                         │ │
│ │ 👤 基本資料      │ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ 💼 職業資訊      │ │ │                                                     │ │ │
│ │ 🎯 求職偏好      │ │ │                 動態內容區                          │ │ │
│ │ 📄 履歷管理      │ │ │                                                     │ │ │
│ │ 🔔 通知設定      │ │ │                                                     │ │ │
│ │ 🔒 隱私設定      │ │ │                                                     │ │ │
│ │ 📊 我的數據      │ │ │                                                     │ │ │
│ │ ⚙️ 帳號設定      │ │ │                                                     │ │ │
│ │                 │ │ │                                                     │ │ │
│ │ ───────────────  │ │ └─────────────────────────────────────────────────────┘ │ │
│ │ 🏠 返回首頁      │ │                                                         │ │
│ │ 📚 使用說明      │ │                                                         │ │
│ │ 🆘 客服支援      │ │                                                         │ │
│ └─────────────────┘ └─────────────────────────────────────────────────────────┘ │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                              頁腳                                               │
│  © 2024 JobSpy  |  隱私政策  |  服務條款  |  聯絡我們  |  幫助中心               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 色彩方案

```css
/* 個人資料頁面專用色彩 */
:root {
  --profile-primary: #3b82f6;
  --profile-primary-hover: #2563eb;
  --profile-secondary: #64748b;
  --profile-success: #10b981;
  --profile-warning: #f59e0b;
  --profile-danger: #ef4444;
  --profile-info: #06b6d4;
  
  --profile-bg-primary: #f8fafc;
  --profile-bg-secondary: #ffffff;
  --profile-bg-card: #ffffff;
  
  --profile-sidebar-bg: #f1f5f9;
  --profile-sidebar-active: #e0f2fe;
  --profile-sidebar-text: #475569;
  
  --profile-border: #e2e8f0;
  --profile-text-primary: #1e293b;
  --profile-text-secondary: #64748b;
  --profile-text-muted: #94a3b8;
}
```

## 👤 基本資料設計

### 個人資訊編輯

```html
<div className="profile-basic-info">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">基本資料</h2>
      <p className="text-muted mb-0">管理您的個人基本資訊</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-eye me-2"></i>
        預覽履歷
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存變更
      </button>
    </div>
  </div>
  
  <!-- 頭像和基本資訊 -->
  <div className="row g-4 mb-4">
    <div className="col-md-4">
      <div className="card border-0 shadow-sm">
        <div className="card-body text-center">
          <div className="position-relative d-inline-block mb-3">
            <img src="https://via.placeholder.com/120" className="rounded-circle" alt="用戶頭像" width="120" height="120">
            <button className="btn btn-primary btn-sm position-absolute bottom-0 end-0 rounded-circle" style="width: 32px; height: 32px;">
              <i className="lucide-camera"></i>
            </button>
          </div>
          <h5 className="mb-1">張小明</h5>
          <p className="text-muted mb-3">前端工程師</p>
          <div className="d-flex justify-content-center gap-2 mb-3">
            <span className="badge bg-success">已驗證</span>
            <span className="badge bg-primary">付費會員</span>
          </div>
          <div className="progress mb-2" style="height: 8px;">
            <div className="progress-bar bg-success" style="width: 85%"></div>
          </div>
          <small className="text-muted">個人資料完整度: 85%</small>
        </div>
      </div>
    </div>
    
    <div className="col-md-8">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">個人資訊</h5>
        </div>
        <div className="card-body">
          <form>
            <div className="row g-3">
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="text" className="form-control" id="firstName" value="小明" required>
                  <label for="firstName">名字 *</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="text" className="form-control" id="lastName" value="張" required>
                  <label for="lastName">姓氏 *</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="email" className="form-control" id="email" value="zhang@example.com" required>
                  <label for="email">電子郵件 *</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="tel" className="form-control" id="phone" value="+886 912-345-678">
                  <label for="phone">電話號碼</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <input type="date" className="form-control" id="birthDate" value="1990-05-15">
                  <label for="birthDate">出生日期</label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-floating">
                  <select className="form-select" id="gender">
                    <option value="">請選擇</option>
                    <option value="male" selected>男性</option>
                    <option value="female">女性</option>
                    <option value="other">其他</option>
                    <option value="prefer-not-to-say">不願透露</option>
                  </select>
                  <label for="gender">性別</label>
                </div>
              </div>
              <div className="col-12">
                <div className="form-floating">
                  <textarea className="form-control" id="bio" style="height: 100px;" placeholder="簡短介紹自己...">熱愛前端開發，專精於 React 和 TypeScript，具備 5 年以上開發經驗。</textarea>
                  <label for="bio">個人簡介</label>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 聯絡資訊 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">聯絡資訊</h5>
    </div>
    <div className="card-body">
      <form>
        <div className="row g-3">
          <div className="col-md-6">
            <div className="form-floating">
              <select className="form-select" id="country" required>
                <option value="">請選擇國家</option>
                <option value="TW" selected>台灣</option>
                <option value="CN">中國</option>
                <option value="HK">香港</option>
                <option value="SG">新加坡</option>
              </select>
              <label for="country">國家/地區 *</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <select className="form-select" id="city" required>
                <option value="">請選擇城市</option>
                <option value="taipei" selected>台北市</option>
                <option value="new-taipei">新北市</option>
                <option value="taoyuan">桃園市</option>
                <option value="taichung">台中市</option>
                <option value="tainan">台南市</option>
                <option value="kaohsiung">高雄市</option>
              </select>
              <label for="city">城市 *</label>
            </div>
          </div>
          <div className="col-12">
            <div className="form-floating">
              <input type="text" className="form-control" id="address" value="信義區信義路五段7號">
              <label for="address">詳細地址</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="url" className="form-control" id="website" placeholder="https://">
              <label for="website">個人網站</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="url" className="form-control" id="linkedin" placeholder="https://linkedin.com/in/">
              <label for="linkedin">LinkedIn</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="url" className="form-control" id="github" placeholder="https://github.com/">
              <label for="github">GitHub</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="url" className="form-control" id="portfolio" placeholder="https://">
              <label for="portfolio">作品集</label>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</div>
```

## 💼 職業資訊設計

### 工作經歷管理

```html
<div className="profile-career-info">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">職業資訊</h2>
      <p className="text-muted mb-0">管理您的工作經歷和技能</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-primary">
        <i className="lucide-plus me-2"></i>
        新增經歷
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存變更
      </button>
    </div>
  </div>
  
  <!-- 當前職位 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">當前職位</h5>
    </div>
    <div className="card-body">
      <form>
        <div className="row g-3">
          <div className="col-md-6">
            <div className="form-floating">
              <input type="text" className="form-control" id="currentTitle" value="前端工程師">
              <label for="currentTitle">職位名稱</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="text" className="form-control" id="currentCompany" value="科技公司 A">
              <label for="currentCompany">公司名稱</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <select className="form-select" id="employmentType">
                <option value="full-time" selected>全職</option>
                <option value="part-time">兼職</option>
                <option value="contract">合約</option>
                <option value="freelance">自由工作者</option>
                <option value="internship">實習</option>
              </select>
              <label for="employmentType">工作類型</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <select className="form-select" id="workLocation">
                <option value="office" selected>辦公室</option>
                <option value="remote">遠端工作</option>
                <option value="hybrid">混合模式</option>
              </select>
              <label for="workLocation">工作地點</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-floating">
              <input type="month" className="form-control" id="startDate" value="2022-03">
              <label for="startDate">開始日期</label>
            </div>
          </div>
          <div className="col-md-6">
            <div className="form-check form-switch mt-3">
              <input className="form-check-input" type="checkbox" id="currentJob" checked>
              <label className="form-check-label" for="currentJob">
                目前仍在此職位
              </label>
            </div>
          </div>
          <div className="col-12">
            <div className="form-floating">
              <textarea className="form-control" id="jobDescription" style="height: 120px;">負責前端架構設計與開發，使用 React、TypeScript 等技術棧，參與產品需求分析和技術方案制定。</textarea>
              <label for="jobDescription">工作描述</label>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
  
  <!-- 工作經歷列表 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <div className="d-flex justify-content-between align-items-center">
        <h5 className="card-title mb-0">工作經歷</h5>
        <button className="btn btn-outline-primary btn-sm">
          <i className="lucide-plus me-2"></i>
          新增經歷
        </button>
      </div>
    </div>
    <div className="card-body">
      <!-- 經歷項目 1 -->
      <div className="experience-item border rounded p-3 mb-3">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div className="flex-grow-1">
            <h6 className="mb-1">前端工程師</h6>
            <p className="text-muted mb-1">科技公司 B • 全職</p>
            <small className="text-muted">2020年1月 - 2022年2月 • 2年2個月</small>
          </div>
          <div className="dropdown">
            <button className="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
              操作
            </button>
            <ul className="dropdown-menu">
              <li><a className="dropdown-item" href="#"><i className="lucide-edit me-2"></i>編輯</a></li>
              <li><a className="dropdown-item text-danger" href="#"><i className="lucide-trash-2 me-2"></i>刪除</a></li>
            </ul>
          </div>
        </div>
        <p className="mb-2">參與多個大型專案開發，負責前端架構設計和性能優化，團隊協作開發經驗豐富。</p>
        <div className="d-flex flex-wrap gap-1">
          <span className="badge bg-light text-dark">React</span>
          <span className="badge bg-light text-dark">JavaScript</span>
          <span className="badge bg-light text-dark">CSS</span>
          <span className="badge bg-light text-dark">Git</span>
        </div>
      </div>
      
      <!-- 經歷項目 2 -->
      <div className="experience-item border rounded p-3">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div className="flex-grow-1">
            <h6 className="mb-1">初級前端工程師</h6>
            <p className="text-muted mb-1">新創公司 C • 全職</p>
            <small className="text-muted">2018年6月 - 2019年12月 • 1年7個月</small>
          </div>
          <div className="dropdown">
            <button className="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
              操作
            </button>
            <ul className="dropdown-menu">
              <li><a className="dropdown-item" href="#"><i className="lucide-edit me-2"></i>編輯</a></li>
              <li><a className="dropdown-item text-danger" href="#"><i className="lucide-trash-2 me-2"></i>刪除</a></li>
            </ul>
          </div>
        </div>
        <p className="mb-2">負責公司官網和內部系統的前端開發，學習並應用現代前端技術棧。</p>
        <div className="d-flex flex-wrap gap-1">
          <span className="badge bg-light text-dark">HTML</span>
          <span className="badge bg-light text-dark">CSS</span>
          <span className="badge bg-light text-dark">JavaScript</span>
          <span className="badge bg-light text-dark">jQuery</span>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 技能管理 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <div className="d-flex justify-content-between align-items-center">
        <h5 className="card-title mb-0">專業技能</h5>
        <button className="btn btn-outline-primary btn-sm">
          <i className="lucide-plus me-2"></i>
          新增技能
        </button>
      </div>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <!-- 程式語言 -->
        <div className="col-md-6">
          <h6 className="mb-3">程式語言</h6>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>JavaScript</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-success" style="width: 90%"></div>
              </div>
              <small className="text-muted">專精</small>
            </div>
          </div>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>TypeScript</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-success" style="width: 85%"></div>
              </div>
              <small className="text-muted">專精</small>
            </div>
          </div>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>Python</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-warning" style="width: 60%"></div>
              </div>
              <small className="text-muted">中等</small>
            </div>
          </div>
        </div>
        
        <!-- 框架和工具 -->
        <div className="col-md-6">
          <h6 className="mb-3">框架和工具</h6>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>React</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-success" style="width: 95%"></div>
              </div>
              <small className="text-muted">專精</small>
            </div>
          </div>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>Vue.js</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-warning" style="width: 70%"></div>
              </div>
              <small className="text-muted">中等</small>
            </div>
          </div>
          <div className="skill-item d-flex justify-content-between align-items-center mb-2">
            <span>Node.js</span>
            <div className="d-flex align-items-center">
              <div className="progress me-2" style="width: 100px; height: 8px;">
                <div className="progress-bar bg-info" style="width: 75%"></div>
              </div>
              <small className="text-muted">良好</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 教育背景 -->
  <div className="card border-0 shadow-sm">
    <div className="card-header bg-transparent border-0">
      <div className="d-flex justify-content-between align-items-center">
        <h5 className="card-title mb-0">教育背景</h5>
        <button className="btn btn-outline-primary btn-sm">
          <i className="lucide-plus me-2"></i>
          新增學歷
        </button>
      </div>
    </div>
    <div className="card-body">
      <div className="education-item border rounded p-3">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div className="flex-grow-1">
            <h6 className="mb-1">資訊工程學系</h6>
            <p className="text-muted mb-1">國立台灣大學 • 學士學位</p>
            <small className="text-muted">2014年9月 - 2018年6月</small>
          </div>
          <div className="dropdown">
            <button className="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown">
              操作
            </button>
            <ul className="dropdown-menu">
              <li><a className="dropdown-item" href="#"><i className="lucide-edit me-2"></i>編輯</a></li>
              <li><a className="dropdown-item text-danger" href="#"><i className="lucide-trash-2 me-2"></i>刪除</a></li>
            </ul>
          </div>
        </div>
        <p className="mb-2">主修資訊工程，專精於軟體開發和演算法設計，畢業專題為「基於機器學習的推薦系統」。</p>
        <div className="d-flex align-items-center">
          <span className="badge bg-light text-dark me-2">GPA: 3.8/4.0</span>
          <span className="badge bg-light text-dark">書卷獎</span>
        </div>
       </div>
     </div>
   </div>
 </div>
 ```

## 📱 響應式設計

### 移動端適配

```css
/* 移動端樣式 */
@media (max-width: 768px) {
  .profile-container {
    padding: 0.5rem;
  }
  
  .profile-sidebar {
    position: fixed;
    top: 0;
    left: -100%;
    width: 280px;
    height: 100vh;
    background: white;
    z-index: 1050;
    transition: left 0.3s ease;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
  }
  
  .profile-sidebar.show {
    left: 0;
  }
  
  .profile-main {
    margin-left: 0;
    width: 100%;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .profile-stats {
    flex-direction: column;
  }
  
  .stat-item {
    margin-bottom: 1rem;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .btn-group {
    flex-direction: column;
  }
  
  .btn-group .btn {
    margin-bottom: 0.5rem;
  }
}

/* 平板端樣式 */
@media (min-width: 769px) and (max-width: 1024px) {
  .profile-sidebar {
    width: 250px;
  }
  
  .profile-main {
    margin-left: 250px;
  }
  
  .form-row {
    flex-wrap: wrap;
  }
  
  .form-group {
    flex: 1 1 45%;
    margin-right: 1rem;
  }
}
```

## ⚙️ 技術實現

### 核心組件結構

```typescript
// UserProfile.tsx
import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useTranslation } from 'react-i18next';
import { useUserStore } from '../stores/userStore';
import { useMutation, useQuery } from '@tanstack/react-query';

// 表單驗證 Schema
const profileSchema = z.object({
  firstName: z.string().min(1, '請輸入姓名'),
  lastName: z.string().min(1, '請輸入姓氏'),
  email: z.string().email('請輸入有效的電子郵件'),
  phone: z.string().optional(),
  location: z.string().optional(),
  bio: z.string().max(500, '簡介不能超過500字').optional(),
  jobTitle: z.string().optional(),
  experience: z.number().min(0).optional(),
  skills: z.array(z.string()).optional(),
  salary: z.object({
    min: z.number().optional(),
    max: z.number().optional(),
    currency: z.string().default('TWD')
  }).optional()
});

type ProfileFormData = z.infer<typeof profileSchema>;

const UserProfile: React.FC = () => {
  const { t } = useTranslation();
  const { user, updateUser } = useUserStore();
  const [activeTab, setActiveTab] = useState('basic');
  const [isEditing, setIsEditing] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
    reset,
    watch
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: user
  });
  
  // 獲取用戶資料
  const { data: userData, isLoading } = useQuery({
    queryKey: ['user-profile', user?.id],
    queryFn: () => fetchUserProfile(user?.id),
    enabled: !!user?.id
  });
  
  // 更新用戶資料
  const updateProfileMutation = useMutation({
    mutationFn: updateUserProfile,
    onSuccess: (data) => {
      updateUser(data);
      setIsEditing(false);
      reset(data);
    },
    onError: (error) => {
      console.error('更新失敗:', error);
    }
  });
  
  const onSubmit = (data: ProfileFormData) => {
    updateProfileMutation.mutate({
      ...data,
      id: user?.id
    });
  };
  
  const handleCancel = () => {
    reset(userData);
    setIsEditing(false);
  };
  
  if (isLoading) {
    return <ProfileSkeleton />;
  }
  
  return (
    <div className="user-profile">
      <ProfileSidebar 
        activeTab={activeTab}
        onTabChange={setActiveTab}
        user={userData}
      />
      
      <div className="profile-main">
        <form onSubmit={handleSubmit(onSubmit)}>
          {activeTab === 'basic' && (
            <BasicInfoSection 
              register={register}
              errors={errors}
              isEditing={isEditing}
              watch={watch}
            />
          )}
          
          {activeTab === 'career' && (
            <CareerInfoSection 
              register={register}
              errors={errors}
              isEditing={isEditing}
            />
          )}
          
          {activeTab === 'preferences' && (
            <JobPreferencesSection 
              register={register}
              errors={errors}
              isEditing={isEditing}
            />
          )}
          
          {activeTab === 'resume' && (
            <ResumeManagementSection 
              user={userData}
            />
          )}
          
          {activeTab === 'notifications' && (
            <NotificationSettingsSection 
              user={userData}
            />
          )}
          
          {activeTab === 'privacy' && (
            <PrivacySettingsSection 
              user={userData}
            />
          )}
          
          {isEditing && (
            <div className="profile-actions">
              <button 
                type="button" 
                className="btn btn-outline-secondary me-2"
                onClick={handleCancel}
              >
                取消
              </button>
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={!isDirty || updateProfileMutation.isPending}
              >
                {updateProfileMutation.isPending ? '儲存中...' : '儲存變更'}
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default UserProfile;
```

### 狀態管理

```typescript
// stores/userStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  location?: string;
  bio?: string;
  avatar?: string;
  jobTitle?: string;
  experience?: number;
  skills?: string[];
  preferences?: {
    jobTypes: string[];
    locations: string[];
    salary: {
      min?: number;
      max?: number;
      currency: string;
    };
    workArrangement: string[];
  };
  notifications?: {
    email: boolean;
    push: boolean;
    sms: boolean;
    jobRecommendations: boolean;
    applicationUpdates: boolean;
  };
  privacy?: {
    profileVisible: boolean;
    contactVisible: boolean;
    resumeDownload: boolean;
    searchVisible: boolean;
  };
}

interface UserStore {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User) => void;
  updateUser: (updates: Partial<User>) => void;
  logout: () => void;
}

export const useUserStore = create<UserStore>()(n  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      
      setUser: (user) => set({ user, isAuthenticated: true }),
      
      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),
      
      logout: () => set({ user: null, isAuthenticated: false })
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated 
      })
    }
  )
);
```

## 🚀 實施計劃

### 第一階段：基礎功能 (1-2週)

1. **基本資料管理**
   - 個人資訊編輯表單
   - 頭像上傳功能
   - 表單驗證和錯誤處理
   - 資料儲存和更新

2. **職業資訊管理**
   - 工作經歷 CRUD
   - 技能標籤管理
   - 教育背景編輯

3. **基礎 UI 組件**
   - 側邊欄導航
   - 表單組件
   - 載入狀態
   - 錯誤提示

### 第二階段：進階功能 (2-3週)

1. **求職偏好設定**
   - 職位類型選擇
   - 地點偏好管理
   - 薪資範圍設定
   - 工作安排偏好

2. **履歷管理系統**
   - 履歷模板選擇
   - 在線編輯器
   - PDF 生成和下載
   - 履歷版本管理

3. **通知系統**
   - 通知偏好設定
   - 多渠道通知配置
   - 即時通知顯示

### 第三階段：優化和整合 (1-2週)

1. **隱私和安全**
   - 隱私設定面板
   - 資料可見性控制
   - 帳號安全設定
   - 資料導出功能

2. **響應式優化**
   - 移動端適配
   - 平板端優化
   - 觸控交互優化

3. **性能優化**
   - 代碼分割
   - 懶加載
   - 圖片優化
   - 快取策略

### 第四階段：測試和部署 (1週)

1. **測試覆蓋**
   - 單元測試
   - 整合測試
   - E2E 測試
   - 無障碍測試

2. **部署準備**
   - 生產環境配置
   - 監控和日誌
   - 錯誤追蹤
   - 性能監控

## 📊 成功指標

### 用戶體驗指標
- 個人資料完成率 > 80%
- 用戶滿意度評分 > 4.5/5
- 頁面載入時間 < 2秒
- 移動端可用性評分 > 90%

### 技術指標
- 代碼覆蓋率 > 85%
- 無障礙合規性 AA 級
- 跨瀏覽器兼容性 > 95%
- API 響應時間 < 500ms

### 業務指標
- 用戶資料完整度提升 40%
- 求職成功率提升 25%
- 用戶留存率提升 30%
- 客服諮詢減少 20%

---

*此設計文檔將作為 JobSpy v2 用戶個人資料頁面開發的完整指南，確保提供優秀的用戶體驗和強大的功能性。*

## 🎯 求職偏好設計

### 偏好設定頁面

```html
<div className="profile-job-preferences">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">求職偏好</h2>
      <p className="text-muted mb-0">設定您的求職偏好，獲得更精準的職位推薦</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-refresh-cw me-2"></i>
        重設偏好
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存偏好
      </button>
    </div>
  </div>
  
  <!-- 求職狀態 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">求職狀態</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <div className="form-floating">
            <select className="form-select" id="jobStatus">
              <option value="actively-looking" selected>積極求職中</option>
              <option value="open-to-opportunities">開放機會</option>
              <option value="not-looking">暫不求職</option>
              <option value="employed-but-open">在職但開放機會</option>
            </select>
            <label for="jobStatus">求職狀態</label>
          </div>
        </div>
        <div className="col-md-6">
          <div className="form-floating">
            <select className="form-select" id="availability">
              <option value="immediately" selected>立即可上班</option>
              <option value="2-weeks">2週內</option>
              <option value="1-month">1個月內</option>
              <option value="2-months">2個月內</option>
              <option value="3-months">3個月內</option>
            </select>
            <label for="availability">可上班時間</label>
          </div>
        </div>
        <div className="col-12">
          <div className="form-check form-switch">
            <input className="form-check-input" type="checkbox" id="profileVisible" checked>
            <label className="form-check-label" for="profileVisible">
              允許雇主查看我的個人資料
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 職位偏好 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">職位偏好</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <label className="form-label">期望職位 *</label>
          <div className="position-relative">
            <input type="text" className="form-control" id="desiredPositions" placeholder="輸入職位關鍵字">
            <div className="selected-items mt-2">
              <span className="badge bg-primary me-1 mb-1">
                前端工程師
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
              <span className="badge bg-primary me-1 mb-1">
                React 開發者
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
              <span className="badge bg-primary me-1 mb-1">
                全端工程師
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <label className="form-label">產業類別</label>
          <div className="position-relative">
            <input type="text" className="form-control" id="industries" placeholder="選擇產業">
            <div className="selected-items mt-2">
              <span className="badge bg-success me-1 mb-1">
                資訊科技
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
              <span className="badge bg-success me-1 mb-1">
                金融科技
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="form-floating">
            <select className="form-select" id="experienceLevel">
              <option value="entry">新鮮人 (0-1年)</option>
              <option value="junior">初級 (1-3年)</option>
              <option value="mid" selected>中級 (3-5年)</option>
              <option value="senior">高級 (5-8年)</option>
              <option value="lead">資深/主管 (8年以上)</option>
            </select>
            <label for="experienceLevel">經驗等級</label>
          </div>
        </div>
        <div className="col-md-6">
          <div className="form-floating">
            <select className="form-select" id="companySize">
              <option value="">不限</option>
              <option value="startup">新創公司 (1-50人)</option>
              <option value="small">小型企業 (51-200人)</option>
              <option value="medium" selected>中型企業 (201-1000人)</option>
              <option value="large">大型企業 (1000人以上)</option>
            </select>
            <label for="companySize">公司規模</label>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 工作條件 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">工作條件</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <label className="form-label">期望薪資範圍 (月薪)</label>
          <div className="row g-2">
            <div className="col-6">
              <div className="input-group">
                <span className="input-group-text">NT$</span>
                <input type="number" className="form-control" placeholder="最低" value="60000">
              </div>
            </div>
            <div className="col-6">
              <div className="input-group">
                <span className="input-group-text">NT$</span>
                <input type="number" className="form-control" placeholder="最高" value="90000">
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <label className="form-label">工作地點</label>
          <div className="position-relative">
            <input type="text" className="form-control" id="locations" placeholder="選擇工作地點">
            <div className="selected-items mt-2">
              <span className="badge bg-info me-1 mb-1">
                台北市
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
              <span className="badge bg-info me-1 mb-1">
                新北市
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
              <span className="badge bg-info me-1 mb-1">
                遠端工作
                <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
              </span>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <label className="form-label">工作類型</label>
          <div className="d-flex flex-wrap gap-2">
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="fullTime" checked>
              <label className="form-check-label" for="fullTime">全職</label>
            </div>
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="partTime">
              <label className="form-check-label" for="partTime">兼職</label>
            </div>
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="contract">
              <label className="form-check-label" for="contract">合約</label>
            </div>
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="freelance">
              <label className="form-check-label" for="freelance">自由工作</label>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <label className="form-label">工作模式</label>
          <div className="d-flex flex-wrap gap-2">
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="onSite" checked>
              <label className="form-check-label" for="onSite">現場工作</label>
            </div>
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="remote" checked>
              <label className="form-check-label" for="remote">遠端工作</label>
            </div>
            <div className="form-check">
              <input className="form-check-input" type="checkbox" id="hybrid" checked>
              <label className="form-check-label" for="hybrid">混合模式</label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 通知偏好 -->
  <div className="card border-0 shadow-sm">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">通知偏好</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <label className="form-label">職位推薦頻率</label>
          <div className="form-check">
            <input className="form-check-input" type="radio" name="notificationFreq" id="daily" checked>
            <label className="form-check-label" for="daily">每日推薦</label>
          </div>
          <div className="form-check">
            <input className="form-check-input" type="radio" name="notificationFreq" id="weekly">
            <label className="form-check-label" for="weekly">每週推薦</label>
          </div>
          <div className="form-check">
            <input className="form-check-input" type="radio" name="notificationFreq" id="monthly">
            <label className="form-check-label" for="monthly">每月推薦</label>
          </div>
        </div>
        <div className="col-md-6">
          <label className="form-label">通知方式</label>
          <div className="form-check form-switch">
            <input className="form-check-input" type="checkbox" id="emailNotif" checked>
            <label className="form-check-label" for="emailNotif">電子郵件通知</label>
          </div>
          <div className="form-check form-switch">
            <input className="form-check-input" type="checkbox" id="pushNotif" checked>
            <label className="form-check-label" for="pushNotif">推播通知</label>
          </div>
          <div className="form-check form-switch">
            <input className="form-check-input" type="checkbox" id="smsNotif">
            <label className="form-check-label" for="smsNotif">簡訊通知</label>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 📄 履歷管理設計

### 履歷編輯器

```html
<div className="profile-resume-management">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">履歷管理</h2>
      <p className="text-muted mb-0">建立和管理您的專業履歷</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-eye me-2"></i>
        預覽履歷
      </button>
      <button className="btn btn-outline-primary">
        <i className="lucide-download me-2"></i>
        下載 PDF
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存履歷
      </button>
    </div>
  </div>
  
  <!-- 履歷模板選擇 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">履歷模板</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-3">
          <div className="template-card border rounded p-3 text-center position-relative">
            <div className="template-preview bg-light rounded mb-2" style="height: 120px; background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 280"><rect width="200" height="40" fill="%23007bff"/><rect x="10" y="50" width="180" height="8" fill="%23dee2e6"/><rect x="10" y="65" width="120" height="6" fill="%23dee2e6"/><rect x="10" y="80" width="180" height="4" fill="%23dee2e6"/><rect x="10" y="90" width="180" height="4" fill="%23dee2e6"/><rect x="10" y="100" width="140" height="4" fill="%23dee2e6"/></svg>'); background-size: cover;"></div>
            <h6 className="mb-1">現代簡約</h6>
            <small className="text-muted">適合科技業</small>
            <div className="position-absolute top-0 end-0 m-2">
              <div className="form-check">
                <input className="form-check-input" type="radio" name="template" id="template1" checked>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="template-card border rounded p-3 text-center position-relative">
            <div className="template-preview bg-light rounded mb-2" style="height: 120px;"></div>
            <h6 className="mb-1">經典商務</h6>
            <small className="text-muted">適合傳統行業</small>
            <div className="position-absolute top-0 end-0 m-2">
              <div className="form-check">
                <input className="form-check-input" type="radio" name="template" id="template2">
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="template-card border rounded p-3 text-center position-relative">
            <div className="template-preview bg-light rounded mb-2" style="height: 120px;"></div>
            <h6 className="mb-1">創意設計</h6>
            <small className="text-muted">適合設計業</small>
            <div className="position-absolute top-0 end-0 m-2">
              <div className="form-check">
                <input className="form-check-input" type="radio" name="template" id="template3">
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="template-card border rounded p-3 text-center position-relative">
            <div className="template-preview bg-light rounded mb-2" style="height: 120px;"></div>
            <h6 className="mb-1">學術研究</h6>
            <small className="text-muted">適合學術界</small>
            <div className="position-absolute top-0 end-0 m-2">
              <div className="form-check">
                <input className="form-check-input" type="radio" name="template" id="template4">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 履歷內容編輯 -->
  <div className="row g-4">
    <!-- 左側編輯區 -->
    <div className="col-lg-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <h5 className="card-title mb-0">履歷內容編輯</h5>
        </div>
        <div className="card-body">
          <!-- 個人資訊區塊 -->
          <div className="resume-section mb-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h6 className="mb-0">個人資訊</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="includePersonal" checked>
                <label className="form-check-label" for="includePersonal">包含</label>
              </div>
            </div>
            <div className="row g-2">
              <div className="col-6">
                <input type="text" className="form-control form-control-sm" placeholder="姓名" value="張小明">
              </div>
              <div className="col-6">
                <input type="text" className="form-control form-control-sm" placeholder="職位" value="前端工程師">
              </div>
              <div className="col-6">
                <input type="email" className="form-control form-control-sm" placeholder="電子郵件" value="zhang@example.com">
              </div>
              <div className="col-6">
                <input type="tel" className="form-control form-control-sm" placeholder="電話" value="+886 912-345-678">
              </div>
            </div>
          </div>
          
          <!-- 專業摘要 -->
          <div className="resume-section mb-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h6 className="mb-0">專業摘要</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="includeSummary" checked>
                <label className="form-check-label" for="includeSummary">包含</label>
              </div>
            </div>
            <textarea className="form-control" rows="3" placeholder="簡述您的專業背景和核心技能...">具備 5 年以上前端開發經驗，專精於 React、TypeScript 等現代技術棧，擅長建構高性能的用戶界面和優化用戶體驗。</textarea>
          </div>
          
          <!-- 工作經歷 -->
          <div className="resume-section mb-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h6 className="mb-0">工作經歷</h6>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-primary">
                  <i className="lucide-plus"></i>
                </button>
                <div className="form-check form-switch">
                  <input className="form-check-input" type="checkbox" id="includeExperience" checked>
                  <label className="form-check-label" for="includeExperience">包含</label>
                </div>
              </div>
            </div>
            <div className="experience-items">
              <div className="border rounded p-2 mb-2">
                <div className="row g-2">
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="職位" value="前端工程師">
                  </div>
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="公司" value="科技公司 A">
                  </div>
                  <div className="col-6">
                    <input type="month" className="form-control form-control-sm" value="2022-03">
                  </div>
                  <div className="col-6">
                    <input type="month" className="form-control form-control-sm" placeholder="結束日期">
                  </div>
                  <div className="col-12">
                    <textarea className="form-control form-control-sm" rows="2" placeholder="工作描述">負責前端架構設計與開發，使用 React、TypeScript 等技術棧。</textarea>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 技能 -->
          <div className="resume-section mb-4">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h6 className="mb-0">專業技能</h6>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-primary">
                  <i className="lucide-plus"></i>
                </button>
                <div className="form-check form-switch">
                  <input className="form-check-input" type="checkbox" id="includeSkills" checked>
                  <label className="form-check-label" for="includeSkills">包含</label>
                </div>
              </div>
            </div>
            <div className="skills-input">
              <input type="text" className="form-control form-control-sm" placeholder="輸入技能，按 Enter 新增">
              <div className="selected-skills mt-2">
                <span className="badge bg-primary me-1 mb-1">
                  JavaScript
                  <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
                </span>
                <span className="badge bg-primary me-1 mb-1">
                  React
                  <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
                </span>
                <span className="badge bg-primary me-1 mb-1">
                  TypeScript
                  <button type="button" className="btn-close btn-close-white ms-1" style="font-size: 0.7em;"></button>
                </span>
              </div>
            </div>
          </div>
          
          <!-- 教育背景 -->
          <div className="resume-section">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h6 className="mb-0">教育背景</h6>
              <div className="d-flex gap-2">
                <button className="btn btn-sm btn-outline-primary">
                  <i className="lucide-plus"></i>
                </button>
                <div className="form-check form-switch">
                  <input className="form-check-input" type="checkbox" id="includeEducation" checked>
                  <label className="form-check-label" for="includeEducation">包含</label>
                </div>
              </div>
            </div>
            <div className="education-items">
              <div className="border rounded p-2">
                <div className="row g-2">
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="學位" value="學士">
                  </div>
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="科系" value="資訊工程">
                  </div>
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="學校" value="國立台灣大學">
                  </div>
                  <div className="col-6">
                    <input type="text" className="form-control form-control-sm" placeholder="畢業年份" value="2018">
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右側預覽區 -->
    <div className="col-lg-6">
      <div className="card border-0 shadow-sm">
        <div className="card-header bg-transparent border-0">
          <div className="d-flex justify-content-between align-items-center">
            <h5 className="card-title mb-0">履歷預覽</h5>
            <div className="btn-group btn-group-sm" role="group">
              <input type="radio" className="btn-check" name="previewMode" id="desktop" autocomplete="off" checked>
              <label className="btn btn-outline-secondary" for="desktop">
                <i className="lucide-monitor"></i>
              </label>
              
              <input type="radio" className="btn-check" name="previewMode" id="mobile" autocomplete="off">
              <label className="btn btn-outline-secondary" for="mobile">
                <i className="lucide-smartphone"></i>
              </label>
            </div>
          </div>
        </div>
        <div className="card-body">
          <div className="resume-preview border rounded p-3" style="height: 600px; overflow-y: auto; background: white;">
            <!-- 履歷預覽內容 -->
            <div className="resume-header text-center mb-3">
              <h4 className="mb-1">張小明</h4>
              <p className="text-muted mb-2">前端工程師</p>
              <div className="contact-info">
                <small className="text-muted">zhang@example.com • +886 912-345-678</small>
              </div>
            </div>
            
            <div className="resume-section mb-3">
              <h6 className="border-bottom pb-1 mb-2">專業摘要</h6>
              <p className="small">具備 5 年以上前端開發經驗，專精於 React、TypeScript 等現代技術棧，擅長建構高性能的用戶界面和優化用戶體驗。</p>
            </div>
            
            <div className="resume-section mb-3">
              <h6 className="border-bottom pb-1 mb-2">工作經歷</h6>
              <div className="experience-item mb-2">
                <div className="d-flex justify-content-between">
                  <strong className="small">前端工程師</strong>
                  <small className="text-muted">2022年3月 - 現在</small>
                </div>
                <div className="small text-muted mb-1">科技公司 A</div>
                <p className="small mb-0">負責前端架構設計與開發，使用 React、TypeScript 等技術棧。</p>
              </div>
            </div>
            
            <div className="resume-section mb-3">
              <h6 className="border-bottom pb-1 mb-2">專業技能</h6>
              <div className="skills-list">
                <span className="badge bg-light text-dark me-1 mb-1">JavaScript</span>
                <span className="badge bg-light text-dark me-1 mb-1">React</span>
                <span className="badge bg-light text-dark me-1 mb-1">TypeScript</span>
              </div>
            </div>
            
            <div className="resume-section">
              <h6 className="border-bottom pb-1 mb-2">教育背景</h6>
              <div className="education-item">
                <div className="d-flex justify-content-between">
                  <strong className="small">學士 - 資訊工程</strong>
                  <small className="text-muted">2018</small>
                </div>
                <div className="small text-muted">國立台灣大學</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 🔔 通知設定設計

### 通知偏好管理

```html
<div className="profile-notification-settings">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">通知設定</h2>
      <p className="text-muted mb-0">管理您的通知偏好和提醒設定</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-bell-off me-2"></i>
        全部關閉
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存設定
      </button>
    </div>
  </div>
  
  <!-- 職位推薦通知 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">職位推薦通知</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">新職位推薦</h6>
              <small className="text-muted">根據您的偏好推薦新職位</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="jobRecommendations" checked>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">緊急職位</h6>
              <small className="text-muted">高匹配度的緊急職位通知</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="urgentJobs" checked>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">薪資提醒</h6>
              <small className="text-muted">符合薪資期望的職位</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="salaryAlerts">
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">地點匹配</h6>
              <small className="text-muted">符合地點偏好的職位</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="locationMatch" checked>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 應用程式通知 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">應用程式通知</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">申請狀態更新</h6>
              <small className="text-muted">職位申請狀態變更通知</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="applicationUpdates" checked>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">面試邀請</h6>
              <small className="text-muted">收到面試邀請時通知</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="interviewInvites" checked>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">訊息通知</h6>
              <small className="text-muted">收到新訊息時通知</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="messageNotifications" checked>
            </div>
          </div>
        </div>
        <div className="col-md-6">
          <div className="notification-item d-flex justify-content-between align-items-center p-3 border rounded">
            <div>
              <h6 className="mb-1">系統更新</h6>
              <small className="text-muted">系統功能更新和維護通知</small>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="systemUpdates">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 通知方式設定 -->
  <div className="card border-0 shadow-sm">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">通知方式</h5>
    </div>
    <div className="card-body">
      <div className="table-responsive">
        <table className="table table-borderless">
          <thead>
            <tr>
              <th>通知類型</th>
              <th className="text-center">電子郵件</th>
              <th className="text-center">推播通知</th>
              <th className="text-center">簡訊</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>職位推薦</td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="jobEmail" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="jobPush" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="jobSms">
                </div>
              </td>
            </tr>
            <tr>
              <td>申請更新</td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="appEmail" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="appPush" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="appSms" checked>
                </div>
              </td>
            </tr>
            <tr>
              <td>面試邀請</td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="interviewEmail" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="interviewPush" checked>
                </div>
              </td>
              <td className="text-center">
                <div className="form-check form-switch d-inline-block">
                  <input className="form-check-input" type="checkbox" id="interviewSms" checked>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
```

## 🔒 隱私設定設計

### 隱私控制面板

```html
<div className="profile-privacy-settings">
  <!-- 頁面標題 -->
  <div className="d-flex justify-content-between align-items-center mb-4">
    <div>
      <h2 className="mb-1">隱私設定</h2>
      <p className="text-muted mb-0">控制您的個人資料可見性和隱私偏好</p>
    </div>
    <div className="d-flex gap-2">
      <button className="btn btn-outline-secondary">
        <i className="lucide-shield me-2"></i>
        隱私檢查
      </button>
      <button className="btn btn-primary">
        <i className="lucide-save me-2"></i>
        儲存設定
      </button>
    </div>
  </div>
  
  <!-- 個人資料可見性 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">個人資料可見性</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">個人資料</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="profileVisible" checked>
              </div>
            </div>
            <small className="text-muted">允許雇主查看您的基本個人資料</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">聯絡資訊</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="contactVisible">
              </div>
            </div>
            <small className="text-muted">顯示電話和電子郵件給雇主</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">履歷下載</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="resumeDownload" checked>
              </div>
            </div>
            <small className="text-muted">允許雇主下載您的履歷</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">求職狀態</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="jobStatusVisible" checked>
              </div>
            </div>
            <small className="text-muted">顯示您的求職狀態</small>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 搜尋和推薦 -->
  <div className="card border-0 shadow-sm mb-4">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">搜尋和推薦</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">搜尋結果顯示</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="searchVisible" checked>
              </div>
            </div>
            <small className="text-muted">允許在雇主搜尋結果中顯示</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">個人化推薦</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="personalizedRecs" checked>
              </div>
            </div>
            <small className="text-muted">使用您的資料提供個人化推薦</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">活動追蹤</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="activityTracking">
              </div>
            </div>
            <small className="text-muted">追蹤您的活動以改善服務</small>
          </div>
        </div>
        <div className="col-md-6">
          <div className="privacy-item border rounded p-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">第三方分享</h6>
              <div className="form-check form-switch">
                <input className="form-check-input" type="checkbox" id="thirdPartySharing">
              </div>
            </div>
            <small className="text-muted">與合作夥伴分享匿名化資料</small>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 資料管理 -->
  <div className="card border-0 shadow-sm">
    <div className="card-header bg-transparent border-0">
      <h5 className="card-title mb-0">資料管理</h5>
    </div>
    <div className="card-body">
      <div className="row g-3">
        <div className="col-md-4">
          <div className="text-center p-3 border rounded">
            <i className="lucide-download text-primary mb-2" style="font-size: 2rem;"></i>
            <h6>下載資料</h6>
            <p className="small text-muted mb-3">下載您的所有個人資料</p>
            <button className="btn btn-outline-primary btn-sm">下載</button>
          </div>
        </div>
        <div className="col-md-4">
          <div className="text-center p-3 border rounded">
            <i className="lucide-trash-2 text-warning mb-2" style="font-size: 2rem;"></i>
            <h6>刪除帳號</h6>
            <p className="small text-muted mb-3">永久刪除您的帳號和資料</p>
            <button className="btn btn-outline-warning btn-sm">刪除</button>
          </div>
        </div>
        <div className="col-md-4">
          <div className="text-center p-3 border rounded">
            <i className="lucide-shield-check text-success mb-2" style="font-size: 2rem;"></i>
            <h6>隱私報告</h6>
            <p className="small text-muted mb-3">查看您的隱私設定報告</p>
            <button className="btn btn-outline-success btn-sm">查看</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```