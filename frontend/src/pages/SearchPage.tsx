import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, 
  TrendingUp, 
  MapPin, 
  Briefcase, 
  Zap, 
  Star,
  Filter,
  SlidersHorizontal,
  Clock,
  DollarSign,
  Building2,
  Users,
  Globe,
  ChevronDown,
  ChevronUp,
  Sparkles
} from 'lucide-react';
import { SearchForm, SearchQuery } from '../components/search/SearchForm';
import { useJobStore } from '../stores/jobStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 首頁搜尋頁面組件
 * 提供智能職位搜尋功能，包含搜尋表單和熱門關鍵詞推薦
 */
export const SearchPage: React.FC = () => {
  const navigate = useNavigate();
  const { searchJobs } = useJobStore();
  const { addNotification } = useUIStore();
  
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  
  // 熱門搜索關鍵詞
  const popularKeywords = [
    'Frontend Developer',
    'Backend Engineer', 
    'Full Stack Developer',
    'Product Manager',
    'Data Scientist',
    'UI/UX Designer',
    'DevOps Engineer',
    'Mobile Developer'
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
  
  // 熱門公司
  const popularCompanies = [
    'Google',
    'Microsoft',
    'Amazon',
    'Apple',
    'Meta',
    '台積電',
    '聯發科',
    '鴻海'
  ];
  
  // AI 智能建議
  const aiSmartSuggestions = [
    '根據您的技能推薦：React 工程師',
    '熱門職位：雲端架構師',
    '新興職位：AI 工程師',
    '遠端工作機會：全遠端開發',
    '高薪職位：區塊鏈工程師'
  ];
  
  // 初始化最近搜索記錄
  useEffect(() => {
    const savedSearches = localStorage.getItem('recentSearches');
    if (savedSearches) {
      setRecentSearches(JSON.parse(savedSearches));
    }
  }, []);
  
  // 保存搜索記錄到本地存儲
  const saveSearchToHistory = (searchTerm: string) => {
    const updatedSearches = [
      searchTerm,
      ...recentSearches.filter(search => search !== searchTerm)
    ].slice(0, 5); // 保留最近5個搜索
    
    setRecentSearches(updatedSearches);
    localStorage.setItem('recentSearches', JSON.stringify(updatedSearches));
  };
  
  // 生成 AI 智能建議
  const generateAiSuggestions = (query: SearchQuery) => {
    // 這是一個簡化的 AI 建議生成邏輯
    // 在實際應用中，這會調用後端 AI 服務
    const suggestions = [];
    
    if (query.jobTitle.includes('developer') || query.jobTitle.includes('engineer')) {
      suggestions.push('您可能也對以下職位感興趣：Senior Developer, Tech Lead');
    }
    
    if (query.location.includes('台北') || query.location.includes('Taipei')) {
      suggestions.push('台北熱門職位：產品經理, 資料科學家');
    }
    
    if (query.selectedPlatforms.includes('linkedin')) {
      suggestions.push('LinkedIn 熱門：遠端工作機會, 國際職位');
    }
    
    // 添加通用建議
    suggestions.push(...aiSmartSuggestions.slice(0, 3 - suggestions.length));
    
    setAiSuggestions(suggestions);
  };
  
  /**
   * 處理搜索提交
   */
  const handleSearch = async (query: SearchQuery) => {
    setIsLoading(true);
    
    try {
      // 保存搜索記錄
      if (query.jobTitle) {
        saveSearchToHistory(query.jobTitle);
      }
      
      // 生成 AI 建議
      generateAiSuggestions(query);
      
      // 模擬搜索請求
      const searchData = {
        keyword: query.jobTitle,
        location: query.location,
        platforms: query.selectedPlatforms,
        useAI: query.useAI
      };
      
      // 這裡應該調用實際的搜索 API
      // await searchJobs(searchData);
      
      // 導航到結果頁面
      navigate('/results', { 
        state: { 
          searchParams: searchData 
        } 
      });
      
      addNotification({
        type: 'success',
        title: '搜索成功',
        message: '正在為您搜尋相關職位...',
        duration: 3000
      });
    } catch (error: any) {
      console.error('搜索錯誤:', error);
      addNotification({
        type: 'error',
        title: '搜索失敗',
        message: error.message || '搜索過程中發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  /**
   * 處理快速關鍵詞選擇
   */
  const handleQuickKeyword = (keyword: string) => {
    // 直接進行搜索
    handleSearch({
      jobTitle: keyword,
      location: '',
      selectedPlatforms: ['linkedin', 'indeed', 'glassdoor'],
      useAI: true
    });
  };
  
  /**
   * 處理快速地點選擇
   */
  const handleQuickLocation = (location: string) => {
    // 直接進行搜索
    handleSearch({
      jobTitle: '',
      location: location,
      selectedPlatforms: ['linkedin', 'indeed', 'glassdoor'],
      useAI: true
    });
  };
  
  /**
   * 清除搜索歷史
   */
  const clearSearchHistory = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };
  
  return (
    <div className="search-page">
      {/* 英雄區域 */}
      <section className="hero-section bg-gradient-primary text-white py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8 text-center">
              <h1 className="display-4 fw-bold mb-3">
                發現您的理想工作
              </h1>
              <p className="lead mb-4">
                使用 AI 智能匹配技術，為您精準推薦最適合的職位機會
              </p>
              
              {/* 搜索表單 */}
              <div className="search-form-wrapper">
                <SearchForm 
                  onSearch={handleSearch}
                  isLoading={isLoading}
                />
                
                {/* AI 智能建議 */}
                {aiSuggestions.length > 0 && (
                  <div className="ai-suggestions mt-3 p-3 bg-white bg-opacity-10 rounded">
                    <div className="d-flex align-items-center mb-2">
                      <Sparkles size={16} className="me-2" />
                      <h6 className="mb-0">AI 智能建議</h6>
                    </div>
                    <div className="d-flex flex-wrap gap-2">
                      {aiSuggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          className="btn btn-sm btn-outline-light"
                          onClick={() => {
                            // 可以根據建議進行搜索
                            console.log('AI 建議:', suggestion);
                          }}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* 統計數據 */}
      <section className="stats-section py-4 bg-light">
        <div className="container">
          <div className="row text-center">
            <div className="col-md-3 mb-4 mb-md-0">
              <div className="stat-item">
                <div className="h2 fw-bold text-primary mb-2">10,000+</div>
                <p className="text-muted mb-0">職位機會</p>
              </div>
            </div>
            <div className="col-md-3 mb-4 mb-md-0">
              <div className="stat-item">
                <div className="h2 fw-bold text-success mb-2">5,000+</div>
                <p className="text-muted mb-0">成功配對</p>
              </div>
            </div>
            <div className="col-md-3 mb-4 mb-md-0">
              <div className="stat-item">
                <div className="h2 fw-bold text-warning mb-2">500+</div>
                <p className="text-muted mb-0">合作企業</p>
              </div>
            </div>
            <div className="col-md-3">
              <div className="stat-item">
                <div className="h2 fw-bold text-info mb-2">98%</div>
                <p className="text-muted mb-0">用戶滿意度</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* 高級篩選器 */}
      <section className="advanced-filters-section py-4">
        <div className="container">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h5 className="fw-bold mb-0">高級篩選</h5>
            <button 
              className="btn btn-outline-primary btn-sm"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            >
              <SlidersHorizontal size={16} className="me-1" />
              {showAdvancedFilters ? '隱藏篩選器' : '顯示篩選器'}
              {showAdvancedFilters ? 
                <ChevronUp size={16} className="ms-1" /> : 
                <ChevronDown size={16} className="ms-1" />
              }
            </button>
          </div>
          
          {showAdvancedFilters && (
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body">
                <div className="row">
                  {/* 薪資範圍 */}
                  <div className="col-md-3 mb-3">
                    <label className="form-label small fw-bold">薪資範圍</label>
                    <div className="input-group">
                      <span className="input-group-text">NT$</span>
                      <input 
                        type="number" 
                        className="form-control" 
                        placeholder="最低"
                      />
                      <span className="input-group-text">-</span>
                      <input 
                        type="number" 
                        className="form-control" 
                        placeholder="最高"
                      />
                    </div>
                  </div>
                  
                  {/* 經驗要求 */}
                  <div className="col-md-3 mb-3">
                    <label className="form-label small fw-bold">經驗要求</label>
                    <select className="form-select">
                      <option value="">不限</option>
                      <option value="0">無經驗</option>
                      <option value="1">1-3 年</option>
                      <option value="3">3-5 年</option>
                      <option value="5">5-10 年</option>
                      <option value="10">10 年以上</option>
                    </select>
                  </div>
                  
                  {/* 工作類型 */}
                  <div className="col-md-3 mb-3">
                    <label className="form-label small fw-bold">工作類型</label>
                    <select className="form-select">
                      <option value="">不限</option>
                      <option value="fulltime">全職</option>
                      <option value="parttime">兼職</option>
                      <option value="contract">合約</option>
                      <option value="internship">實習</option>
                      <option value="remote">遠端</option>
                    </select>
                  </div>
                  
                  {/* 公司規模 */}
                  <div className="col-md-3 mb-3">
                    <label className="form-label small fw-bold">公司規模</label>
                    <select className="form-select">
                      <option value="">不限</option>
                      <option value="startup">新創公司</option>
                      <option value="small">1-50 人</option>
                      <option value="medium">51-200 人</option>
                      <option value="large">201-1000 人</option>
                      <option value="enterprise">1000 人以上</option>
                    </select>
                  </div>
                </div>
                
                <div className="d-flex justify-content-end">
                  <button className="btn btn-primary">
                    <Filter size={16} className="me-1" />
                    應用篩選
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
      
      {/* 快速選擇區塊 */}
      <section className="quick-selection-section py-5">
        <div className="container">
          <div className="row">
            {/* 最近搜索 */}
            {recentSearches.length > 0 && (
              <div className="col-lg-12 mb-4">
                <div className="card border-0 shadow-sm">
                  <div className="card-header bg-white border-0 py-3">
                    <div className="d-flex justify-content-between align-items-center">
                      <h5 className="fw-bold mb-0">最近搜索</h5>
                      <button 
                        className="btn btn-sm btn-outline-danger"
                        onClick={clearSearchHistory}
                      >
                        清除記錄
                      </button>
                    </div>
                  </div>
                  <div className="card-body p-4">
                    <div className="d-flex flex-wrap gap-2">
                      {recentSearches.map((search, index) => (
                        <button
                          key={index}
                          className="btn btn-outline-secondary btn-sm"
                          onClick={() => handleQuickKeyword(search)}
                        >
                          <Clock size={14} className="me-1" />
                          {search}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* 熱門關鍵詞 */}
            <div className="col-lg-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4">
                  <div className="d-flex align-items-center mb-3">
                    <TrendingUp size={20} className="text-primary me-2" />
                    <h5 className="fw-bold mb-0">熱門職位</h5>
                  </div>
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
              </div>
            </div>
            
            {/* 熱門地點 */}
            <div className="col-lg-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4">
                  <div className="d-flex align-items-center mb-3">
                    <MapPin size={20} className="text-success me-2" />
                    <h5 className="fw-bold mb-0">熱門地點</h5>
                  </div>
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
            
            {/* 熱門公司 */}
            <div className="col-lg-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4">
                  <div className="d-flex align-items-center mb-3">
                    <Briefcase size={20} className="text-warning me-2" />
                    <h5 className="fw-bold mb-0">熱門公司</h5>
                  </div>
                  <div className="d-flex flex-wrap gap-2">
                    {popularCompanies.map((company, index) => (
                      <button
                        key={index}
                        className="btn btn-outline-warning btn-sm"
                        onClick={() => handleQuickKeyword(company)}
                      >
                        {company}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* 功能特色 */}
      <section className="features-section py-5 bg-light">
        <div className="container">
          <div className="row text-center">
            <div className="col-lg-12 mb-5">
              <h2 className="fw-bold mb-3">為什麼選擇 JobSpy</h2>
              <p className="text-muted">我們提供最先進的求職體驗</p>
            </div>
          </div>
          
          <div className="row">
            <div className="col-md-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4 text-center">
                  <div className="feature-icon bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                       style={{ width: '60px', height: '60px' }}>
                    <Zap size={30} />
                  </div>
                  <h5 className="fw-bold mb-3">AI 智能匹配</h5>
                  <p className="text-muted">
                    利用先進的 AI 技術，為您精準匹配最適合的職位機會
                  </p>
                </div>
              </div>
            </div>
            
            <div className="col-md-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4 text-center">
                  <div className="feature-icon bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                       style={{ width: '60px', height: '60px' }}>
                    <Star size={30} />
                  </div>
                  <h5 className="fw-bold mb-3">精選職位</h5>
                  <p className="text-muted">
                    從各大求職平台精選優質職位，節省您的搜尋時間
                  </p>
                </div>
              </div>
            </div>
            
            <div className="col-md-4 mb-4">
              <div className="card border-0 shadow-sm h-100">
                <div className="card-body p-4 text-center">
                  <div className="feature-icon bg-warning text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" 
                       style={{ width: '60px', height: '60px' }}>
                    <Search size={30} />
                  </div>
                  <h5 className="fw-bold mb-3">即時更新</h5>
                  <p className="text-muted">
                    實時同步最新職位資訊，確保您不會錯過任何機會
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SearchPage;