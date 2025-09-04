/**
 * 職位搜索頁面組件
 * 提供詳細的職位搜索功能
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { 
  Search, 
  MapPin, 
  Briefcase, 
  Filter, 
  TrendingUp, 
  DollarSign,
  Clock,
  Building,
  X,
  Plus,
  ChevronDown
} from 'lucide-react';
import { useSearchStore } from '../stores/searchStore';
import { useUIStore } from '../stores/uiStore';

interface SearchFormData {
  keywords: string;
  location: string;
  jobType: string;
  experience: string;
  salary: string;
  company: string;
  remote: boolean;
  platforms: string[];
}

/**
 * 職位搜索頁面組件
 */
export const JobSearchPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { searchQuery, setSearchQuery, addToHistory } = useSearchStore();
  const { addNotification } = useUIStore();
  
  // 從路由狀態獲取初始搜索參數
  const initialState = location.state as { keywords?: string; location?: string } || {};
  
  const [formData, setFormData] = useState<SearchFormData>({
    keywords: initialState.keywords || searchParams.get('q') || searchQuery.keywords || '',
    location: initialState.location || searchParams.get('location') || searchQuery.location || '',
    jobType: searchQuery.jobType || '',
    experience: searchQuery.experience || '',
    salary: searchQuery.salary || '',
    company: searchQuery.company || '',
    remote: searchQuery.remote || false,
    platforms: searchQuery.platforms || []
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // 可用的求職平台
  const availablePlatforms = [
    { id: '104', name: '104人力銀行', color: 'primary' },
    { id: 'linkedin', name: 'LinkedIn', color: 'info' },
    { id: 'indeed', name: 'Indeed', color: 'success' },
    { id: 'yourator', name: 'Yourator', color: 'warning' },
    { id: 'cakeresume', name: 'CakeResume', color: 'danger' }
  ];
  
  // 熱門搜索關鍵詞
  const popularKeywords = [
    'Frontend Developer',
    'Backend Engineer', 
    'Full Stack Developer',
    'Product Manager',
    'Data Scientist',
    'UI/UX Designer',
    'DevOps Engineer',
    'Mobile Developer',
    'QA Engineer',
    'Project Manager'
  ];
  
  // 熱門地點
  const popularLocations = [
    '台北市',
    '新北市',
    '桃園市',
    '台中市',
    '台南市',
    '高雄市',
    '新竹市',
    '新竹縣'
  ];
  
  // 處理表單輸入變化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;
    
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  // 處理平台選擇
  const handlePlatformToggle = (platformId: string) => {
    setFormData(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter(p => p !== platformId)
        : [...prev.platforms, platformId]
    }));
  };
  
  // 處理快速關鍵詞選擇
  const handleQuickKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      keywords: keyword
    }));
  };
  
  // 處理快速地點選擇
  const handleQuickLocation = (location: string) => {
    setFormData(prev => ({
      ...prev,
      location: location
    }));
  };
  
  // 清除所有篩選條件
  const handleClearFilters = () => {
    setFormData({
      keywords: '',
      location: '',
      jobType: '',
      experience: '',
      salary: '',
      company: '',
      remote: false,
      platforms: []
    });
  };
  
  // 處理表單提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.keywords.trim()) {
      addNotification({
        type: 'error',
        title: '請輸入搜索關鍵詞',
        message: '請輸入職位名稱或相關關鍵詞',
        duration: 3000
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      // 更新搜索狀態
      setSearchQuery({
        keywords: formData.keywords,
        location: formData.location,
        jobType: formData.jobType,
        experience: formData.experience,
        salary: formData.salary,
        company: formData.company,
        remote: formData.remote,
        platforms: formData.platforms
      });
      
      // 添加到搜索歷史
      addToHistory({
        keywords: formData.keywords,
        location: formData.location,
        timestamp: new Date().toISOString()
      });
      
      // 模擬 API 調用
      const response = await fetch('http://localhost:8000/api/v1/jobs/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        const results = await response.json();
        // 導航到結果頁面
        navigate('/results', { 
          state: { 
            results, 
            searchParams: formData 
          } 
        });
      } else {
        throw new Error('搜索失敗');
      }
    } catch (error) {
      console.error('搜索錯誤:', error);
      addNotification({
        type: 'error',
        title: '搜索失敗',
        message: '搜索過程中發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="job-search-page">
      {/* 頁面標題 */}
      <section className="page-header bg-light py-4">
        <div className="container">
          <div className="row">
            <div className="col-12">
              <nav aria-label="breadcrumb">
                <ol className="breadcrumb mb-2">
                  <li className="breadcrumb-item">
                    <a href="/" className="text-decoration-none">首頁</a>
                  </li>
                  <li className="breadcrumb-item active" aria-current="page">
                    職位搜索
                  </li>
                </ol>
              </nav>
              <h1 className="h3 fw-bold mb-1">職位搜索</h1>
              <p className="text-muted mb-0">搜索來自多個平台的最新職位機會</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* 搜索表單 */}
      <section className="search-form-section py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-10">
              <div className="card shadow-lg border-0">
                <div className="card-body p-4">
                  <form onSubmit={handleSubmit}>
                    {/* 基本搜索 */}
                    <div className="basic-search mb-4">
                      <div className="row g-3">
                        {/* 關鍵詞搜索 */}
                        <div className="col-lg-6">
                          <label htmlFor="keywords" className="form-label fw-semibold">
                            <Briefcase size={18} className="me-2" />
                            職位關鍵詞 *
                          </label>
                          <input
                            type="text"
                            className="form-control form-control-lg"
                            id="keywords"
                            name="keywords"
                            placeholder="例如：Frontend Developer, 產品經理"
                            value={formData.keywords}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                        
                        {/* 地點搜索 */}
                        <div className="col-lg-6">
                          <label htmlFor="location" className="form-label fw-semibold">
                            <MapPin size={18} className="me-2" />
                            工作地點
                          </label>
                          <input
                            type="text"
                            className="form-control form-control-lg"
                            id="location"
                            name="location"
                            placeholder="例如：台北市, 新竹市"
                            value={formData.location}
                            onChange={handleInputChange}
                          />
                        </div>
                      </div>
                    </div>
                    
                    {/* 進階搜索切換 */}
                    <div className="advanced-toggle mb-3">
                      <button
                        type="button"
                        className="btn btn-outline-secondary"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                      >
                        <Filter size={16} className="me-2" />
                        進階搜索
                        <ChevronDown 
                          size={16} 
                          className={`ms-2 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} 
                        />
                      </button>
                    </div>
                    
                    {/* 進階搜索選項 */}
                    {showAdvanced && (
                      <div className="advanced-search mb-4">
                        <div className="row g-3">
                          {/* 職位類型 */}
                          <div className="col-lg-3">
                            <label htmlFor="jobType" className="form-label fw-semibold">
                              職位類型
                            </label>
                            <select
                              className="form-select"
                              id="jobType"
                              name="jobType"
                              value={formData.jobType}
                              onChange={handleInputChange}
                            >
                              <option value="">所有類型</option>
                              <option value="full-time">全職</option>
                              <option value="part-time">兼職</option>
                              <option value="contract">合約</option>
                              <option value="internship">實習</option>
                            </select>
                          </div>
                          
                          {/* 經驗要求 */}
                          <div className="col-lg-3">
                            <label htmlFor="experience" className="form-label fw-semibold">
                              經驗要求
                            </label>
                            <select
                              className="form-select"
                              id="experience"
                              name="experience"
                              value={formData.experience}
                              onChange={handleInputChange}
                            >
                              <option value="">不限</option>
                              <option value="entry">新鮮人</option>
                              <option value="1-3">1-3年</option>
                              <option value="3-5">3-5年</option>
                              <option value="5+">5年以上</option>
                            </select>
                          </div>
                          
                          {/* 薪資範圍 */}
                          <div className="col-lg-3">
                            <label htmlFor="salary" className="form-label fw-semibold">
                              <DollarSign size={16} className="me-1" />
                              薪資範圍
                            </label>
                            <select
                              className="form-select"
                              id="salary"
                              name="salary"
                              value={formData.salary}
                              onChange={handleInputChange}
                            >
                              <option value="">不限</option>
                              <option value="30-50">30K-50K</option>
                              <option value="50-80">50K-80K</option>
                              <option value="80-120">80K-120K</option>
                              <option value="120+">120K以上</option>
                            </select>
                          </div>
                          
                          {/* 公司名稱 */}
                          <div className="col-lg-3">
                            <label htmlFor="company" className="form-label fw-semibold">
                              <Building size={16} className="me-1" />
                              公司名稱
                            </label>
                            <input
                              type="text"
                              className="form-control"
                              id="company"
                              name="company"
                              placeholder="例如：Google, 台積電"
                              value={formData.company}
                              onChange={handleInputChange}
                            />
                          </div>
                          
                          {/* 遠端工作 */}
                          <div className="col-12">
                            <div className="form-check">
                              <input
                                className="form-check-input"
                                type="checkbox"
                                id="remote"
                                name="remote"
                                checked={formData.remote}
                                onChange={handleInputChange}
                              />
                              <label className="form-check-label" htmlFor="remote">
                                包含遠端工作職位
                              </label>
                            </div>
                          </div>
                          
                          {/* 平台選擇 */}
                          <div className="col-12">
                            <label className="form-label fw-semibold mb-3">
                              搜索平台（可多選）
                            </label>
                            <div className="platform-selection">
                              <div className="row g-2">
                                {availablePlatforms.map((platform) => (
                                  <div key={platform.id} className="col-auto">
                                    <div className="form-check">
                                      <input
                                        className="form-check-input"
                                        type="checkbox"
                                        id={`platform-${platform.id}`}
                                        checked={formData.platforms.includes(platform.id)}
                                        onChange={() => handlePlatformToggle(platform.id)}
                                      />
                                      <label 
                                        className="form-check-label" 
                                        htmlFor={`platform-${platform.id}`}
                                      >
                                        <span className={`badge bg-${platform.color} me-1`}>
                                          {platform.name}
                                        </span>
                                      </label>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* 搜索按鈕和清除按鈕 */}
                    <div className="search-actions d-flex justify-content-between align-items-center">
                      <button
                        type="button"
                        className="btn btn-outline-secondary"
                        onClick={handleClearFilters}
                      >
                        <X size={16} className="me-2" />
                        清除篩選
                      </button>
                      
                      <button
                        type="submit"
                        className="btn btn-primary btn-lg px-5"
                        disabled={isLoading}
                      >
                        {isLoading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            搜索中...
                          </>
                        ) : (
                          <>
                            <Search size={20} className="me-2" />
                            搜索職位
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* 快速選擇區塊 */}
      <section className="quick-selection-section py-4 bg-light">
        <div className="container">
          <div className="row">
            {/* 熱門關鍵詞 */}
            <div className="col-lg-6 mb-4">
              <h6 className="fw-bold mb-3">
                <TrendingUp size={18} className="me-2 text-primary" />
                熱門關鍵詞
              </h6>
              <div className="d-flex flex-wrap gap-2">
                {popularKeywords.map((keyword, index) => (
                  <button
                    key={index}
                    className="btn btn-outline-primary btn-sm"
                    onClick={() => handleQuickKeyword(keyword)}
                  >
                    {keyword}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 熱門地點 */}
            <div className="col-lg-6 mb-4">
              <h6 className="fw-bold mb-3">
                <MapPin size={18} className="me-2 text-success" />
                熱門地點
              </h6>
              <div className="d-flex flex-wrap gap-2">
                {popularLocations.map((location, index) => (
                  <button
                    key={index}
                    className="btn btn-outline-success btn-sm"
                    onClick={() => handleQuickLocation(location)}
                  >
                    {location}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default JobSearchPage;