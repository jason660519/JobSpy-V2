# JobSpy v2 職位詳情頁面設計

## 📋 設計概述

職位詳情頁面是求職者了解職位資訊並做出申請決定的關鍵頁面。此頁面需要提供完整的職位資訊、直觀的申請流程、相關職位推薦，以及良好的用戶體驗。

## 🎯 設計目標

### 核心目標
- **資訊完整性**：提供全面、結構化的職位資訊
- **申請便利性**：簡化申請流程，提高轉換率
- **決策支援**：幫助求職者做出明智的申請決定
- **互動性**：提供收藏、分享、比較等互動功能
- **推薦精準性**：基於用戶偏好推薦相關職位

### 用戶體驗目標
- 清晰的資訊層次結構
- 快速的頁面載入速度
- 直觀的操作流程
- 響應式設計適配
- 無障礙訪問支援

## 🛠️ 技術要求

### 前端技術棧
- **React 18** + **TypeScript** - 現代化前端框架
- **Bootstrap 5** - 響應式 UI 框架
- **Lucide React** - 一致的圖標系統
- **React Hook Form** + **Zod** - 表單處理和驗證
- **TanStack Query** - 數據獲取和快取
- **Zustand** - 狀態管理
- **i18next** - 國際化支援
- **React Router** - 路由管理

### 核心功能模組
- 職位資訊展示
- 申請流程管理
- 收藏和分享功能
- 相關職位推薦
- 公司資訊展示
- 評論和評分系統

## 🎨 視覺設計

### 整體布局

```html
<div className="job-details-page">
  <!-- 頂部導航 -->
  <nav className="job-nav sticky-top bg-white border-bottom">
    <div className="container">
      <div className="d-flex justify-content-between align-items-center py-2">
        <div className="d-flex align-items-center">
          <button className="btn btn-link p-0 me-3" onClick={() => navigate(-1)}>
            <i className="lucide-arrow-left"></i>
          </button>
          <span className="text-muted small">返回搜尋結果</span>
        </div>
        <div className="d-flex gap-2">
          <button className="btn btn-outline-secondary btn-sm">
            <i className="lucide-share-2 me-1"></i>
            分享
          </button>
          <button className="btn btn-outline-primary btn-sm">
            <i className="lucide-heart me-1"></i>
            收藏
          </button>
        </div>
      </div>
    </div>
  </nav>
  
  <!-- 主要內容 -->
  <div className="container py-4">
    <div className="row">
      <!-- 左側主要內容 -->
      <div className="col-lg-8">
        <!-- 職位標題區域 -->
        <div className="job-header mb-4">
          <!-- 職位基本資訊 -->
        </div>
        
        <!-- 職位詳細資訊 -->
        <div className="job-content">
          <!-- 職位描述、要求等 -->
        </div>
      </div>
      
      <!-- 右側邊欄 -->
      <div className="col-lg-4">
        <!-- 申請卡片 -->
        <div className="application-card sticky-top">
          <!-- 申請按鈕和相關操作 -->
        </div>
        
        <!-- 公司資訊 -->
        <div className="company-info mt-4">
          <!-- 公司詳細資訊 -->
        </div>
        
        <!-- 相關職位推薦 -->
        <div className="related-jobs mt-4">
          <!-- 推薦職位列表 -->
        </div>
      </div>
    </div>
  </div>
</div>
```

## 📋 右側邊欄設計

### 申請卡片

```html
<div className="application-card card border-0 shadow-sm sticky-top">
  <div className="card-body">
    <!-- 申請狀態 -->
    <div className="application-status mb-3">
      {user?.appliedJobs?.includes(job.id) ? (
        <div className="alert alert-success d-flex align-items-center mb-0">
          <i className="lucide-check-circle me-2"></i>
          <span>您已申請此職位</span>
        </div>
      ) : (
        <div className="d-grid gap-2">
          <button 
            className="btn btn-primary btn-lg"
            onClick={() => handleApply(job.id)}
            disabled={!user || isApplying}
          >
            {isApplying ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                申請中...
              </>
            ) : (
              <>
                <i className="lucide-send me-2"></i>
                立即申請
              </>
            )}
          </button>
          
          <div className="row g-2">
            <div className="col-6">
              <button 
                className={`btn btn-outline-primary w-100 ${user?.savedJobs?.includes(job.id) ? 'active' : ''}`}
                onClick={() => handleSave(job.id)}
              >
                <i className={`lucide-heart me-1 ${user?.savedJobs?.includes(job.id) ? 'fill' : ''}`}></i>
                {user?.savedJobs?.includes(job.id) ? '已收藏' : '收藏'}
              </button>
            </div>
            <div className="col-6">
              <button 
                className="btn btn-outline-secondary w-100"
                onClick={() => handleShare(job)}
              >
                <i className="lucide-share-2 me-1"></i>
                分享
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    
    <!-- 申請要求 -->
    <div className="application-requirements">
      <h6 className="mb-3">申請要求</h6>
      <div className="requirements-checklist">
        <div className="requirement-item d-flex align-items-center mb-2">
          <i className={`lucide-${user?.profile?.resume ? 'check-circle text-success' : 'x-circle text-danger'} me-2`}></i>
          <span className={user?.profile?.resume ? 'text-success' : 'text-danger'}>
            上傳履歷
          </span>
          {!user?.profile?.resume && (
            <a href="/profile/resume" className="ms-auto text-primary text-decoration-none small">
              上傳
            </a>
          )}
        </div>
        <div className="requirement-item d-flex align-items-center mb-2">
          <i className={`lucide-${user?.profile?.complete ? 'check-circle text-success' : 'x-circle text-danger'} me-2`}></i>
          <span className={user?.profile?.complete ? 'text-success' : 'text-danger'}>
            完整個人資料
          </span>
          {!user?.profile?.complete && (
            <a href="/profile" className="ms-auto text-primary text-decoration-none small">
              完善
            </a>
          )}
        </div>
        <div className="requirement-item d-flex align-items-center mb-2">
          <i className="lucide-check-circle text-success me-2"></i>
          <span className="text-success">驗證電子郵件</span>
        </div>
      </div>
    </div>
    
    <!-- 申請統計 -->
    <div className="application-stats mt-3 pt-3 border-top">
      <div className="row text-center">
        <div className="col-6">
          <div className="stat-item">
            <div className="h6 mb-0 text-primary">{job.applications || 0}</div>
            <small className="text-muted">申請人數</small>
          </div>
        </div>
        <div className="col-6">
          <div className="stat-item">
            <div className="h6 mb-0 text-warning">{calculateDaysLeft(job.deadline)}</div>
            <small className="text-muted">剩餘天數</small>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 快速申請提示 -->
    {!user && (
      <div className="login-prompt mt-3 p-3 bg-light rounded">
        <div className="text-center">
          <i className="lucide-user-plus text-primary mb-2" style={{fontSize: '2rem'}}></i>
          <h6>登入以申請職位</h6>
          <p className="small text-muted mb-3">登入後可以快速申請並追蹤申請狀態</p>
          <div className="d-grid gap-2">
            <a href="/login" className="btn btn-primary btn-sm">登入</a>
            <a href="/register" className="btn btn-outline-primary btn-sm">註冊</a>
          </div>
        </div>
      </div>
    )}
  </div>
</div>
```

### 公司資訊卡片

```html
<div className="company-info card border-0 shadow-sm mt-4">
  <div className="card-body">
    <div className="d-flex align-items-center mb-3">
      <img 
        src={job.company.logo} 
        alt={job.company.name}
        className="rounded me-3"
        style={{width: '50px', height: '50px', objectFit: 'cover'}}
      />
      <div>
        <h6 className="mb-1">
          <a href={`/company/${job.company.id}`} className="text-decoration-none">
            {job.company.name}
          </a>
        </h6>
        <small className="text-muted">{job.company.industry}</small>
      </div>
    </div>
    
    <div className="company-stats mb-3">
      <div className="row g-2 text-center">
        <div className="col-4">
          <div className="stat-item">
            <div className="small fw-semibold text-primary">{job.company.employees || 'N/A'}</div>
            <div className="small text-muted">員工數</div>
          </div>
        </div>
        <div className="col-4">
          <div className="stat-item">
            <div className="small fw-semibold text-success">{job.company.rating || 'N/A'}</div>
            <div className="small text-muted">評分</div>
          </div>
        </div>
        <div className="col-4">
          <div className="stat-item">
            <div className="small fw-semibold text-warning">{job.company.openPositions || 0}</div>
            <div className="small text-muted">職位</div>
          </div>
        </div>
      </div>
    </div>
    
    <div className="company-description mb-3">
      <p className="small text-muted mb-0">
        {job.company.description?.substring(0, 120)}...
      </p>
    </div>
    
    <div className="d-grid gap-2">
      <a href={`/company/${job.company.id}`} className="btn btn-outline-primary btn-sm">
        <i className="lucide-building me-2"></i>
        查看公司詳情
      </a>
      <button 
        className="btn btn-outline-secondary btn-sm"
        onClick={() => handleFollowCompany(job.company.id)}
      >
        <i className="lucide-plus me-2"></i>
        關注公司
      </button>
    </div>
  </div>
</div>
```

### 相關職位推薦

```html
<div className="related-jobs card border-0 shadow-sm mt-4">
  <div className="card-header bg-transparent border-0">
    <h6 className="mb-0">
      <i className="lucide-briefcase text-primary me-2"></i>
      相關職位推薦
    </h6>
  </div>
  <div className="card-body p-0">
    {relatedJobs?.length > 0 ? (
      <div className="related-jobs-list">
        {relatedJobs.slice(0, 5).map((relatedJob, index) => (
          <div key={index} className="related-job-item p-3 border-bottom">
            <div className="d-flex align-items-start">
              <img 
                src={relatedJob.company.logo} 
                alt={relatedJob.company.name}
                className="rounded me-3"
                style={{width: '40px', height: '40px', objectFit: 'cover'}}
              />
              <div className="flex-grow-1">
                <h6 className="mb-1">
                  <a 
                    href={`/jobs/${relatedJob.id}`} 
                    className="text-decoration-none text-dark"
                  >
                    {relatedJob.title}
                  </a>
                </h6>
                <div className="small text-muted mb-2">
                  <span className="me-2">{relatedJob.company.name}</span>
                  <span className="me-2">•</span>
                  <span>{relatedJob.location}</span>
                </div>
                <div className="d-flex justify-content-between align-items-center">
                  <div className="small text-success fw-semibold">
                    {relatedJob.salary ? 
                      `${relatedJob.salary.min}-${relatedJob.salary.max} ${relatedJob.salary.currency}` : 
                      '面議'
                    }
                  </div>
                  <div className="d-flex gap-1">
                    <button 
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => handleSave(relatedJob.id)}
                    >
                      <i className="lucide-heart" style={{fontSize: '12px'}}></i>
                    </button>
                    <a 
                      href={`/jobs/${relatedJob.id}`} 
                      className="btn btn-primary btn-sm"
                    >
                      查看
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <div className="text-center py-4">
        <i className="lucide-search text-muted mb-2" style={{fontSize: '2rem'}}></i>
        <p className="text-muted mb-0">暫無相關職位</p>
      </div>
    )}
    
    {relatedJobs?.length > 5 && (
      <div className="p-3">
        <a href={`/search?similar=${job.id}`} className="btn btn-outline-primary w-100 btn-sm">
          查看更多相關職位
        </a>
      </div>
    )}
  </div>
</div>
```

## 📱 響應式設計

### 移動端適配

```css
/* 移動端樣式 */
@media (max-width: 768px) {
  .job-details-page {
    padding: 0;
  }
  
  .job-nav {
    padding: 0.5rem 0;
  }
  
  .job-header {
    margin: 1rem;
    padding: 1rem;
  }
  
  .job-header .row {
    flex-direction: column;
    text-align: center;
  }
  
  .company-logo {
    margin-bottom: 1rem;
  }
  
  .salary-benefits .row {
    flex-direction: column;
  }
  
  .job-stats .row {
    justify-content: space-around;
  }
  
  .nav-tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    border-bottom: 1px solid #dee2e6;
  }
  
  .nav-tabs .nav-link {
    white-space: nowrap;
    font-size: 0.875rem;
    padding: 0.5rem 0.75rem;
  }
  
  .application-card {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    border-radius: 1rem 1rem 0 0;
    box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
  }
  
  .company-info,
  .related-jobs {
    margin: 1rem;
  }
  
  .job-content {
    margin: 1rem;
    padding-bottom: 200px; /* 為固定的申請卡片留出空間 */
  }
}

/* 平板端樣式 */
@media (min-width: 769px) and (max-width: 1024px) {
  .container {
    padding: 0 1rem;
  }
  
  .job-header {
    padding: 2rem;
  }
  
  .application-card {
    position: sticky;
    top: 2rem;
  }
}
```

## ⚙️ 技術實現

### 核心組件結構

```typescript
// JobDetails.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { useUserStore } from '../stores/userStore';
import { useJobStore } from '../stores/jobStore';

interface JobDetailsProps {
  jobId?: string;
}

const JobDetails: React.FC<JobDetailsProps> = ({ jobId: propJobId }) => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { user } = useUserStore();
  const { saveJob, unsaveJob, applyToJob } = useJobStore();
  
  const jobId = propJobId || id;
  const [activeTab, setActiveTab] = useState('description');
  const [isApplying, setIsApplying] = useState(false);
  
  // 獲取職位詳情
  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job-details', jobId],
    queryFn: () => fetchJobDetails(jobId),
    enabled: !!jobId
  });
  
  // 獲取相關職位
  const { data: relatedJobs } = useQuery({
    queryKey: ['related-jobs', jobId],
    queryFn: () => fetchRelatedJobs(jobId),
    enabled: !!jobId
  });
  
  // 申請職位
  const applyMutation = useMutation({
    mutationFn: (jobId: string) => applyToJob(jobId),
    onSuccess: () => {
      setIsApplying(false);
      // 顯示成功提示
    },
    onError: (error) => {
      setIsApplying(false);
      console.error('申請失敗:', error);
    }
  });
  
  // 收藏職位
  const saveMutation = useMutation({
    mutationFn: ({ jobId, action }: { jobId: string; action: 'save' | 'unsave' }) => {
      return action === 'save' ? saveJob(jobId) : unsaveJob(jobId);
    }
  });
  
  const handleApply = async (jobId: string) => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    setIsApplying(true);
    applyMutation.mutate(jobId);
  };
  
  const handleSave = (jobId: string) => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    const isSaved = user.savedJobs?.includes(jobId);
    saveMutation.mutate({
      jobId,
      action: isSaved ? 'unsave' : 'save'
    });
  };
  
  const handleShare = (job: Job) => {
    if (navigator.share) {
      navigator.share({
        title: job.title,
        text: `查看這個職位：${job.title} - ${job.company.name}`,
        url: window.location.href
      });
    } else {
      // 複製到剪貼板
      navigator.clipboard.writeText(window.location.href);
    }
  };
  
  const calculateDaysLeft = (deadline: string) => {
    if (!deadline) return '無限期';
    const days = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    return days > 0 ? `${days} 天` : '已截止';
  };
  
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('zh-TW');
  };
  
  if (isLoading) {
    return <JobDetailsSkeleton />;
  }
  
  if (error || !job) {
    return (
      <div className="container py-5 text-center">
        <i className="lucide-alert-circle text-danger mb-3" style={{fontSize: '3rem'}}></i>
        <h4>職位不存在</h4>
        <p className="text-muted">抱歉，您查找的職位可能已被移除或不存在。</p>
        <button className="btn btn-primary" onClick={() => navigate('/search')}>
          返回搜尋
        </button>
      </div>
    );
  }
  
  return (
    <div className="job-details-page">
      {/* 導航欄 */}
      <nav className="job-nav sticky-top bg-white border-bottom">
        {/* 導航內容 */}
      </nav>
      
      {/* 主要內容 */}
      <div className="container py-4">
        <div className="row">
          <div className="col-lg-8">
            {/* 職位標題區域 */}
            <JobHeader job={job} />
            
            {/* 職位詳細內容 */}
            <JobContent 
              job={job} 
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
          </div>
          
          <div className="col-lg-4">
            {/* 申請卡片 */}
            <ApplicationCard 
              job={job}
              user={user}
              isApplying={isApplying}
              onApply={handleApply}
              onSave={handleSave}
              onShare={handleShare}
            />
            
            {/* 公司資訊 */}
            <CompanyInfoCard company={job.company} />
            
            {/* 相關職位推薦 */}
            <RelatedJobsCard 
              relatedJobs={relatedJobs}
              onSave={handleSave}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetails;
```

### 狀態管理

```typescript
// stores/jobStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Job {
  id: string;
  title: string;
  company: {
    id: string;
    name: string;
    logo: string;
    industry: string;
    size: string;
    description: string;
    rating?: number;
    reviews?: number;
    openPositions?: number;
  };
  location: string;
  employmentType: string;
  description: string;
  requirements: string[];
  responsibilities: string[];
  skills: string[];
  requiredSkills: string[];
  preferredSkills?: string[];
  salary?: {
    min: number;
    max: number;
    currency: string;
  };
  benefits?: {
    vacation: string;
    insurance: string;
    others: string[];
  };
  experience?: string;
  education?: string;
  languages?: string[];
  publishedAt: string;
  deadline?: string;
  isUrgent?: boolean;
  isRemote?: boolean;
  isNew?: boolean;
  views?: number;
  applications?: number;
  saves?: number;
  reviews?: Array<{
    author: string;
    position: string;
    rating: number;
    content: string;
    date: string;
  }>;
}

interface JobStore {
  currentJob: Job | null;
  savedJobs: string[];
  appliedJobs: string[];
  viewHistory: string[];
  
  setCurrentJob: (job: Job) => void;
  saveJob: (jobId: string) => Promise<void>;
  unsaveJob: (jobId: string) => Promise<void>;
  applyToJob: (jobId: string) => Promise<void>;
  addToViewHistory: (jobId: string) => void;
  clearHistory: () => void;
}

export const useJobStore = create<JobStore>()(n  persist(
    (set, get) => ({
      currentJob: null,
      savedJobs: [],
      appliedJobs: [],
      viewHistory: [],
      
      setCurrentJob: (job) => {
        set({ currentJob: job });
        get().addToViewHistory(job.id);
      },
      
      saveJob: async (jobId) => {
        try {
          await api.saveJob(jobId);
          set((state) => ({
            savedJobs: [...state.savedJobs, jobId]
          }));
        } catch (error) {
          throw error;
        }
      },
      
      unsaveJob: async (jobId) => {
        try {
          await api.unsaveJob(jobId);
          set((state) => ({
            savedJobs: state.savedJobs.filter(id => id !== jobId)
          }));
        } catch (error) {
          throw error;
        }
      },
      
      applyToJob: async (jobId) => {
        try {
          await api.applyToJob(jobId);
          set((state) => ({
            appliedJobs: [...state.appliedJobs, jobId]
          }));
        } catch (error) {
          throw error;
        }
      },
      
      addToViewHistory: (jobId) => {
        set((state) => {
          const newHistory = [jobId, ...state.viewHistory.filter(id => id !== jobId)];
          return {
            viewHistory: newHistory.slice(0, 50) // 保留最近50個
          };
        });
      },
      
      clearHistory: () => set({ viewHistory: [] })
    }),
    {
      name: 'job-storage',
      partialize: (state) => ({
        savedJobs: state.savedJobs,
        appliedJobs: state.appliedJobs,
        viewHistory: state.viewHistory
      })
    }
  )
);
```

## 📊 分階段實施計畫

### 第一階段：基礎功能 (1-2週)
- [ ] 職位詳情頁面基本佈局
- [ ] 職位標題區域實現
- [ ] 職位描述和要求展示
- [ ] 基本申請功能
- [ ] 收藏功能
- [ ] 響應式設計基礎

### 第二階段：進階功能 (2-3週)
- [ ] 公司資訊卡片
- [ ] 相關職位推薦
- [ ] 申請狀態管理
- [ ] 分享功能
- [ ] 員工評價系統
- [ ] 申請要求檢查

### 第三階段：優化整合 (1-2週)
- [ ] 性能優化
- [ ] SEO 優化
- [ ] 無障碍設計
- [ ] 國際化支持
- [ ] 錯誤處理優化
- [ ] 載入狀態優化

### 第四階段：測試部署 (1週)
- [ ] 單元測試
- [ ] 整合測試
- [ ] E2E 測試
- [ ] 性能測試
- [ ] 用戶驗收測試
- [ ] 生產環境部署

## 🧪 測試策略

### 單元測試
```typescript
// JobDetails.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import JobDetails from './JobDetails';
import { useUserStore } from '../stores/userStore';
import { useJobStore } from '../stores/jobStore';

// Mock stores
jest.mock('../stores/userStore');
jest.mock('../stores/jobStore');

const mockJob = {
  id: '1',
  title: 'Frontend Developer',
  company: {
    id: '1',
    name: 'Tech Corp',
    logo: '/logo.png',
    industry: 'Technology'
  },
  location: 'Taipei',
  description: 'Job description',
  requirements: ['React', 'TypeScript'],
  salary: { min: 50000, max: 80000, currency: 'TWD' }
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('JobDetails', () => {
  beforeEach(() => {
    (useUserStore as jest.Mock).mockReturnValue({
      user: { id: '1', savedJobs: [], appliedJobs: [] }
    });
    
    (useJobStore as jest.Mock).mockReturnValue({
      saveJob: jest.fn(),
      unsaveJob: jest.fn(),
      applyToJob: jest.fn()
    });
  });
  
  test('renders job details correctly', async () => {
    renderWithProviders(<JobDetails />);
    
    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('Taipei')).toBeInTheDocument();
    });
  });
  
  test('handles job application', async () => {
    const mockApplyToJob = jest.fn();
    (useJobStore as jest.Mock).mockReturnValue({
      applyToJob: mockApplyToJob
    });
    
    renderWithProviders(<JobDetails />);
    
    const applyButton = screen.getByText('立即申請');
    fireEvent.click(applyButton);
    
    await waitFor(() => {
      expect(mockApplyToJob).toHaveBeenCalledWith('1');
    });
  });
  
  test('handles job saving', async () => {
    const mockSaveJob = jest.fn();
    (useJobStore as jest.Mock).mockReturnValue({
      saveJob: mockSaveJob
    });
    
    renderWithProviders(<JobDetails />);
    
    const saveButton = screen.getByText('收藏');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockSaveJob).toHaveBeenCalledWith('1');
    });
  });
});
```

### E2E 測試
```typescript
// e2e/job-details.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Job Details Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/jobs/1');
  });
  
  test('displays job information correctly', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Frontend Developer');
    await expect(page.locator('.company-name')).toContainText('Tech Corp');
    await expect(page.locator('.job-location')).toContainText('Taipei');
  });
  
  test('allows user to apply for job', async ({ page }) => {
    // 登入用戶
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="login-button"]');
    
    // 返回職位詳情頁
    await page.goto('/jobs/1');
    
    // 申請職位
    await page.click('[data-testid="apply-button"]');
    await expect(page.locator('.alert-success')).toContainText('您已申請此職位');
  });
  
  test('allows user to save job', async ({ page }) => {
    await page.click('[data-testid="save-button"]');
    await expect(page.locator('[data-testid="save-button"]')).toContainText('已收藏');
  });
  
  test('displays related jobs', async ({ page }) => {
    await expect(page.locator('.related-jobs')).toBeVisible();
    await expect(page.locator('.related-job-item')).toHaveCount(5);
  });
  
  test('is responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await expect(page.locator('.application-card')).toHaveCSS('position', 'fixed');
    await expect(page.locator('.application-card')).toHaveCSS('bottom', '0px');
  });
});
```

## 📈 成功指標

### 用戶體驗指標
- **頁面載入時間**: < 2秒
- **互動響應時間**: < 100ms
- **申請轉換率**: > 15%
- **頁面停留時間**: > 3分鐘
- **跳出率**: < 40%

### 技術指標
- **Core Web Vitals**:
  - LCP (Largest Contentful Paint): < 2.5s
  - FID (First Input Delay): < 100ms
  - CLS (Cumulative Layout Shift): < 0.1
- **SEO 分數**: > 90
- **無障礙分數**: > 95
- **性能分數**: > 90

### 業務指標
- **職位申請數量**: 提升 25%
- **用戶註冊轉換**: 提升 20%
- **頁面分享次數**: 提升 30%
- **用戶滿意度**: > 4.5/5
- **移動端使用率**: > 60%

## 🔧 維護和優化

### 持續優化計畫
1. **性能監控**: 使用 Web Vitals 監控頁面性能
2. **用戶行為分析**: 追蹤用戶互動和轉換漏斗
3. **A/B 測試**: 測試不同的 UI 元素和佈局
4. **錯誤監控**: 使用 Sentry 監控前端錯誤
5. **定期更新**: 每月檢視和更新設計元素

### 未來功能擴展
- 職位比較功能
- 薪資談判工具
- 面試準備資源
- 職業發展建議
- AI 職位匹配

---

**設計完成日期**: 2024年1月
**負責團隊**: UI/UX 設計團隊、前端開發團隊
**審核狀態**: 待審核

### 色彩方案

```css
:root {
  /* 主要色彩 */
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #dbeafe;
  
  /* 次要色彩 */
  --secondary-color: #64748b;
  --secondary-light: #f1f5f9;
  
  /* 狀態色彩 */
  --success-color: #059669;
  --warning-color: #d97706;
  --danger-color: #dc2626;
  --info-color: #0891b2;
  
  /* 中性色彩 */
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-400: #94a3b8;
  --gray-500: #64748b;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1e293b;
  --gray-900: #0f172a;
  
  /* 背景色彩 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-accent: #f0f9ff;
  
  /* 邊框和陰影 */
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

## 💼 職位標題區域設計

### 職位基本資訊

```html
<div className="job-header card border-0 shadow-sm p-4 mb-4">
  <div className="row align-items-start">
    <!-- 公司 Logo -->
    <div className="col-auto">
      <div className="company-logo">
        <img 
          src={job.company.logo} 
          alt={job.company.name}
          className="rounded"
          style={{width: '80px', height: '80px', objectFit: 'cover'}}
        />
      </div>
    </div>
    
    <!-- 職位資訊 -->
    <div className="col">
      <div className="d-flex justify-content-between align-items-start mb-2">
        <div>
          <h1 className="h3 mb-1 fw-bold">{job.title}</h1>
          <div className="d-flex align-items-center text-muted mb-2">
            <a href={`/company/${job.company.id}`} className="text-decoration-none me-3">
              <strong className="text-dark">{job.company.name}</strong>
            </a>
            <span className="me-3">
              <i className="lucide-map-pin me-1" style={{fontSize: '14px'}}></i>
              {job.location}
            </span>
            <span className="me-3">
              <i className="lucide-clock me-1" style={{fontSize: '14px'}}></i>
              {job.employmentType}
            </span>
            <span>
              <i className="lucide-calendar me-1" style={{fontSize: '14px'}}></i>
              發布於 {formatDate(job.publishedAt)}
            </span>
          </div>
        </div>
        
        <!-- 職位狀態標籤 -->
        <div className="d-flex flex-column align-items-end">
          {job.isUrgent && (
            <span className="badge bg-danger mb-1">
              <i className="lucide-zap me-1"></i>
              緊急招聘
            </span>
          )}
          {job.isRemote && (
            <span className="badge bg-info mb-1">
              <i className="lucide-wifi me-1"></i>
              遠程工作
            </span>
          )}
          {job.isNew && (
            <span className="badge bg-success">
              <i className="lucide-star me-1"></i>
              新職位
            </span>
          )}
        </div>
      </div>
      
      <!-- 薪資和福利 -->
      <div className="salary-benefits mb-3">
        <div className="row g-3">
          <div className="col-md-4">
            <div className="d-flex align-items-center">
              <i className="lucide-dollar-sign text-success me-2"></i>
              <div>
                <div className="fw-semibold text-success">
                  {job.salary ? `${job.salary.min} - ${job.salary.max} ${job.salary.currency}` : '面議'}
                </div>
                <small className="text-muted">月薪</small>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="d-flex align-items-center">
              <i className="lucide-users text-primary me-2"></i>
              <div>
                <div className="fw-semibold">{job.experience || '不限'}</div>
                <small className="text-muted">經驗要求</small>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="d-flex align-items-center">
              <i className="lucide-graduation-cap text-info me-2"></i>
              <div>
                <div className="fw-semibold">{job.education || '不限'}</div>
                <small className="text-muted">學歷要求</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 技能標籤 -->
      <div className="skills-tags">
        <div className="d-flex flex-wrap gap-1">
          {job.skills?.slice(0, 8).map((skill, index) => (
            <span key={index} className="badge bg-light text-dark border">
              {skill}
            </span>
          ))}
          {job.skills?.length > 8 && (
            <span className="badge bg-secondary">+{job.skills.length - 8} 更多</span>
          )}
        </div>
      </div>
    </div>
  </div>
  
  <!-- 統計資訊 -->
  <div className="job-stats mt-3 pt-3 border-top">
    <div className="row text-center">
      <div className="col-3">
        <div className="stat-item">
          <div className="h6 mb-0 text-primary">{job.views || 0}</div>
          <small className="text-muted">瀏覽次數</small>
        </div>
      </div>
      <div className="col-3">
        <div className="stat-item">
          <div className="h6 mb-0 text-success">{job.applications || 0}</div>
          <small className="text-muted">申請人數</small>
        </div>
      </div>
      <div className="col-3">
        <div className="stat-item">
          <div className="h6 mb-0 text-warning">{job.saves || 0}</div>
          <small className="text-muted">收藏次數</small>
        </div>
      </div>
      <div className="col-3">
        <div className="stat-item">
          <div className="h6 mb-0 text-info">{calculateDaysLeft(job.deadline)}</div>
          <small className="text-muted">剩餘天數</small>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 📝 職位詳細內容設計

### 內容標籤導航

```html
<div className="job-content">
  <!-- 標籤導航 -->
  <ul className="nav nav-tabs mb-4" id="jobTabs" role="tablist">
    <li className="nav-item" role="presentation">
      <button 
        className="nav-link active" 
        id="description-tab" 
        data-bs-toggle="tab" 
        data-bs-target="#description" 
        type="button" 
        role="tab"
      >
        <i className="lucide-file-text me-2"></i>
        職位描述
      </button>
    </li>
    <li className="nav-item" role="presentation">
      <button 
        className="nav-link" 
        id="requirements-tab" 
        data-bs-toggle="tab" 
        data-bs-target="#requirements" 
        type="button" 
        role="tab"
      >
        <i className="lucide-check-circle me-2"></i>
        職位要求
      </button>
    </li>
    <li className="nav-item" role="presentation">
      <button 
        className="nav-link" 
        id="benefits-tab" 
        data-bs-toggle="tab" 
        data-bs-target="#benefits" 
        type="button" 
        role="tab"
      >
        <i className="lucide-gift me-2"></i>
        福利待遇
      </button>
    </li>
    <li className="nav-item" role="presentation">
      <button 
        className="nav-link" 
        id="company-tab" 
        data-bs-toggle="tab" 
        data-bs-target="#company" 
        type="button" 
        role="tab"
      >
        <i className="lucide-building me-2"></i>
        公司介紹
      </button>
    </li>
    <li className="nav-item" role="presentation">
      <button 
        className="nav-link" 
        id="reviews-tab" 
        data-bs-toggle="tab" 
        data-bs-target="#reviews" 
        type="button" 
        role="tab"
      >
        <i className="lucide-star me-2"></i>
        評價 ({job.reviews?.length || 0})
      </button>
    </li>
  </ul>
  
  <!-- 標籤內容 -->
  <div className="tab-content" id="jobTabsContent">
    <!-- 職位描述 -->
    <div className="tab-pane fade show active" id="description" role="tabpanel">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">
            <i className="lucide-file-text text-primary me-2"></i>
            工作內容
          </h5>
          <div className="job-description">
            <div dangerouslySetInnerHTML={{ __html: job.description }} />
          </div>
          
          {job.responsibilities && (
            <div className="mt-4">
              <h6 className="mb-3">
                <i className="lucide-list text-primary me-2"></i>
                主要職責
              </h6>
              <ul className="list-unstyled">
                {job.responsibilities.map((responsibility, index) => (
                  <li key={index} className="d-flex align-items-start mb-2">
                    <i className="lucide-check text-success me-2 mt-1" style={{fontSize: '16px'}}></i>
                    <span>{responsibility}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
    
    <!-- 職位要求 -->
    <div className="tab-pane fade" id="requirements" role="tabpanel">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">
            <i className="lucide-check-circle text-primary me-2"></i>
            任職要求
          </h5>
          
          <!-- 基本要求 -->
          <div className="requirements-section mb-4">
            <h6 className="mb-3">基本要求</h6>
            <div className="row g-3">
              <div className="col-md-6">
                <div className="requirement-item p-3 border rounded">
                  <div className="d-flex align-items-center mb-2">
                    <i className="lucide-graduation-cap text-info me-2"></i>
                    <strong>學歷要求</strong>
                  </div>
                  <p className="mb-0 text-muted">{job.education || '不限'}</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="requirement-item p-3 border rounded">
                  <div className="d-flex align-items-center mb-2">
                    <i className="lucide-briefcase text-warning me-2"></i>
                    <strong>工作經驗</strong>
                  </div>
                  <p className="mb-0 text-muted">{job.experience || '不限'}</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="requirement-item p-3 border rounded">
                  <div className="d-flex align-items-center mb-2">
                    <i className="lucide-globe text-success me-2"></i>
                    <strong>語言能力</strong>
                  </div>
                  <p className="mb-0 text-muted">{job.languages?.join(', ') || '中文'}</p>
                </div>
              </div>
              <div className="col-md-6">
                <div className="requirement-item p-3 border rounded">
                  <div className="d-flex align-items-center mb-2">
                    <i className="lucide-map-pin text-danger me-2"></i>
                    <strong>工作地點</strong>
                  </div>
                  <p className="mb-0 text-muted">{job.location}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 技能要求 -->
          {job.requiredSkills && (
            <div className="skills-section mb-4">
              <h6 className="mb-3">技能要求</h6>
              <div className="row">
                <div className="col-md-6">
                  <h6 className="small text-muted mb-2">必備技能</h6>
                  <div className="d-flex flex-wrap gap-1 mb-3">
                    {job.requiredSkills.map((skill, index) => (
                      <span key={index} className="badge bg-danger text-white">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                {job.preferredSkills && (
                  <div className="col-md-6">
                    <h6 className="small text-muted mb-2">加分技能</h6>
                    <div className="d-flex flex-wrap gap-1 mb-3">
                      {job.preferredSkills.map((skill, index) => (
                        <span key={index} className="badge bg-success text-white">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          
          <!-- 其他要求 -->
          {job.additionalRequirements && (
            <div className="additional-requirements">
              <h6 className="mb-3">其他要求</h6>
              <ul className="list-unstyled">
                {job.additionalRequirements.map((requirement, index) => (
                  <li key={index} className="d-flex align-items-start mb-2">
                    <i className="lucide-arrow-right text-primary me-2 mt-1" style={{fontSize: '16px'}}></i>
                    <span>{requirement}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
    
    <!-- 福利待遇 -->
    <div className="tab-pane fade" id="benefits" role="tabpanel">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">
            <i className="lucide-gift text-primary me-2"></i>
            福利待遇
          </h5>
          
          <!-- 薪資福利 -->
          <div className="benefits-section mb-4">
            <h6 className="mb-3">薪資福利</h6>
            <div className="row g-3">
              <div className="col-md-4">
                <div className="benefit-item text-center p-3 border rounded">
                  <i className="lucide-dollar-sign text-success mb-2" style={{fontSize: '2rem'}}></i>
                  <h6>薪資範圍</h6>
                  <p className="text-muted mb-0">
                    {job.salary ? `${job.salary.min} - ${job.salary.max} ${job.salary.currency}` : '面議'}
                  </p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="benefit-item text-center p-3 border rounded">
                  <i className="lucide-calendar text-info mb-2" style={{fontSize: '2rem'}}></i>
                  <h6>年假</h6>
                  <p className="text-muted mb-0">{job.benefits?.vacation || '依法規定'}</p>
                </div>
              </div>
              <div className="col-md-4">
                <div className="benefit-item text-center p-3 border rounded">
                  <i className="lucide-heart text-danger mb-2" style={{fontSize: '2rem'}}></i>
                  <h6>保險</h6>
                  <p className="text-muted mb-0">{job.benefits?.insurance || '勞健保'}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 其他福利 -->
          {job.benefits?.others && (
            <div className="other-benefits">
              <h6 className="mb-3">其他福利</h6>
              <div className="row g-2">
                {job.benefits.others.map((benefit, index) => (
                  <div key={index} className="col-md-6">
                    <div className="d-flex align-items-center p-2 border rounded">
                      <i className="lucide-check-circle text-success me-2"></i>
                      <span>{benefit}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
    
    <!-- 公司介紹 -->
    <div className="tab-pane fade" id="company" role="tabpanel">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <div className="company-header d-flex align-items-center mb-4">
            <img 
              src={job.company.logo} 
              alt={job.company.name}
              className="rounded me-3"
              style={{width: '60px', height: '60px', objectFit: 'cover'}}
            />
            <div>
              <h5 className="mb-1">{job.company.name}</h5>
              <div className="d-flex align-items-center text-muted">
                <span className="me-3">
                  <i className="lucide-users me-1"></i>
                  {job.company.size || '未知'} 人
                </span>
                <span className="me-3">
                  <i className="lucide-building me-1"></i>
                  {job.company.industry || '未知行業'}
                </span>
                <span>
                  <i className="lucide-calendar me-1"></i>
                  成立於 {job.company.founded || '未知'}
                </span>
              </div>
            </div>
          </div>
          
          <div className="company-description mb-4">
            <h6 className="mb-3">公司簡介</h6>
            <p className="text-muted">{job.company.description}</p>
          </div>
          
          {job.company.culture && (
            <div className="company-culture mb-4">
              <h6 className="mb-3">企業文化</h6>
              <p className="text-muted">{job.company.culture}</p>
            </div>
          )}
          
          <div className="company-stats">
            <h6 className="mb-3">公司統計</h6>
            <div className="row g-3">
              <div className="col-md-3">
                <div className="stat-item text-center p-3 border rounded">
                  <div className="h5 mb-1 text-primary">{job.company.openPositions || 0}</div>
                  <small className="text-muted">開放職位</small>
                </div>
              </div>
              <div className="col-md-3">
                <div className="stat-item text-center p-3 border rounded">
                  <div className="h5 mb-1 text-success">{job.company.rating || 'N/A'}</div>
                  <small className="text-muted">公司評分</small>
                </div>
              </div>
              <div className="col-md-3">
                <div className="stat-item text-center p-3 border rounded">
                  <div className="h5 mb-1 text-warning">{job.company.reviews || 0}</div>
                  <small className="text-muted">評價數量</small>
                </div>
              </div>
              <div className="col-md-3">
                <div className="stat-item text-center p-3 border rounded">
                  <div className="h5 mb-1 text-info">{job.company.followers || 0}</div>
                  <small className="text-muted">關注人數</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 評價 -->
    <div className="tab-pane fade" id="reviews" role="tabpanel">
      <div className="card border-0 shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">
            <i className="lucide-star text-primary me-2"></i>
            員工評價
          </h5>
          
          {job.reviews && job.reviews.length > 0 ? (
            <div className="reviews-list">
              {job.reviews.map((review, index) => (
                <div key={index} className="review-item border-bottom pb-3 mb-3">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div className="d-flex align-items-center">
                      <div className="avatar-placeholder bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style={{width: '40px', height: '40px'}}>
                        {review.author.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <h6 className="mb-0">{review.author}</h6>
                        <small className="text-muted">{review.position} • {formatDate(review.date)}</small>
                      </div>
                    </div>
                    <div className="rating">
                      {[...Array(5)].map((_, i) => (
                        <i 
                          key={i} 
                          className={`lucide-star ${i < review.rating ? 'text-warning' : 'text-muted'}`}
                          style={{fontSize: '14px'}}
                        ></i>
                      ))}
                    </div>
                  </div>
                  <p className="text-muted mb-0">{review.content}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <i className="lucide-message-circle text-muted mb-3" style={{fontSize: '3rem'}}></i>
              <h6 className="text-muted">暫無評價</h6>
              <p className="text-muted">成為第一個評價這個職位的人</p>
            </div>
          )}
        </div>
      </div>
    </div>
  </div>
</div>
```