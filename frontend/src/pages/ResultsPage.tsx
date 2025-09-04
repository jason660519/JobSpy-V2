/**
 * 搜索結果頁面組件
 * 提供職位搜索結果展示、篩選、排序、分頁等功能
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import {
  Search,
  Filter,
  SlidersHorizontal,
  MapPin,
  Calendar,
  DollarSign,
  Clock,
  Building,
  Briefcase,
  Heart,
  Share2,
  ChevronDown,
  ChevronUp,
  Grid,
  List,
  ArrowUpDown,
  TrendingUp,
  Star,
  Eye,
  Bookmark,
  X,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useJobStore } from '../stores/jobStore';
import { useSearchStore } from '../stores/searchStore';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 排序選項
 */
const SORT_OPTIONS = [
  { value: 'relevance', label: '相關性' },
  { value: 'date', label: '發布時間' },
  { value: 'salary_high', label: '薪資由高到低' },
  { value: 'salary_low', label: '薪資由低到高' },
  { value: 'company', label: '公司名稱' }
];

/**
 * 每頁顯示數量選項
 */
const PER_PAGE_OPTIONS = [10, 20, 50];

/**
 * 職位卡片組件
 */
interface JobCardProps {
  job: any;
  viewMode: 'grid' | 'list';
  onToggleFavorite: (jobId: string) => void;
  onShare: (job: any) => void;
}

const JobCard: React.FC<JobCardProps> = ({ job, viewMode, onToggleFavorite, onShare }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  
  /**
   * 格式化薪資
   */
  const formatSalary = (min?: number, max?: number, currency = 'TWD') => {
    if (!min && !max) return '面議';
    
    const formatNumber = (num: number) => {
      return new Intl.NumberFormat('zh-TW').format(num);
    };
    
    if (min && max) {
      return `${formatNumber(min)} - ${formatNumber(max)} ${currency}`;
    } else if (min) {
      return `${formatNumber(min)}+ ${currency}`;
    } else if (max) {
      return `最高 ${formatNumber(max)} ${currency}`;
    }
    
    return '面議';
  };
  
  /**
   * 格式化日期
   */
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return '1 天前';
    } else if (diffDays < 7) {
      return `${diffDays} 天前`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} 週前`;
    } else {
      return date.toLocaleDateString('zh-TW');
    }
  };
  
  /**
   * 處理職位點擊
   */
  const handleJobClick = () => {
    navigate(`/jobs/${job.id}`);
  };
  
  /**
   * 處理收藏點擊
   */
  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    onToggleFavorite(job.id);
  };
  
  /**
   * 處理分享點擊
   */
  const handleShareClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    onShare(job);
  };
  
  if (viewMode === 'list') {
    return (
      <div className="job-card list-view card border-0 shadow-sm mb-3 cursor-pointer" onClick={handleJobClick}>
        <div className="card-body p-4">
          <div className="row align-items-center">
            <div className="col-md-8">
              <div className="d-flex align-items-start">
                <img
                  src={job.companyLogo || `https://ui-avatars.com/api/?name=${job.company}&background=ffc107&color=fff&size=56`}
                  alt={job.company}
                  className="rounded me-3 flex-shrink-0"
                  style={{ width: '56px', height: '56px', objectFit: 'cover' }}
                />
                <div className="flex-grow-1">
                  <div className="d-flex align-items-start justify-content-between mb-2">
                    <div>
                      <h5 className="fw-bold mb-1 text-primary">{job.title}</h5>
                      <p className="text-muted mb-1">{job.company}</p>
                    </div>
                    <div className="action-buttons d-flex gap-2">
                      <button
                        className="btn btn-outline-secondary btn-sm"
                        onClick={handleFavoriteClick}
                      >
                        <Heart 
                          size={16} 
                          className={job.isFavorited ? 'text-danger' : ''}
                          fill={job.isFavorited ? 'currentColor' : 'none'}
                        />
                      </button>
                      <button
                        className="btn btn-outline-secondary btn-sm"
                        onClick={handleShareClick}
                      >
                        <Share2 size={16} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="job-meta d-flex flex-wrap gap-3 mb-2">
                    <span className="text-muted d-flex align-items-center">
                      <MapPin size={14} className="me-1" />
                      {job.location}
                    </span>
                    <span className="text-muted d-flex align-items-center">
                      <Briefcase size={14} className="me-1" />
                      {job.type}
                    </span>
                    <span className="text-muted d-flex align-items-center">
                      <Clock size={14} className="me-1" />
                      {formatDate(job.postedDate)}
                    </span>
                    {(job.salaryMin || job.salaryMax) && (
                      <span className="text-success fw-semibold d-flex align-items-center">
                        <DollarSign size={14} className="me-1" />
                        {formatSalary(job.salaryMin, job.salaryMax)}
                      </span>
                    )}
                  </div>
                  
                  {job.description && (
                    <p className="text-muted small mb-2 job-description">
                      {job.description.length > 150 ? `${job.description.substring(0, 150)}...` : job.description}
                    </p>
                  )}
                  
                  {job.tags && job.tags.length > 0 && (
                    <div className="job-tags">
                      {job.tags.slice(0, 3).map((tag: string, index: number) => (
                        <span key={index} className="badge bg-light text-dark me-2 mb-1">
                          {tag}
                        </span>
                      ))}
                      {job.tags.length > 3 && (
                        <span className="badge bg-light text-muted">+{job.tags.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="col-md-4 text-md-end">
              <div className="job-stats mb-2">
                <div className="d-flex justify-content-md-end gap-3 text-muted small">
                  <span className="d-flex align-items-center">
                    <Eye size={12} className="me-1" />
                    {job.views || 0}
                  </span>
                  <span className="d-flex align-items-center">
                    <Star size={12} className="me-1" />
                    {job.rating || 0}
                  </span>
                </div>
              </div>
              
              {job.urgency === 'high' && (
                <span className="badge bg-danger mb-2">急徵</span>
              )}
              
              <div className="d-grid">
                <button className="btn btn-warning btn-sm">
                  立即申請
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Grid view
  return (
    <div className="job-card grid-view card border-0 shadow-sm h-100 cursor-pointer" onClick={handleJobClick}>
      <div className="card-body p-4">
        <div className="d-flex align-items-start justify-content-between mb-3">
          <img
            src={job.companyLogo || `https://ui-avatars.com/api/?name=${job.company}&background=ffc107&color=fff&size=48`}
            alt={job.company}
            className="rounded flex-shrink-0"
            style={{ width: '48px', height: '48px', objectFit: 'cover' }}
          />
          <div className="action-buttons d-flex gap-2">
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={handleFavoriteClick}
            >
              <Heart 
                size={16} 
                className={job.isFavorited ? 'text-danger' : ''}
                fill={job.isFavorited ? 'currentColor' : 'none'}
              />
            </button>
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={handleShareClick}
            >
              <Share2 size={16} />
            </button>
          </div>
        </div>
        
        <h6 className="fw-bold mb-2 text-primary">{job.title}</h6>
        <p className="text-muted mb-2">{job.company}</p>
        
        <div className="job-meta mb-3">
          <div className="d-flex align-items-center text-muted small mb-1">
            <MapPin size={12} className="me-1" />
            <span>{job.location}</span>
          </div>
          <div className="d-flex align-items-center text-muted small mb-1">
            <Briefcase size={12} className="me-1" />
            <span>{job.type}</span>
          </div>
          <div className="d-flex align-items-center text-muted small">
            <Clock size={12} className="me-1" />
            <span>{formatDate(job.postedDate)}</span>
          </div>
        </div>
        
        {(job.salaryMin || job.salaryMax) && (
          <div className="salary-info mb-3">
            <span className="badge bg-success">
              <DollarSign size={12} className="me-1" />
              {formatSalary(job.salaryMin, job.salaryMax)}
            </span>
          </div>
        )}
        
        {job.description && (
          <p className="text-muted small mb-3 job-description">
            {job.description.length > 100 ? `${job.description.substring(0, 100)}...` : job.description}
          </p>
        )}
        
        {job.tags && job.tags.length > 0 && (
          <div className="job-tags mb-3">
            {job.tags.slice(0, 2).map((tag: string, index: number) => (
              <span key={index} className="badge bg-light text-dark me-1 mb-1">
                {tag}
              </span>
            ))}
            {job.tags.length > 2 && (
              <span className="badge bg-light text-muted">+{job.tags.length - 2}</span>
            )}
          </div>
        )}
        
        <div className="mt-auto">
          {job.urgency === 'high' && (
            <span className="badge bg-danger mb-2">急徵</span>
          )}
          
          <div className="d-flex justify-content-between align-items-center">
            <div className="job-stats d-flex gap-2 text-muted small">
              <span className="d-flex align-items-center">
                <Eye size={12} className="me-1" />
                {job.views || 0}
              </span>
              <span className="d-flex align-items-center">
                <Star size={12} className="me-1" />
                {job.rating || 0}
              </span>
            </div>
            <button className="btn btn-warning btn-sm">
              申請
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 搜索結果頁面組件
 */
export const ResultsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const { 
    searchResults,
    isLoading,
    totalResults,
    currentPage,
    totalPages,
    searchJobs,
    toggleFavorite
  } = useJobStore();
  
  const { searchQuery, updateSearchQuery } = useSearchStore();
  const { isAuthenticated } = useAuthStore();
  const { addNotification } = useUIStore();
  
  // 本地狀態
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [sortBy, setSortBy] = useState('relevance');
  const [perPage, setPerPage] = useState(20);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    jobType: '',
    experienceLevel: '',
    salaryMin: '',
    salaryMax: '',
    company: '',
    remote: false,
    datePosted: ''
  });
  
  // 從 URL 參數獲取搜索條件
  const searchKeyword = searchParams.get('q') || '';
  const searchLocation = searchParams.get('location') || '';
  
  /**
   * 載入搜索結果
   */
  useEffect(() => {
    const loadResults = async () => {
      const searchData = {
        keyword: searchKeyword,
        location: searchLocation,
        jobType: filters.jobType,
        experienceLevel: filters.experienceLevel,
        salaryMin: filters.salaryMin ? parseInt(filters.salaryMin) : undefined,
        salaryMax: filters.salaryMax ? parseInt(filters.salaryMax) : undefined,
        company: filters.company,
        remote: filters.remote,
        datePosted: filters.datePosted,
        sortBy,
        page: currentPage,
        perPage
      };
      
      await searchJobs(searchData);
    };
    
    loadResults();
  }, [searchKeyword, searchLocation, filters, sortBy, currentPage, perPage, searchJobs]);
  
  /**
   * 處理收藏切換
   */
  const handleToggleFavorite = async (jobId: string) => {
    if (!isAuthenticated) {
      addNotification({
        type: 'warning',
        title: '請先登入',
        message: '收藏職位前請先登入您的帳戶',
        duration: 3000
      });
      navigate('/login');
      return;
    }
    
    try {
      await toggleFavorite(jobId);
      
      const job = searchResults.find(j => j.id === jobId);
      addNotification({
        type: 'success',
        title: job?.isFavorited ? '已取消收藏' : '已加入收藏',
        message: job?.isFavorited ? '職位已從收藏中移除' : '職位已加入您的收藏',
        duration: 3000
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '操作失敗',
        message: error.message || '收藏操作失敗，請稍後再試',
        duration: 5000
      });
    }
  };
  
  /**
   * 處理分享
   */
  const handleShare = (job: any) => {
    if (navigator.share) {
      navigator.share({
        title: job.title,
        text: `${job.company} - ${job.title}`,
        url: `${window.location.origin}/jobs/${job.id}`
      });
    } else {
      navigator.clipboard.writeText(`${window.location.origin}/jobs/${job.id}`);
      addNotification({
        type: 'success',
        title: '連結已複製',
        message: '職位連結已複製到剪貼簿',
        duration: 3000
      });
    }
  };
  
  /**
   * 處理篩選器變更
   */
  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };
  
  /**
   * 清除篩選器
   */
  const clearFilters = () => {
    setFilters({
      jobType: '',
      experienceLevel: '',
      salaryMin: '',
      salaryMax: '',
      company: '',
      remote: false,
      datePosted: ''
    });
  };
  
  /**
   * 處理分頁
   */
  const handlePageChange = (page: number) => {
    // 這裡應該調用 jobStore 的分頁方法
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  /**
   * 生成分頁按鈕
   */
  const renderPagination = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          className={`btn ${i === currentPage ? 'btn-warning' : 'btn-outline-secondary'} btn-sm mx-1`}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }
    
    return (
      <div className="d-flex justify-content-center align-items-center gap-2">
        <button
          className="btn btn-outline-secondary btn-sm"
          disabled={currentPage === 1}
          onClick={() => handlePageChange(currentPage - 1)}
        >
          上一頁
        </button>
        
        {startPage > 1 && (
          <>
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={() => handlePageChange(1)}
            >
              1
            </button>
            {startPage > 2 && <span className="mx-2">...</span>}
          </>
        )}
        
        {pages}
        
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="mx-2">...</span>}
            <button
              className="btn btn-outline-secondary btn-sm"
              onClick={() => handlePageChange(totalPages)}
            >
              {totalPages}
            </button>
          </>
        )}
        
        <button
          className="btn btn-outline-secondary btn-sm"
          disabled={currentPage === totalPages}
          onClick={() => handlePageChange(currentPage + 1)}
        >
          下一頁
        </button>
      </div>
    );
  };
  
  return (
    <div className="results-page">
      <div className="container py-4">
        {/* 搜索摘要 */}
        <div className="search-summary mb-4">
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h4 className="fw-bold mb-2">
                搜索結果
                {searchKeyword && (
                  <span className="text-muted"> - "{searchKeyword}"</span>
                )}
                {searchLocation && (
                  <span className="text-muted"> 在 {searchLocation}</span>
                )}
              </h4>
              <p className="text-muted mb-0">
                找到 <strong>{totalResults}</strong> 個職位
              </p>
            </div>
            
            <div className="search-actions d-flex gap-2">
              <Link 
                to="/search" 
                className="btn btn-outline-warning"
              >
                <Search size={16} className="me-2" />
                修改搜索
              </Link>
              
              <button
                className="btn btn-outline-secondary"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter size={16} className="me-2" />
                篩選器
                {showFilters ? <ChevronUp size={16} className="ms-1" /> : <ChevronDown size={16} className="ms-1" />}
              </button>
            </div>
          </div>
        </div>
        
        {/* 篩選器 */}
        {showFilters && (
          <div className="filters-panel card border-0 shadow-sm mb-4">
            <div className="card-body p-4">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h6 className="fw-bold mb-0">
                  <SlidersHorizontal size={18} className="me-2" />
                  進階篩選
                </h6>
                <button 
                  className="btn btn-outline-secondary btn-sm"
                  onClick={clearFilters}
                >
                  <X size={16} className="me-1" />
                  清除篩選
                </button>
              </div>
              
              <div className="row">
                <div className="col-md-3 mb-3">
                  <label className="form-label small fw-semibold">職位類型</label>
                  <select 
                    className="form-select"
                    value={filters.jobType}
                    onChange={(e) => handleFilterChange('jobType', e.target.value)}
                  >
                    <option value="">全部類型</option>
                    <option value="full-time">全職</option>
                    <option value="part-time">兼職</option>
                    <option value="contract">合約</option>
                    <option value="internship">實習</option>
                  </select>
                </div>
                
                <div className="col-md-3 mb-3">
                  <label className="form-label small fw-semibold">經驗要求</label>
                  <select 
                    className="form-select"
                    value={filters.experienceLevel}
                    onChange={(e) => handleFilterChange('experienceLevel', e.target.value)}
                  >
                    <option value="">全部經驗</option>
                    <option value="entry">新鮮人</option>
                    <option value="junior">1-3年</option>
                    <option value="mid">3-5年</option>
                    <option value="senior">5年以上</option>
                  </select>
                </div>
                
                <div className="col-md-3 mb-3">
                  <label className="form-label small fw-semibold">最低薪資</label>
                  <input 
                    type="number" 
                    className="form-control"
                    placeholder="例如: 40000"
                    value={filters.salaryMin}
                    onChange={(e) => handleFilterChange('salaryMin', e.target.value)}
                  />
                </div>
                
                <div className="col-md-3 mb-3">
                  <label className="form-label small fw-semibold">最高薪資</label>
                  <input 
                    type="number" 
                    className="form-control"
                    placeholder="例如: 80000"
                    value={filters.salaryMax}
                    onChange={(e) => handleFilterChange('salaryMax', e.target.value)}
                  />
                </div>
                
                <div className="col-md-4 mb-3">
                  <label className="form-label small fw-semibold">公司名稱</label>
                  <input 
                    type="text" 
                    className="form-control"
                    placeholder="輸入公司名稱"
                    value={filters.company}
                    onChange={(e) => handleFilterChange('company', e.target.value)}
                  />
                </div>
                
                <div className="col-md-4 mb-3">
                  <label className="form-label small fw-semibold">發布時間</label>
                  <select 
                    className="form-select"
                    value={filters.datePosted}
                    onChange={(e) => handleFilterChange('datePosted', e.target.value)}
                  >
                    <option value="">任何時間</option>
                    <option value="1">過去24小時</option>
                    <option value="7">過去一週</option>
                    <option value="30">過去一個月</option>
                  </select>
                </div>
                
                <div className="col-md-4 mb-3 d-flex align-items-end">
                  <div className="form-check">
                    <input 
                      className="form-check-input" 
                      type="checkbox" 
                      id="remoteWork"
                      checked={filters.remote}
                      onChange={(e) => handleFilterChange('remote', e.target.checked)}
                    />
                    <label className="form-check-label fw-semibold" htmlFor="remoteWork">
                      僅顯示遠端工作
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* 工具列 */}
        <div className="toolbar d-flex justify-content-between align-items-center mb-4">
          <div className="view-controls d-flex align-items-center gap-3">
            <div className="btn-group" role="group">
              <button
                className={`btn ${viewMode === 'list' ? 'btn-warning' : 'btn-outline-secondary'} btn-sm`}
                onClick={() => setViewMode('list')}
              >
                <List size={16} />
              </button>
              <button
                className={`btn ${viewMode === 'grid' ? 'btn-warning' : 'btn-outline-secondary'} btn-sm`}
                onClick={() => setViewMode('grid')}
              >
                <Grid size={16} />
              </button>
            </div>
            
            <div className="per-page-selector d-flex align-items-center gap-2">
              <span className="text-muted small">每頁顯示:</span>
              <select 
                className="form-select form-select-sm" 
                style={{ width: 'auto' }}
                value={perPage}
                onChange={(e) => setPerPage(parseInt(e.target.value))}
              >
                {PER_PAGE_OPTIONS.map(option => (
                  <option key={option} value={option}>{option}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="sort-controls d-flex align-items-center gap-2">
            <ArrowUpDown size={16} className="text-muted" />
            <span className="text-muted small">排序:</span>
            <select 
              className="form-select form-select-sm" 
              style={{ width: 'auto' }}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              {SORT_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* 載入狀態 */}
        {isLoading && (
          <div className="text-center py-5">
            <div className="spinner-border text-warning mb-3" role="status">
              <span className="visually-hidden">載入中...</span>
            </div>
            <p className="text-muted">搜索職位中...</p>
          </div>
        )}
        
        {/* 搜索結果 */}
        {!isLoading && (
          <>
            {searchResults && searchResults.length > 0 ? (
              <>
                {viewMode === 'list' ? (
                  <div className="jobs-list">
                    {searchResults.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        viewMode="list"
                        onToggleFavorite={handleToggleFavorite}
                        onShare={handleShare}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="jobs-grid row">
                    {searchResults.map((job) => (
                      <div key={job.id} className="col-lg-4 col-md-6 mb-4">
                        <JobCard
                          job={job}
                          viewMode="grid"
                          onToggleFavorite={handleToggleFavorite}
                          onShare={handleShare}
                        />
                      </div>
                    ))}
                  </div>
                )}
                
                {/* 分頁 */}
                {totalPages > 1 && (
                  <div className="pagination-wrapper mt-5">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <p className="text-muted mb-0">
                        顯示第 {((currentPage - 1) * perPage) + 1} - {Math.min(currentPage * perPage, totalResults)} 項，
                        共 {totalResults} 項結果
                      </p>
                      <div className="pagination-info text-muted small">
                        第 {currentPage} 頁，共 {totalPages} 頁
                      </div>
                    </div>
                    {renderPagination()}
                  </div>
                )}
              </>
            ) : (
              <div className="no-results text-center py-5">
                <AlertCircle size={64} className="text-muted mb-3" />
                <h5 className="text-muted mb-3">找不到符合條件的職位</h5>
                <p className="text-muted mb-4">
                  請嘗試調整搜索條件或篩選器，或者
                  <Link to="/search" className="text-warning text-decoration-none ms-1">
                    重新搜索
                  </Link>
                </p>
                
                <div className="suggestions">
                  <h6 className="fw-bold mb-3">搜索建議：</h6>
                  <ul className="list-unstyled text-muted">
                    <li className="mb-2">• 檢查關鍵字拼寫是否正確</li>
                    <li className="mb-2">• 嘗試使用更通用的關鍵字</li>
                    <li className="mb-2">• 減少篩選條件</li>
                    <li className="mb-2">• 擴大搜索地區範圍</li>
                  </ul>
                </div>
                
                <div className="mt-4">
                  <button 
                    className="btn btn-warning me-3"
                    onClick={clearFilters}
                  >
                    <RefreshCw size={16} className="me-2" />
                    清除所有篩選
                  </button>
                  <Link to="/search" className="btn btn-outline-warning">
                    <Search size={16} className="me-2" />
                    重新搜索
                  </Link>
                </div>
              </div>
            )}
          </>
        )}
      </div>
      
      {/* 自定義樣式已移至內聯樣式 */}
    </div>
  );
};

export default ResultsPage;