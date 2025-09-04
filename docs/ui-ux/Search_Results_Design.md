# JobSpy v2 - 搜尋結果頁面設計

## 🎯 設計目標

### 核心目標
- **高效搜尋**: 提供快速、準確的職位搜尋結果
- **智能篩選**: 多維度篩選條件，精準匹配用戶需求
- **結果展示**: 清晰、易讀的職位資訊展示
- **用戶體驗**: 流暢的瀏覽和互動體驗
- **個人化**: 基於用戶偏好的智能推薦

### 用戶需求
- 快速找到符合條件的職位
- 方便比較不同職位
- 保存感興趣的職位
- 直接申請心儀職位
- 獲得相關職位推薦

## 🛠️ 技術要求

### 前端技術棧
- **React 18** + **TypeScript** - 現代化前端框架
- **Bootstrap 5** - 響應式 UI 框架
- **Lucide React** - 一致的圖標系統
- **React Hook Form** + **Zod** - 表單處理和驗證
- **TanStack Query** - 數據獲取和狀態管理
- **Zustand** - 輕量級狀態管理
- **i18next** - 國際化支持
- **React Router** - 路由管理
- **React Virtualized** - 大量數據虛擬化

### 性能要求
- 搜尋響應時間 < 500ms
- 頁面載入時間 < 2s
- 支援無限滾動載入
- 搜尋結果快取機制

## 🎨 整體佈局設計

### 頁面結構
```html
<div className="search-results-page">
  <!-- 頂部導航 -->
  <nav className="navbar sticky-top">
    <!-- 導航內容 -->
  </nav>
  
  <!-- 搜尋區域 -->
  <section className="search-section bg-light py-3">
    <div className="container">
      <!-- 搜尋表單 -->
      <!-- 快速篩選標籤 -->
    </div>
  </section>
  
  <!-- 主要內容 -->
  <div className="container py-4">
    <div className="row">
      <!-- 左側篩選器 -->
      <div className="col-lg-3">
        <!-- 篩選面板 -->
      </div>
      
      <!-- 右側結果區域 -->
      <div className="col-lg-9">
        <!-- 結果統計和排序 -->
        <!-- 職位列表 -->
        <!-- 分頁/載入更多 -->
      </div>
    </div>
  </div>
</div>
```

### 網格檢視模式
```html
<div className="jobs-grid">
  <div className="row g-4">
    {jobs.map((job, index) => (
      <div key={job.id} className="col-lg-6 col-xl-4">
        <div className="job-card-grid card h-100 border-0 shadow-sm hover-lift">
          <div className="card-body d-flex flex-column">
            <!-- 公司 Logo 和基本資訊 -->
            <div className="d-flex align-items-center mb-3">
              <img 
                src={job.company.logo} 
                alt={job.company.name}
                className="rounded me-3"
                style={{width: '40px', height: '40px', objectFit: 'cover'}}
                onError={(e) => {
                  e.target.src = '/default-company-logo.svg';
                }}
              />
              <div className="flex-grow-1 min-width-0">
                <h6 className="company-name mb-0 text-truncate">
                  <a href={`/company/${job.company.id}`} className="text-decoration-none text-muted hover-primary">
                    {job.company.name}
                  </a>
                </h6>
                <small className="text-muted">
                  <i className="lucide-map-pin me-1" style={{fontSize: '12px'}}></i>
                  {job.location}
                </small>
              </div>
            </div>
            
            <!-- 職位標題 -->
            <h5 className="job-title mb-2">
              <a 
                href={`/jobs/${job.id}`} 
                className="text-decoration-none text-dark hover-primary"
              >
                {job.title}
              </a>
            </h5>
            
            <!-- 職位標籤 -->
            <div className="job-badges mb-3">
              {job.isNew && <span className="badge bg-success me-1">新職位</span>}
              {job.isUrgent && <span className="badge bg-warning me-1">急徵</span>}
              {job.isRemote && <span className="badge bg-info me-1">遠端</span>}
              <span className="badge bg-light text-dark">{job.employmentType}</span>
            </div>
            
            <!-- 職位描述 -->
            <p className="job-description text-muted small mb-3 flex-grow-1">
              {job.description.substring(0, 100)}...
            </p>
            
            <!-- 技能標籤 -->
            <div className="skills-tags mb-3">
              {job.skills.slice(0, 3).map((skill, skillIndex) => (
                <span key={skillIndex} className="badge bg-light text-dark me-1 mb-1 small">
                  {skill}
                </span>
              ))}
              {job.skills.length > 3 && (
                <span className="badge bg-light text-muted small">+{job.skills.length - 3}</span>
              )}
            </div>
            
            <!-- 薪資資訊 -->
            <div className="salary-info mb-3">
              {job.salary ? (
                <div className="text-success fw-bold">
                  NT$ {job.salary.min.toLocaleString()} - {job.salary.max.toLocaleString()}
                </div>
              ) : (
                <div className="text-muted">薪資面議</div>
              )}
            </div>
            
            <!-- 操作按鈕 -->
            <div className="job-actions mt-auto">
              <div className="d-grid gap-2">
                {user?.appliedJobs?.includes(job.id) ? (
                  <button className="btn btn-success btn-sm" disabled>
                    <i className="lucide-check me-1" style={{fontSize: '12px'}}></i>
                    已申請
                  </button>
                ) : (
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => handleQuickApply(job.id)}
                  >
                    <i className="lucide-send me-1" style={{fontSize: '12px'}}></i>
                    快速申請
                  </button>
                )}
                
                <div className="row g-1">
                  <div className="col-6">
                    <button 
                      className={`btn btn-sm w-100 ${
                        user?.savedJobs?.includes(job.id) 
                          ? 'btn-warning' 
                          : 'btn-outline-warning'
                      }`}
                      onClick={() => handleSaveJob(job.id)}
                    >
                      <i className={`lucide-heart ${user?.savedJobs?.includes(job.id) ? 'fill' : ''}`} style={{fontSize: '12px'}}></i>
                    </button>
                  </div>
                  <div className="col-6">
                    <button 
                      className="btn btn-outline-secondary btn-sm w-100"
                      onClick={() => handleShareJob(job)}
                    >
                      <i className="lucide-share-2" style={{fontSize: '12px'}}></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 職位統計 -->
            <div className="job-stats small text-muted mt-2 pt-2 border-top">
              <div className="d-flex justify-content-between">
                <span>
                  <i className="lucide-eye me-1" style={{fontSize: '10px'}}></i>
                  {job.views || 0}
                </span>
                <span>
                  <i className="lucide-users me-1" style={{fontSize: '10px'}}></i>
                  {job.applications || 0}
                </span>
                <span>
                  <i className="lucide-calendar me-1" style={{fontSize: '10px'}}></i>
                  {formatDate(job.publishedAt)}
                </span>
              </div>
            </div>
            
            <!-- 匹配度 -->
            {user && job.matchScore && (
              <div className="match-score mt-2">
                <div className="d-flex align-items-center">
                  <small className="text-muted me-2">匹配度</small>
                  <div className="progress flex-grow-1" style={{height: '4px'}}>
                    <div 
                      className={`progress-bar ${
                        job.matchScore >= 80 ? 'bg-success' :
                        job.matchScore >= 60 ? 'bg-warning' : 'bg-danger'
                      }`}
                      style={{width: `${job.matchScore}%`}}
                    ></div>
                  </div>
                  <small className="text-muted ms-2">{job.matchScore}%</small>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
```

## 📄 分頁和載入更多

### 無限滾動載入
```html
<div className="load-more-section py-4">
  {hasNextPage ? (
    <div className="text-center">
      {isLoadingMore ? (
        <div className="loading-more">
          <div className="spinner-border text-primary me-2" role="status">
            <span className="visually-hidden">載入中...</span>
          </div>
          <span className="text-muted">載入更多職位中...</span>
        </div>
      ) : (
        <button 
          className="btn btn-outline-primary"
          onClick={loadMoreJobs}
        >
          <i className="lucide-plus me-2"></i>
          載入更多職位
        </button>
      )}
    </div>
  ) : jobs.length > 0 ? (
    <div className="text-center text-muted">
      <i className="lucide-check-circle me-2"></i>
      已顯示全部 {totalResults} 個職位
    </div>
  ) : null}
</div>
```

### 傳統分頁
```html
<nav aria-label="搜尋結果分頁" className="mt-4">
  <ul className="pagination justify-content-center">
    <!-- 上一頁 -->
    <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
      <button 
        className="page-link"
        onClick={() => goToPage(currentPage - 1)}
        disabled={currentPage === 1}
      >
        <i className="lucide-chevron-left"></i>
        <span className="d-none d-sm-inline ms-1">上一頁</span>
      </button>
    </li>
    
    <!-- 頁碼 -->
    {getPageNumbers().map((pageNum, index) => (
      pageNum === '...' ? (
        <li key={index} className="page-item disabled">
          <span className="page-link">...</span>
        </li>
      ) : (
        <li key={index} className={`page-item ${currentPage === pageNum ? 'active' : ''}`}>
          <button 
            className="page-link"
            onClick={() => goToPage(pageNum)}
          >
            {pageNum}
          </button>
        </li>
      )
    ))}
    
    <!-- 下一頁 -->
    <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
      <button 
        className="page-link"
        onClick={() => goToPage(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        <span className="d-none d-sm-inline me-1">下一頁</span>
        <i className="lucide-chevron-right"></i>
      </button>
    </li>
  </ul>
  
  <!-- 分頁資訊 -->
  <div className="text-center mt-2">
    <small className="text-muted">
      第 {((currentPage - 1) * perPage) + 1} - {Math.min(currentPage * perPage, totalResults)} 個，
      共 {totalResults} 個職位
    </small>
  </div>
</nav>
```

## 📱 響應式設計

### 移動端適配
```css
/* 移動端樣式 */
@media (max-width: 768px) {
  .search-results-page {
    padding: 0;
  }
  
  .search-section {
    padding: 1rem 0;
  }
  
  .search-form .row {
    --bs-gutter-x: 0.5rem;
  }
  
  .search-form .col-md-4,
  .search-form .col-md-3,
  .search-form .col-md-2 {
    margin-bottom: 0.5rem;
  }
  
  .quick-filters {
    overflow-x: auto;
    white-space: nowrap;
    padding-bottom: 0.5rem;
  }
  
  .quick-filters .btn {
    flex-shrink: 0;
  }
  
  /* 隱藏左側篩選面板，改為抽屜式 */
  .filters-panel {
    position: fixed;
    top: 0;
    left: -100%;
    width: 280px;
    height: 100vh;
    background: white;
    z-index: 1050;
    transition: left 0.3s ease;
    overflow-y: auto;
    padding: 1rem;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }
  
  .filters-panel.show {
    left: 0;
  }
  
  .filters-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1040;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
  }
  
  .filters-overlay.show {
    opacity: 1;
    visibility: visible;
  }
  
  /* 移動端篩選按鈕 */
  .mobile-filter-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1030;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .results-header .row {
    flex-direction: column;
  }
  
  .results-header .col-md-6:last-child {
    margin-top: 1rem;
  }
  
  .job-card .row {
    flex-direction: column;
  }
  
  .job-card .col-md-4 {
    margin-top: 1rem;
    text-align: left !important;
  }
  
  .job-actions .row {
    flex-direction: row;
  }
  
  /* 網格檢視在移動端改為單列 */
  .jobs-grid .col-lg-6,
  .jobs-grid .col-xl-4 {
    flex: 0 0 100%;
    max-width: 100%;
  }
  
  .pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination .page-item {
    margin: 0.125rem;
  }
}

/* 平板端適配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .filters-panel {
    position: sticky;
    top: 100px;
  }
  
  .jobs-grid .col-lg-6 {
    flex: 0 0 50%;
    max-width: 50%;
  }
  
  .search-form .row {
    --bs-gutter-x: 1rem;
  }
}

/* 大螢幕優化 */
@media (min-width: 1400px) {
  .container {
    max-width: 1320px;
  }
  
  .jobs-grid .col-xl-4 {
    flex: 0 0 33.333333%;
    max-width: 33.333333%;
  }
}
```

### 移動端篩選抽屜
```html
<!-- 移動端篩選按鈕 -->
<button 
  className="btn btn-primary mobile-filter-btn d-md-none"
  onClick={() => setShowMobileFilters(true)}
>
  <i className="lucide-sliders-horizontal"></i>
  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
    {activeFiltersCount}
  </span>
</button>

<!-- 篩選抽屜遮罩 -->
<div 
  className={`filters-overlay d-md-none ${showMobileFilters ? 'show' : ''}`}
  onClick={() => setShowMobileFilters(false)}
></div>

<!-- 移動端篩選面板 -->
<div className={`filters-panel d-md-none ${showMobileFilters ? 'show' : ''}`}>
  <!-- 抽屜標題 -->
  <div className="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
    <h5 className="mb-0">
      <i className="lucide-filter text-primary me-2"></i>
      篩選條件
    </h5>
    <button 
      className="btn btn-link p-0 text-muted"
      onClick={() => setShowMobileFilters(false)}
    >
      <i className="lucide-x" style={{fontSize: '20px'}}></i>
    </button>
  </div>
  
  <!-- 篩選內容（與桌面版相同） -->
  <!-- ... 篩選器內容 ... -->
  
  <!-- 底部操作按鈕 -->
  <div className="position-sticky bottom-0 bg-white pt-3 border-top mt-4">
    <div className="row g-2">
      <div className="col-6">
        <button 
          className="btn btn-outline-secondary w-100"
          onClick={clearAllFilters}
        >
          清除全部
        </button>
      </div>
      <div className="col-6">
        <button 
          className="btn btn-primary w-100"
          onClick={() => {
            applyFilters();
            setShowMobileFilters(false);
          }}
        >
          查看結果 ({filteredJobsCount})
        </button>
      </div>
    </div>
  </div>
</div>
```

## ⚙️ 技術實現

### 核心組件結構
```typescript
// SearchResults.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useInfiniteQuery } from '@tanstack/react-query';
import { useIntersectionObserver } from '../hooks/useIntersectionObserver';
import { useDebounce } from '../hooks/useDebounce';
import { searchJobsAPI } from '../api/jobs';
import { useSearchStore } from '../stores/searchStore';
import { useUserStore } from '../stores/userStore';

interface SearchResultsProps {
  initialQuery?: string;
}

const SearchResults: React.FC<SearchResultsProps> = ({ initialQuery }) => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // 狀態管理
  const {
    searchQuery,
    filters,
    sortBy,
    viewMode,
    perPage,
    setSearchQuery,
    setFilters,
    setSortBy,
    setViewMode,
    setPerPage,
    clearFilters
  } = useSearchStore();
  
  const { user, saveJob, unsaveJob, applyToJob } = useUserStore();
  
  // 本地狀態
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  
  // 防抖搜尋
  const debouncedQuery = useDebounce(searchQuery, 300);
  
  // 無限查詢
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error,
    refetch
  } = useInfiniteQuery({
    queryKey: ['searchJobs', debouncedQuery, filters, sortBy],
    queryFn: ({ pageParam = 1 }) => searchJobsAPI({
      ...debouncedQuery,
      ...filters,
      sortBy,
      page: pageParam,
      limit: perPage
    }),
    getNextPageParam: (lastPage) => {
      return lastPage.hasNextPage ? lastPage.page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000, // 5分鐘
    cacheTime: 10 * 60 * 1000, // 10分鐘
  });
  
  // 無限滾動
  const { ref: loadMoreRef } = useIntersectionObserver({
    onIntersect: () => {
      if (hasNextPage && !isFetchingNextPage) {
        fetchNextPage();
      }
    },
    threshold: 0.1
  });
  
  // 扁平化職位數據
  const jobs = data?.pages.flatMap(page => page.jobs) || [];
  const totalResults = data?.pages[0]?.total || 0;
  
  // 初始化搜尋參數
  useEffect(() => {
    const params = Object.fromEntries(searchParams);
    if (params.q) {
      setSearchQuery({ ...searchQuery, keyword: params.q });
    }
    if (params.location) {
      setSearchQuery({ ...searchQuery, location: params.location });
    }
    if (params.salary) {
      setSearchQuery({ ...searchQuery, salary: params.salary });
    }
  }, []);
  
  // 更新 URL 參數
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery.keyword) params.set('q', searchQuery.keyword);
    if (searchQuery.location) params.set('location', searchQuery.location);
    if (searchQuery.salary) params.set('salary', searchQuery.salary);
    if (sortBy !== 'relevance') params.set('sort', sortBy);
    
    setSearchParams(params, { replace: true });
  }, [searchQuery, sortBy, setSearchParams]);
  
  // 搜尋處理
  const handleSearch = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    refetch();
  }, [refetch]);
  
  // 快速申請
  const handleQuickApply = useCallback(async (jobId: string) => {
    if (!user) {
      navigate('/login', { state: { returnTo: `/jobs/${jobId}` } });
      return;
    }
    
    try {
      await applyToJob(jobId);
      // 顯示成功提示
    } catch (error) {
      // 顯示錯誤提示
    }
  }, [user, navigate, applyToJob]);
  
  // 保存職位
  const handleSaveJob = useCallback(async (jobId: string) => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    try {
      if (user.savedJobs?.includes(jobId)) {
        await unsaveJob(jobId);
      } else {
        await saveJob(jobId);
      }
    } catch (error) {
      // 顯示錯誤提示
    }
  }, [user, navigate, saveJob, unsaveJob]);
  
  // 分享職位
  const handleShareJob = useCallback((job: Job) => {
    if (navigator.share) {
      navigator.share({
        title: job.title,
        text: `${job.company.name} - ${job.title}`,
        url: `${window.location.origin}/jobs/${job.id}`
      });
    } else {
      // 複製到剪貼板
      navigator.clipboard.writeText(`${window.location.origin}/jobs/${job.id}`);
    }
  }, []);
  
  return (
    <div className="search-results-page">
      {/* 搜尋區域 */}
      <SearchSection 
        searchQuery={searchQuery}
        onSearchQueryChange={setSearchQuery}
        onSearch={handleSearch}
        isLoading={isLoading}
        showAdvancedFilters={showAdvancedFilters}
        onToggleAdvancedFilters={setShowAdvancedFilters}
      />
      
      <div className="container py-4">
        <div className="row">
          {/* 左側篩選面板 */}
          <div className="col-lg-3 d-none d-lg-block">
            <FiltersPanel 
              filters={filters}
              onFiltersChange={setFilters}
              onClearFilters={clearFilters}
              totalResults={totalResults}
            />
          </div>
          
          {/* 右側結果區域 */}
          <div className="col-lg-9">
            {/* 結果統計和排序 */}
            <ResultsHeader 
              totalResults={totalResults}
              searchQuery={searchQuery}
              filters={filters}
              sortBy={sortBy}
              onSortChange={setSortBy}
              viewMode={viewMode}
              onViewModeChange={setViewMode}
              perPage={perPage}
              onPerPageChange={setPerPage}
              isLoading={isLoading}
            />
            
            {/* 職位列表 */}
            {isError ? (
              <ErrorState error={error} onRetry={refetch} />
            ) : (
              <JobsList 
                jobs={jobs}
                viewMode={viewMode}
                isLoading={isLoading}
                user={user}
                onQuickApply={handleQuickApply}
                onSaveJob={handleSaveJob}
                onShareJob={handleShareJob}
              />
            )}
            
            {/* 載入更多 */}
            {hasNextPage && (
              <div ref={loadMoreRef} className="load-more-section py-4">
                <LoadMoreButton 
                  isLoading={isFetchingNextPage}
                  onClick={() => fetchNextPage()}
                />
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* 移動端篩選 */}
      <MobileFilters 
        show={showMobileFilters}
        onClose={() => setShowMobileFilters(false)}
        filters={filters}
        onFiltersChange={setFilters}
        onClearFilters={clearFilters}
        totalResults={totalResults}
      />
      
      {/* 移動端篩選按鈕 */}
      <MobileFilterButton 
        onClick={() => setShowMobileFilters(true)}
        activeFiltersCount={Object.values(filters).flat().length}
      />
    </div>
  );
};

export default SearchResults;
```

### 狀態管理
```typescript
// stores/searchStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SearchQuery {
  keyword: string;
  location: string;
  salary: string;
}

interface SearchFilters {
  jobTypes: string[];
  experience: string;
  companySizes: string[];
  skills: string[];
  workTypes: string[];
  publishedTime: string;
  salaryRange: {
    min: number;
    max: number;
  };
}

interface SearchStore {
  // 搜尋狀態
  searchQuery: SearchQuery;
  filters: SearchFilters;
  sortBy: string;
  viewMode: 'list' | 'grid';
  perPage: number;
  
  // 搜尋歷史
  searchHistory: string[];
  
  // 動作
  setSearchQuery: (query: Partial<SearchQuery>) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  setSortBy: (sortBy: string) => void;
  setViewMode: (viewMode: 'list' | 'grid') => void;
  setPerPage: (perPage: number) => void;
  clearFilters: () => void;
  addToSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
}

const initialSearchQuery: SearchQuery = {
  keyword: '',
  location: '',
  salary: ''
};

const initialFilters: SearchFilters = {
  jobTypes: [],
  experience: '',
  companySizes: [],
  skills: [],
  workTypes: [],
  publishedTime: '',
  salaryRange: {
    min: 20000,
    max: 200000
  }
};

export const useSearchStore = create<SearchStore>()(
  persist(
    (set, get) => ({
      // 初始狀態
      searchQuery: initialSearchQuery,
      filters: initialFilters,
      sortBy: 'relevance',
      viewMode: 'list',
      perPage: 20,
      searchHistory: [],
      
      // 動作實現
      setSearchQuery: (query) => {
        set((state) => ({
          searchQuery: { ...state.searchQuery, ...query }
        }));
      },
      
      setFilters: (newFilters) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters }
        }));
      },
      
      setSortBy: (sortBy) => {
        set({ sortBy });
      },
      
      setViewMode: (viewMode) => {
        set({ viewMode });
      },
      
      setPerPage: (perPage) => {
        set({ perPage });
      },
      
      clearFilters: () => {
        set({
          searchQuery: initialSearchQuery,
          filters: initialFilters
        });
      },
      
      addToSearchHistory: (query) => {
        if (!query.trim()) return;
        
        set((state) => {
          const newHistory = [query, ...state.searchHistory.filter(h => h !== query)].slice(0, 10);
          return { searchHistory: newHistory };
        });
      },
      
      clearSearchHistory: () => {
        set({ searchHistory: [] });
      }
    }),
    {
      name: 'jobspy-search-store',
      partialize: (state) => ({
        viewMode: state.viewMode,
        perPage: state.perPage,
        searchHistory: state.searchHistory
      })
    }
  )
);
```

### API 整合
```typescript
// api/jobs.ts
import { apiClient } from './client';

export interface SearchJobsParams {
  keyword?: string;
  location?: string;
  salary?: string;
  jobTypes?: string[];
  experience?: string;
  companySizes?: string[];
  skills?: string[];
  workTypes?: string[];
  publishedTime?: string;
  salaryRange?: {
    min: number;
    max: number;
  };
  sortBy?: string;
  page?: number;
  limit?: number;
}

export interface SearchJobsResponse {
  jobs: Job[];
  total: number;
  page: number;
  limit: number;
  hasNextPage: boolean;
  filters: {
    jobTypes: FilterOption[];
    companySizes: FilterOption[];
    skills: FilterOption[];
    workTypes: FilterOption[];
    locations: FilterOption[];
  };
}

export interface FilterOption {
  value: string;
  label: string;
  count: number;
}

export interface Job {
  id: string;
  title: string;
  description: string;
  company: {
    id: string;
    name: string;
    logo: string;
    size: string;
    industry: string;
  };
  location: string;
  employmentType: string;
  salary?: {
    min: number;
    max: number;
    currency: string;
  };
  skills: string[];
  requirements: string[];
  benefits: string[];
  publishedAt: string;
  updatedAt: string;
  views: number;
  applications: number;
  isNew: boolean;
  isUrgent: boolean;
  isRemote: boolean;
  matchScore?: number;
}

/**
 * 搜尋職位
 */
export const searchJobsAPI = async (params: SearchJobsParams): Promise<SearchJobsResponse> => {
  const response = await apiClient.get('/jobs/search', {
    params: {
      ...params,
      jobTypes: params.jobTypes?.join(','),
      companySizes: params.companySizes?.join(','),
      skills: params.skills?.join(','),
      workTypes: params.workTypes?.join(','),
      salaryMin: params.salaryRange?.min,
      salaryMax: params.salaryRange?.max
    }
  });
  
  return response.data;
};

/**
 * 獲取搜尋建議
 */
export const getSearchSuggestionsAPI = async (query: string): Promise<string[]> => {
  const response = await apiClient.get('/jobs/search/suggestions', {
    params: { q: query }
  });
  
  return response.data.suggestions;
};

/**
 * 獲取熱門搜尋關鍵字
 */
export const getPopularKeywordsAPI = async (): Promise<string[]> => {
  const response = await apiClient.get('/jobs/search/popular-keywords');
  
  return response.data.keywords;
};

/**
 * 獲取篩選器選項
 */
export const getFilterOptionsAPI = async (): Promise<{
  jobTypes: FilterOption[];
  companySizes: FilterOption[];
  skills: FilterOption[];
  workTypes: FilterOption[];
  locations: FilterOption[];
}> => {
  const response = await apiClient.get('/jobs/filters');
  
  return response.data;
};
```

### 自訂 Hooks
```typescript
// hooks/useDebounce.ts
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// hooks/useIntersectionObserver.ts
import { useEffect, useRef } from 'react';

interface UseIntersectionObserverProps {
  onIntersect: () => void;
  threshold?: number;
  rootMargin?: string;
}

export function useIntersectionObserver({
  onIntersect,
  threshold = 0,
  rootMargin = '0px'
}: UseIntersectionObserverProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          onIntersect();
        }
      },
      { threshold, rootMargin }
    );

    observer.observe(element);

    return () => {
      observer.unobserve(element);
    };
  }, [onIntersect, threshold, rootMargin]);

  return { ref };
}

// hooks/useLocalStorage.ts
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue] as const;
}
```

## 🧪 測試策略

### 單元測試
```typescript
// __tests__/SearchResults.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import SearchResults from '../SearchResults';
import { useSearchStore } from '../stores/searchStore';

// Mock API
jest.mock('../api/jobs', () => ({
  searchJobsAPI: jest.fn(),
  getFilterOptionsAPI: jest.fn()
}));

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false }
    }
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

describe('SearchResults', () => {
  beforeEach(() => {
    // 重置 store
    useSearchStore.getState().clearFilters();
  });

  test('renders search form correctly', () => {
    renderWithProviders(<SearchResults />);
    
    expect(screen.getByPlaceholderText(/職位關鍵字/)).toBeInTheDocument();
    expect(screen.getByDisplayValue(/全台灣/)).toBeInTheDocument();
    expect(screen.getByText(/搜尋職位/)).toBeInTheDocument();
  });

  test('handles search input changes', async () => {
    renderWithProviders(<SearchResults />);
    
    const keywordInput = screen.getByPlaceholderText(/職位關鍵字/);
    fireEvent.change(keywordInput, { target: { value: 'React Developer' } });
    
    await waitFor(() => {
      expect(useSearchStore.getState().searchQuery.keyword).toBe('React Developer');
    });
  });

  test('applies filters correctly', async () => {
    renderWithProviders(<SearchResults />);
    
    // 測試職位類型篩選
    const frontendFilter = screen.getByLabelText(/前端工程師/);
    fireEvent.click(frontendFilter);
    
    await waitFor(() => {
      expect(useSearchStore.getState().filters.jobTypes).toContain('frontend');
    });
  });

  test('switches between list and grid view', () => {
    renderWithProviders(<SearchResults />);
    
    const gridViewButton = screen.getByLabelText(/網格檢視/);
    fireEvent.click(gridViewButton);
    
    expect(useSearchStore.getState().viewMode).toBe('grid');
  });

  test('handles mobile filter drawer', () => {
    // 模擬移動端
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    });
    
    renderWithProviders(<SearchResults />);
    
    const filterButton = screen.getByRole('button', { name: /篩選/ });
    fireEvent.click(filterButton);
    
    expect(screen.getByText(/篩選條件/)).toBeVisible();
  });
});
```

### E2E 測試
```typescript
// e2e/search-results.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Search Results Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search');
  });

  test('should perform basic job search', async ({ page }) => {
    // 輸入搜尋關鍵字
    await page.fill('[placeholder*="職位關鍵字"]', 'React Developer');
    
    // 選擇地點
    await page.selectOption('select[name="location"]', 'taipei');
    
    // 點擊搜尋
    await page.click('button:has-text("搜尋職位")');
    
    // 等待結果載入
    await page.waitForSelector('.job-card');
    
    // 驗證結果
    await expect(page.locator('.results-info')).toContainText('找到');
    await expect(page.locator('.job-card')).toHaveCount.greaterThan(0);
  });

  test('should apply and remove filters', async ({ page }) => {
    // 選擇職位類型篩選
    await page.check('input[id*="jobType-frontend"]');
    
    // 等待結果更新
    await page.waitForResponse('**/jobs/search**');
    
    // 驗證篩選標籤出現
    await expect(page.locator('.badge:has-text("前端工程師")')).toBeVisible();
    
    // 清除篩選
    await page.click('button:has-text("清除全部")');
    
    // 驗證篩選標籤消失
    await expect(page.locator('.badge:has-text("前端工程師")')).not.toBeVisible();
  });

  test('should switch between list and grid view', async ({ page }) => {
    // 等待職位載入
    await page.waitForSelector('.job-card');
    
    // 切換到網格檢視
    await page.click('label[for="gridView"]');
    
    // 驗證網格佈局
    await expect(page.locator('.jobs-grid')).toBeVisible();
    await expect(page.locator('.job-card-grid')).toHaveCount.greaterThan(0);
    
    // 切換回列表檢視
    await page.click('label[for="listView"]');
    
    // 驗證列表佈局
    await expect(page.locator('.jobs-list')).toBeVisible();
  });

  test('should handle infinite scroll', async ({ page }) => {
    // 等待初始結果載入
    await page.waitForSelector('.job-card');
    
    const initialJobCount = await page.locator('.job-card').count();
    
    // 滾動到頁面底部
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    
    // 等待更多職位載入
    await page.waitForFunction(
      (count) => document.querySelectorAll('.job-card').length > count,
      initialJobCount
    );
    
    const newJobCount = await page.locator('.job-card').count();
    expect(newJobCount).toBeGreaterThan(initialJobCount);
  });

  test('should work on mobile devices', async ({ page }) => {
    // 設定移動端視窗
    await page.setViewportSize({ width: 375, height: 667 });
    
    // 驗證移動端篩選按鈕存在
    await expect(page.locator('.mobile-filter-btn')).toBeVisible();
    
    // 點擊篩選按鈕
    await page.click('.mobile-filter-btn');
    
    // 驗證篩選抽屜打開
    await expect(page.locator('.filters-panel.show')).toBeVisible();
    
    // 關閉篩選抽屜
    await page.click('.filters-overlay');
    
    // 驗證篩選抽屜關閉
    await expect(page.locator('.filters-panel.show')).not.toBeVisible();
  });

  test('should save and apply jobs', async ({ page }) => {
    // 登入用戶
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // 回到搜尋頁面
    await page.goto('/search');
    await page.waitForSelector('.job-card');
    
    // 保存第一個職位
    await page.click('.job-card:first-child .btn-outline-warning');
    
    // 驗證保存狀態
    await expect(page.locator('.job-card:first-child .btn-warning')).toBeVisible();
    
    // 申請職位
    await page.click('.job-card:first-child .btn-primary:has-text("快速申請")');
    
    // 驗證申請狀態
    await expect(page.locator('.job-card:first-child .btn-success:has-text("已申請")')).toBeVisible();
  });
});
```

## 📋 分階段實施計劃

### 第一階段：基礎功能 (2-3 週)
- **搜尋表單實現**
  - 關鍵字、地點、薪資搜尋
  - 基本表單驗證
  - 搜尋歷史記錄

- **基礎篩選器**
  - 職位類型篩選
  - 工作經驗篩選
  - 發布時間篩選

- **職位列表展示**
  - 列表檢視模式
  - 基本職位資訊展示
  - 分頁功能

- **響應式基礎**
  - 移動端基本適配
  - 平板端佈局調整

### 第二階段：進階功能 (2-3 週)
- **進階篩選器**
  - 薪資範圍滑桿
  - 技能標籤篩選
  - 公司規模篩選
  - 工作性質篩選

- **網格檢視模式**
  - 網格佈局實現
  - 檢視模式切換
  - 卡片式設計

- **無限滾動**
  - 無限滾動載入
  - 載入狀態處理
  - 性能優化

- **移動端優化**
  - 篩選抽屜實現
  - 觸控手勢支援
  - 移動端專用 UI

### 第三階段：智能功能 (2-3 週)
- **智能推薦**
  - 個人化職位推薦
  - 匹配度計算
  - 相關職位推薦

- **搜尋優化**
  - 搜尋建議
  - 自動完成
  - 拼寫檢查

- **用戶互動**
  - 職位保存功能
  - 快速申請
  - 分享功能

- **數據分析**
  - 搜尋行為追蹤
  - 點擊率統計
  - 轉換率分析

### 第四階段：優化整合 (1-2 週)
- **性能優化**
  - 虛擬化列表
  - 圖片懶載入
  - 快取策略優化

- **用戶體驗優化**
  - 載入狀態優化
  - 錯誤處理改進
  - 無障礙功能完善

- **測試和部署**
  - 單元測試完善
  - E2E 測試覆蓋
  - 性能測試
  - 生產環境部署

## 📊 成功指標

### 用戶體驗指標
- **搜尋效率**
  - 平均搜尋時間 < 3 秒
  - 搜尋成功率 > 95%
  - 零結果搜尋率 < 10%

- **用戶參與度**
  - 平均頁面停留時間 > 2 分鐘
  - 職位點擊率 > 15%
  - 篩選器使用率 > 60%

- **轉換率**
  - 搜尋到申請轉換率 > 8%
  - 職位保存率 > 20%
  - 重複搜尋率 > 40%

### 技術指標
- **性能指標**
  - 頁面載入時間 < 2 秒
  - 搜尋響應時間 < 500ms
  - 無限滾動載入時間 < 1 秒

- **穩定性指標**
  - 系統可用性 > 99.9%
  - 錯誤率 < 0.1%
  - API 響應成功率 > 99.5%

- **相容性指標**
  - 移動端相容性 > 95%
  - 瀏覽器相容性覆蓋率 > 98%
  - 無障礙標準符合率 > 90%

### 業務指標
- **搜尋量增長**
  - 月搜尋量增長 > 20%
  - 活躍搜尋用戶增長 > 15%
  - 搜尋深度提升 > 25%

- **用戶滿意度**
  - 用戶滿意度評分 > 4.5/5
  - 功能使用滿意度 > 85%
  - 推薦意願 > 80%

## 🔄 維護和優化

### 持續優化
- **A/B 測試**
  - 搜尋結果排序算法
  - 篩選器佈局優化
  - 職位卡片設計改進

- **用戶反饋收集**
  - 搜尋體驗調查
  - 功能使用情況分析
  - 改進建議收集

- **性能監控**
  - 實時性能監控
  - 錯誤日誌分析
  - 用戶行為追蹤

### 未來功能擴展
- **AI 智能搜尋**
  - 自然語言搜尋
  - 智能查詢理解
  - 個人化排序

- **進階篩選**
  - 地圖式地點篩選
  - 通勤時間篩選
  - 公司文化匹配

- **社交功能**
  - 職位分享到社交媒體
  - 同事推薦職位
  - 求職社群功能
```

### 色彩方案
```css
:root {
  /* 主色調 */
  --primary-color: #2563eb;
  --primary-hover: #1d4ed8;
  --primary-light: #dbeafe;
  
  /* 輔助色 */
  --success-color: #059669;
  --warning-color: #d97706;
  --danger-color: #dc2626;
  --info-color: #0891b2;
  
  /* 中性色 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-accent: #f1f5f9;
  
  /* 邊框和陰影 */
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

## 🔍 搜尋區域設計

### 搜尋表單
```html
<div className="search-form-container">
  <form className="search-form" onSubmit={handleSearch}>
    <div className="row g-3 align-items-end">
      <!-- 關鍵字搜尋 -->
      <div className="col-md-4">
        <label className="form-label small text-muted">職位關鍵字</label>
        <div className="input-group">
          <span className="input-group-text bg-white border-end-0">
            <i className="lucide-search text-muted"></i>
          </span>
          <input 
            type="text" 
            className="form-control border-start-0 ps-0"
            placeholder="例如：前端工程師、React、TypeScript"
            value={searchQuery.keyword}
            onChange={(e) => setSearchQuery({...searchQuery, keyword: e.target.value})}
          />
          {searchQuery.keyword && (
            <button 
              type="button" 
              className="btn btn-link position-absolute end-0 top-50 translate-middle-y me-2 p-1"
              onClick={() => setSearchQuery({...searchQuery, keyword: ''})}
              style={{zIndex: 10}}
            >
              <i className="lucide-x text-muted" style={{fontSize: '14px'}}></i>
            </button>
          )}
        </div>
      </div>
      
      <!-- 地點搜尋 -->
      <div className="col-md-3">
        <label className="form-label small text-muted">工作地點</label>
        <div className="input-group">
          <span className="input-group-text bg-white border-end-0">
            <i className="lucide-map-pin text-muted"></i>
          </span>
          <select 
            className="form-select border-start-0"
            value={searchQuery.location}
            onChange={(e) => setSearchQuery({...searchQuery, location: e.target.value})}
          >
            <option value="">全台灣</option>
            <option value="taipei">台北市</option>
            <option value="new-taipei">新北市</option>
            <option value="taoyuan">桃園市</option>
            <option value="taichung">台中市</option>
            <option value="tainan">台南市</option>
            <option value="kaohsiung">高雄市</option>
            <option value="remote">遠端工作</option>
          </select>
        </div>
      </div>
      
      <!-- 薪資範圍 -->
      <div className="col-md-3">
        <label className="form-label small text-muted">期望薪資</label>
        <div className="input-group">
          <span className="input-group-text bg-white border-end-0">
            <i className="lucide-dollar-sign text-muted"></i>
          </span>
          <select 
            className="form-select border-start-0"
            value={searchQuery.salary}
            onChange={(e) => setSearchQuery({...searchQuery, salary: e.target.value})}
          >
            <option value="">不限</option>
            <option value="30000-40000">30K - 40K</option>
            <option value="40000-60000">40K - 60K</option>
            <option value="60000-80000">60K - 80K</option>
            <option value="80000-100000">80K - 100K</option>
            <option value="100000+">100K+</option>
          </select>
        </div>
      </div>
      
      <!-- 搜尋按鈕 -->
      <div className="col-md-2">
        <div className="d-grid">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isSearching}
          >
            {isSearching ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                搜尋中
              </>
            ) : (
              <>
                <i className="lucide-search me-2"></i>
                搜尋職位
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  </form>
</div>
```

### 快速篩選標籤
```html
<div className="quick-filters mt-3">
  <div className="d-flex flex-wrap gap-2 align-items-center">
    <span className="small text-muted me-2">快速篩選：</span>
    
    {quickFilters.map((filter, index) => (
      <button
        key={index}
        className={`btn btn-sm ${
          activeFilters.includes(filter.value) 
            ? 'btn-primary' 
            : 'btn-outline-secondary'
        }`}
        onClick={() => toggleQuickFilter(filter.value)}
      >
        <i className={`lucide-${filter.icon} me-1`} style={{fontSize: '12px'}}></i>
        {filter.label}
      </button>
    ))}
    
    <!-- 進階篩選按鈕 -->
    <button 
      className="btn btn-sm btn-outline-primary ms-2"
      onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
    >
      <i className="lucide-sliders-horizontal me-1" style={{fontSize: '12px'}}></i>
      進階篩選
      <i className={`lucide-chevron-${showAdvancedFilters ? 'up' : 'down'} ms-1`} style={{fontSize: '12px'}}></i>
    </button>
    
    <!-- 清除篩選 -->
    {(activeFilters.length > 0 || Object.values(searchQuery).some(v => v)) && (
      <button 
        className="btn btn-sm btn-link text-danger ms-2 p-0"
        onClick={clearAllFilters}
      >
        <i className="lucide-x me-1" style={{fontSize: '12px'}}></i>
        清除全部
      </button>
    )}
  </div>
</div>
```

## 🎛️ 左側篩選面板設計

### 篩選器容器
```html
<div className="filters-panel">
  <div className="sticky-top" style={{top: '100px'}}>
    <!-- 篩選標題 -->
    <div className="d-flex justify-content-between align-items-center mb-3">
      <h6 className="mb-0">
        <i className="lucide-filter text-primary me-2"></i>
        篩選條件
      </h6>
      {hasActiveFilters && (
        <button 
          className="btn btn-sm btn-link text-danger p-0"
          onClick={clearAllFilters}
        >
          清除全部
        </button>
      )}
    </div>
    
    <!-- 職位類型篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-briefcase text-muted me-2" style={{fontSize: '16px'}}></i>
        職位類型
      </h6>
      <div className="filter-options">
        {jobTypes.map((type, index) => (
          <div key={index} className="form-check mb-2">
            <input 
              className="form-check-input"
              type="checkbox"
              id={`jobType-${index}`}
              checked={filters.jobTypes.includes(type.value)}
              onChange={() => toggleFilter('jobTypes', type.value)}
            />
            <label className="form-check-label d-flex justify-content-between" htmlFor={`jobType-${index}`}>
              <span>{type.label}</span>
              <span className="badge bg-light text-muted">{type.count}</span>
            </label>
          </div>
        ))}
      </div>
    </div>
    
    <!-- 工作經驗篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-user-check text-muted me-2" style={{fontSize: '16px'}}></i>
        工作經驗
      </h6>
      <div className="filter-options">
        {experienceLevels.map((level, index) => (
          <div key={index} className="form-check mb-2">
            <input 
              className="form-check-input"
              type="radio"
              name="experience"
              id={`experience-${index}`}
              checked={filters.experience === level.value}
              onChange={() => setFilter('experience', level.value)}
            />
            <label className="form-check-label d-flex justify-content-between" htmlFor={`experience-${index}`}>
              <span>{level.label}</span>
              <span className="badge bg-light text-muted">{level.count}</span>
            </label>
          </div>
        ))}
      </div>
    </div>
    
    <!-- 公司規模篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-building text-muted me-2" style={{fontSize: '16px'}}></i>
        公司規模
      </h6>
      <div className="filter-options">
        {companySizes.map((size, index) => (
          <div key={index} className="form-check mb-2">
            <input 
              className="form-check-input"
              type="checkbox"
              id={`companySize-${index}`}
              checked={filters.companySizes.includes(size.value)}
              onChange={() => toggleFilter('companySizes', size.value)}
            />
            <label className="form-check-label d-flex justify-content-between" htmlFor={`companySize-${index}`}>
              <span>{size.label}</span>
              <span className="badge bg-light text-muted">{size.count}</span>
            </label>
          </div>
        ))}
      </div>
    </div>
    
    <!-- 薪資範圍滑桿 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-dollar-sign text-muted me-2" style={{fontSize: '16px'}}></i>
        薪資範圍
      </h6>
      <div className="salary-range-container">
        <div className="d-flex justify-content-between mb-2">
          <span className="small text-muted">NT$ {formatSalary(salaryRange.min)}</span>
          <span className="small text-muted">NT$ {formatSalary(salaryRange.max)}</span>
        </div>
        <div className="range-slider-container position-relative">
          <input 
            type="range"
            className="form-range"
            min="20000"
            max="200000"
            step="5000"
            value={salaryRange.min}
            onChange={(e) => setSalaryRange({...salaryRange, min: parseInt(e.target.value)})}
          />
          <input 
            type="range"
            className="form-range position-absolute top-0"
            min="20000"
            max="200000"
            step="5000"
            value={salaryRange.max}
            onChange={(e) => setSalaryRange({...salaryRange, max: parseInt(e.target.value)})}
          />
        </div>
        <div className="d-flex justify-content-between mt-2">
          <input 
            type="number"
            className="form-control form-control-sm"
            style={{width: '80px'}}
            value={salaryRange.min}
            onChange={(e) => setSalaryRange({...salaryRange, min: parseInt(e.target.value)})}
          />
          <span className="align-self-center mx-2">-</span>
          <input 
            type="number"
            className="form-control form-control-sm"
            style={{width: '80px'}}
            value={salaryRange.max}
            onChange={(e) => setSalaryRange({...salaryRange, max: parseInt(e.target.value)})}
          />
        </div>
      </div>
    </div>
    
    <!-- 技能標籤篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-code text-muted me-2" style={{fontSize: '16px'}}></i>
        技能要求
      </h6>
      <div className="skills-input mb-3">
        <div className="input-group input-group-sm">
          <input 
            type="text"
            className="form-control"
            placeholder="搜尋技能..."
            value={skillSearch}
            onChange={(e) => setSkillSearch(e.target.value)}
          />
          <button className="btn btn-outline-secondary" type="button">
            <i className="lucide-search" style={{fontSize: '12px'}}></i>
          </button>
        </div>
      </div>
      <div className="skills-tags">
        {popularSkills.filter(skill => 
          skill.name.toLowerCase().includes(skillSearch.toLowerCase())
        ).slice(0, 10).map((skill, index) => (
          <button
            key={index}
            className={`btn btn-sm me-2 mb-2 ${
              filters.skills.includes(skill.value) 
                ? 'btn-primary' 
                : 'btn-outline-secondary'
            }`}
            onClick={() => toggleFilter('skills', skill.value)}
          >
            {skill.name}
            <span className="badge bg-light text-muted ms-1">{skill.count}</span>
          </button>
        ))}
      </div>
    </div>
    
    <!-- 工作性質篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-clock text-muted me-2" style={{fontSize: '16px'}}></i>
        工作性質
      </h6>
      <div className="filter-options">
        {workTypes.map((type, index) => (
          <div key={index} className="form-check mb-2">
            <input 
              className="form-check-input"
              type="checkbox"
              id={`workType-${index}`}
              checked={filters.workTypes.includes(type.value)}
              onChange={() => toggleFilter('workTypes', type.value)}
            />
            <label className="form-check-label d-flex justify-content-between" htmlFor={`workType-${index}`}>
              <span>
                <i className={`lucide-${type.icon} me-2 text-muted`} style={{fontSize: '14px'}}></i>
                {type.label}
              </span>
              <span className="badge bg-light text-muted">{type.count}</span>
            </label>
          </div>
        ))}
      </div>
    </div>
    
    <!-- 發布時間篩選 -->
    <div className="filter-section mb-4">
      <h6 className="filter-title mb-3">
        <i className="lucide-calendar text-muted me-2" style={{fontSize: '16px'}}></i>
        發布時間
      </h6>
      <div className="filter-options">
        {publishedTimeOptions.map((option, index) => (
          <div key={index} className="form-check mb-2">
            <input 
              className="form-check-input"
              type="radio"
              name="publishedTime"
              id={`publishedTime-${index}`}
              checked={filters.publishedTime === option.value}
              onChange={() => setFilter('publishedTime', option.value)}
            />
            <label className="form-check-label d-flex justify-content-between" htmlFor={`publishedTime-${index}`}>
              <span>{option.label}</span>
              <span className="badge bg-light text-muted">{option.count}</span>
            </label>
          </div>
        ))}
      </div>
    </div>
  </div>
</div>
```

## 📊 結果統計和排序區域

### 結果統計
```html
<div className="results-header mb-4">
  <div className="row align-items-center">
    <div className="col-md-6">
      <div className="results-info">
        <h5 className="mb-1">
          {isLoading ? (
            <div className="placeholder-glow">
              <span className="placeholder col-4"></span>
            </div>
          ) : (
            <>
              找到 <span className="text-primary fw-bold">{totalResults.toLocaleString()}</span> 個職位
            </>
          )}
        </h5>
        <div className="d-flex flex-wrap gap-2 align-items-center">
          {searchQuery.keyword && (
            <span className="badge bg-primary-subtle text-primary">
              關鍵字: {searchQuery.keyword}
            </span>
          )}
          {searchQuery.location && (
            <span className="badge bg-success-subtle text-success">
              地點: {getLocationName(searchQuery.location)}
            </span>
          )}
          {searchQuery.salary && (
            <span className="badge bg-warning-subtle text-warning">
              薪資: {searchQuery.salary}
            </span>
          )}
          {activeFilters.length > 0 && (
            <span className="badge bg-info-subtle text-info">
              {activeFilters.length} 個篩選條件
            </span>
          )}
        </div>
      </div>
    </div>
    
    <div className="col-md-6">
      <div className="d-flex justify-content-md-end align-items-center gap-3">
        <!-- 檢視模式切換 -->
        <div className="btn-group" role="group">
          <input 
            type="radio" 
            className="btn-check" 
            name="viewMode" 
            id="listView" 
            checked={viewMode === 'list'}
            onChange={() => setViewMode('list')}
          />
          <label className="btn btn-outline-secondary btn-sm" htmlFor="listView">
            <i className="lucide-list"></i>
          </label>
          
          <input 
            type="radio" 
            className="btn-check" 
            name="viewMode" 
            id="gridView" 
            checked={viewMode === 'grid'}
            onChange={() => setViewMode('grid')}
          />
          <label className="btn btn-outline-secondary btn-sm" htmlFor="gridView">
            <i className="lucide-grid-3x3"></i>
          </label>
        </div>
        
        <!-- 排序選項 -->
        <div className="sort-options">
          <select 
            className="form-select form-select-sm"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{minWidth: '150px'}}
          >
            <option value="relevance">相關性排序</option>
            <option value="date">發布時間</option>
            <option value="salary-high">薪資由高到低</option>
            <option value="salary-low">薪資由低到高</option>
            <option value="company">公司名稱</option>
            <option value="location">工作地點</option>
          </select>
        </div>
        
        <!-- 每頁顯示數量 -->
        <div className="per-page-options">
          <select 
            className="form-select form-select-sm"
            value={perPage}
            onChange={(e) => setPerPage(parseInt(e.target.value))}
            style={{minWidth: '100px'}}
          >
            <option value={10}>10 個/頁</option>
            <option value={20}>20 個/頁</option>
            <option value={50}>50 個/頁</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</div>
```

## 📋 職位列表設計

### 列表檢視模式
```html
<div className="jobs-list">
  {isLoading ? (
    <!-- 載入骨架屏 -->
    <div className="loading-skeleton">
      {Array.from({length: 5}).map((_, index) => (
        <div key={index} className="job-card card border-0 shadow-sm mb-3">
          <div className="card-body">
            <div className="row">
              <div className="col-md-8">
                <div className="placeholder-glow">
                  <div className="d-flex align-items-center mb-2">
                    <div className="placeholder rounded me-3" style={{width: '50px', height: '50px'}}></div>
                    <div className="flex-grow-1">
                      <h5 className="placeholder col-6 mb-1"></h5>
                      <p className="placeholder col-4 mb-0"></p>
                    </div>
                  </div>
                  <p className="placeholder col-8 mb-2"></p>
                  <div className="d-flex gap-2">
                    <span className="placeholder col-2"></span>
                    <span className="placeholder col-2"></span>
                    <span className="placeholder col-2"></span>
                  </div>
                </div>
              </div>
              <div className="col-md-4">
                <div className="placeholder-glow text-end">
                  <p className="placeholder col-6 ms-auto mb-2"></p>
                  <p className="placeholder col-4 ms-auto mb-2"></p>
                  <div className="placeholder col-8 ms-auto" style={{height: '38px'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  ) : jobs.length > 0 ? (
    <!-- 職位卡片列表 -->
    <div className="jobs-container">
      {jobs.map((job, index) => (
        <div key={job.id} className="job-card card border-0 shadow-sm mb-3 hover-lift">
          <div className="card-body">
            <div className="row">
              <!-- 左側：職位資訊 -->
              <div className="col-md-8">
                <div className="d-flex align-items-start">
                  <!-- 公司 Logo -->
                  <div className="company-logo me-3">
                    <img 
                      src={job.company.logo} 
                      alt={job.company.name}
                      className="rounded"
                      style={{width: '50px', height: '50px', objectFit: 'cover'}}
                      onError={(e) => {
                        e.target.src = '/default-company-logo.svg';
                      }}
                    />
                  </div>
                  
                  <!-- 職位詳情 -->
                  <div className="job-info flex-grow-1">
                    <div className="d-flex align-items-start justify-content-between mb-2">
                      <h5 className="job-title mb-1">
                        <a 
                          href={`/jobs/${job.id}`} 
                          className="text-decoration-none text-dark hover-primary"
                        >
                          {job.title}
                        </a>
                        {job.isNew && (
                          <span className="badge bg-success ms-2">新職位</span>
                        )}
                        {job.isUrgent && (
                          <span className="badge bg-warning ms-2">急徵</span>
                        )}
                        {job.isRemote && (
                          <span className="badge bg-info ms-2">遠端</span>
                        )}
                      </h5>
                    </div>
                    
                    <div className="company-info mb-2">
                      <a 
                        href={`/company/${job.company.id}`} 
                        className="text-decoration-none text-muted hover-primary"
                      >
                        <i className="lucide-building me-1" style={{fontSize: '14px'}}></i>
                        {job.company.name}
                      </a>
                      <span className="text-muted mx-2">•</span>
                      <span className="text-muted">
                        <i className="lucide-map-pin me-1" style={{fontSize: '14px'}}></i>
                        {job.location}
                      </span>
                      <span className="text-muted mx-2">•</span>
                      <span className="text-muted">
                        <i className="lucide-clock me-1" style={{fontSize: '14px'}}></i>
                        {job.employmentType}
                      </span>
                    </div>
                    
                    <p className="job-description text-muted mb-2">
                      {job.description.substring(0, 150)}...
                    </p>
                    
                    <!-- 技能標籤 -->
                    <div className="skills-tags mb-2">
                      {job.skills.slice(0, 4).map((skill, skillIndex) => (
                        <span key={skillIndex} className="badge bg-light text-dark me-1 mb-1">
                          {skill}
                        </span>
                      ))}
                      {job.skills.length > 4 && (
                        <span className="badge bg-light text-muted">+{job.skills.length - 4}</span>
                      )}
                    </div>
                    
                    <!-- 職位統計 -->
                    <div className="job-stats small text-muted">
                      <span className="me-3">
                        <i className="lucide-eye me-1" style={{fontSize: '12px'}}></i>
                        {job.views || 0} 次查看
                      </span>
                      <span className="me-3">
                        <i className="lucide-users me-1" style={{fontSize: '12px'}}></i>
                        {job.applications || 0} 人申請
                      </span>
                      <span>
                        <i className="lucide-calendar me-1" style={{fontSize: '12px'}}></i>
                        {formatDate(job.publishedAt)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 右側：薪資和操作 -->
              <div className="col-md-4">
                <div className="text-md-end">
                  <!-- 薪資資訊 -->
                  <div className="salary-info mb-3">
                    {job.salary ? (
                      <div className="salary-range">
                        <div className="h6 text-success mb-0">
                          NT$ {job.salary.min.toLocaleString()} - {job.salary.max.toLocaleString()}
                        </div>
                        <small className="text-muted">月薪</small>
                      </div>
                    ) : (
                      <div className="salary-negotiable">
                        <div className="h6 text-muted mb-0">面議</div>
                        <small className="text-muted">薪資面議</small>
                      </div>
                    )}
                  </div>
                  
                  <!-- 操作按鈕 -->
                  <div className="job-actions">
                    <div className="d-grid gap-2">
                      {user?.appliedJobs?.includes(job.id) ? (
                        <button className="btn btn-success btn-sm" disabled>
                          <i className="lucide-check me-1" style={{fontSize: '12px'}}></i>
                          已申請
                        </button>
                      ) : (
                        <button 
                          className="btn btn-primary btn-sm"
                          onClick={() => handleQuickApply(job.id)}
                        >
                          <i className="lucide-send me-1" style={{fontSize: '12px'}}></i>
                          快速申請
                        </button>
                      )}
                      
                      <div className="row g-1">
                        <div className="col-6">
                          <button 
                            className={`btn btn-sm w-100 ${
                              user?.savedJobs?.includes(job.id) 
                                ? 'btn-warning' 
                                : 'btn-outline-warning'
                            }`}
                            onClick={() => handleSaveJob(job.id)}
                          >
                            <i className={`lucide-heart ${user?.savedJobs?.includes(job.id) ? 'fill' : ''}`} style={{fontSize: '12px'}}></i>
                          </button>
                        </div>
                        <div className="col-6">
                          <button 
                            className="btn btn-outline-secondary btn-sm w-100"
                            onClick={() => handleShareJob(job)}
                          >
                            <i className="lucide-share-2" style={{fontSize: '12px'}}></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 匹配度 -->
                  {user && job.matchScore && (
                    <div className="match-score mt-2">
                      <div className="d-flex align-items-center justify-content-end">
                        <small className="text-muted me-2">匹配度</small>
                        <div className="progress" style={{width: '60px', height: '6px'}}>
                          <div 
                            className={`progress-bar ${
                              job.matchScore >= 80 ? 'bg-success' :
                              job.matchScore >= 60 ? 'bg-warning' : 'bg-danger'
                            }`}
                            style={{width: `${job.matchScore}%`}}
                          ></div>
                        </div>
                        <small className="text-muted ms-2">{job.matchScore}%</small>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  ) : (
    <!-- 無結果狀態 -->
    <div className="no-results text-center py-5">
      <i className="lucide-search-x text-muted mb-3" style={{fontSize: '4rem'}}></i>
      <h4 className="text-muted mb-3">找不到符合條件的職位</h4>
      <p className="text-muted mb-4">
        試試調整搜尋條件或篩選器，或者
        <a href="/job-alerts" className="text-decoration-none ms-1">設定職位提醒</a>
        讓我們在有新職位時通知您。
      </p>
      <div className="d-flex justify-content-center gap-3">
        <button className="btn btn-outline-primary" onClick={clearAllFilters}>
          <i className="lucide-refresh-cw me-2"></i>
          清除篩選條件
        </button>
        <a href="/search" className="btn btn-primary">
          <i className="lucide-search me-2"></i>
          重新搜尋
        </a>
      </div>
    </div>
  )}
</div>
```