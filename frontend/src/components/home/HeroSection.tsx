/**
 * 首頁英雄區塊組件
 * 包含主要搜索功能和視覺吸引力的頂部區域
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Briefcase, TrendingUp, Users, Star } from 'lucide-react';
import { useSearchStore, useUIStore } from '../../stores';

interface HeroSectionProps {
  className?: string;
}

/**
 * 英雄區塊組件
 */
export const HeroSection: React.FC<HeroSectionProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { query, setQuery, search } = useSearchStore();
  const { addNotification } = useUIStore();
  
  const [localKeyword, setLocalKeyword] = useState(query.keyword);
  const [localLocation, setLocalLocation] = useState(query.location);
  const [isSearching, setIsSearching] = useState(false);
  
  // 熱門搜索關鍵詞
  const popularKeywords = [
    'Frontend Developer',
    'Backend Engineer',
    'Full Stack',
    'Data Scientist',
    'Product Manager',
    'UI/UX Designer',
    'DevOps Engineer',
    'Mobile Developer'
  ];
  
  // 統計數據
  const stats = [
    { icon: Briefcase, label: '活躍職位', value: '50,000+', color: 'text-primary' },
    { icon: Users, label: '註冊用戶', value: '100,000+', color: 'text-success' },
    { icon: TrendingUp, label: '成功媒合', value: '25,000+', color: 'text-info' },
    { icon: Star, label: '平均評分', value: '4.8/5', color: 'text-warning' }
  ];
  
  /**
   * 處理搜索提交
   */
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!localKeyword.trim()) {
      addNotification({
        type: 'warning',
        title: '請輸入搜索關鍵詞',
        message: '請輸入您想要搜索的職位關鍵詞',
      });
      return;
    }
    
    setIsSearching(true);
    
    try {
      // 更新搜索狀態
      setQuery({
        keyword: localKeyword,
        location: localLocation,
      });
      
      // 執行搜索
      await search();
      
      // 導航到搜索頁面
      navigate('/search', { 
        state: { 
          keywords: localKeyword, 
          location: localLocation 
        } 
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: '搜索失敗',
        message: '搜索過程中發生錯誤，請稍後再試',
      });
    } finally {
      setIsSearching(false);
    }
  };
  
  /**
   * 處理熱門關鍵詞點擊
   */
  const handlePopularKeywordClick = (keyword: string) => {
    setLocalKeyword(keyword);
    setQuery({ keyword, location: localLocation });
  };
  
  /**
   * 動畫效果
   */
  useEffect(() => {
    const elements = document.querySelectorAll('.hero-animate');
    elements.forEach((el, index) => {
      setTimeout(() => {
        el.classList.add('animate-fade-in-up');
      }, index * 200);
    });
  }, []);
  
  return (
    <section className={`hero-section position-relative overflow-hidden ${className}`}>
      {/* 背景漸變 */}
      <div className="hero-bg position-absolute top-0 start-0 w-100 h-100">
        <div className="gradient-bg-primary opacity-90"></div>
        <div className="hero-pattern opacity-10"></div>
      </div>
      
      {/* 浮動元素 */}
      <div className="hero-floating-elements position-absolute top-0 start-0 w-100 h-100">
        <div className="floating-shape floating-shape-1"></div>
        <div className="floating-shape floating-shape-2"></div>
        <div className="floating-shape floating-shape-3"></div>
      </div>
      
      <div className="container position-relative py-5">
        <div className="row justify-content-center text-center">
          <div className="col-lg-10 col-xl-8">
            {/* 主標題 */}
            <div className="hero-content mb-5">
              <h1 className="hero-title display-3 fw-bold text-white mb-4 hero-animate opacity-0">
                找到您的
                <span className="gradient-text d-block">
                  理想工作
                </span>
              </h1>
              <p className="hero-subtitle lead text-white-75 mb-5 hero-animate opacity-0">
                JobSpy v2 - 智能職位搜索平台，整合多個求職網站，
                <br className="d-none d-md-block" />
                為您提供最全面、最精準的職位匹配服務
              </p>
            </div>
            
            {/* 搜索表單 */}
            <div className="hero-search-form hero-animate opacity-0">
              <form onSubmit={handleSearch} className="search-form-hero">
                <div className="row g-2 justify-content-center">
                  <div className="col-md-5">
                    <div className="input-group input-group-lg">
                      <span className="input-group-text bg-white border-end-0">
                        <Search className="text-muted" size={20} />
                      </span>
                      <input
                        type="text"
                        className="form-control border-start-0 ps-0"
                        placeholder="輸入職位關鍵詞..."
                        value={localKeyword}
                        onChange={(e) => setLocalKeyword(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="input-group input-group-lg">
                      <span className="input-group-text bg-white border-end-0">
                        <MapPin className="text-muted" size={20} />
                      </span>
                      <input
                        type="text"
                        className="form-control border-start-0 ps-0"
                        placeholder="地點 (可選)"
                        value={localLocation}
                        onChange={(e) => setLocalLocation(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="col-md-3">
                    <button
                      type="submit"
                      className="btn btn-primary btn-lg w-100 btn-gradient"
                      disabled={isSearching}
                    >
                      {isSearching ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          搜索中...
                        </>
                      ) : (
                        '搜索職位'
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>
            
            {/* 熱門關鍵詞 */}
            <div className="hero-popular-keywords mt-4 hero-animate opacity-0">
              <p className="text-white-75 mb-3">熱門搜索：</p>
              <div className="d-flex flex-wrap justify-content-center gap-2">
                {popularKeywords.map((keyword, index) => (
                  <button
                    key={index}
                    type="button"
                    className="btn btn-outline-light btn-sm rounded-pill"
                    onClick={() => handlePopularKeywordClick(keyword)}
                  >
                    {keyword}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
        
        {/* 統計數據 */}
        <div className="row mt-5 pt-5">
          <div className="col-12">
            <div className="hero-stats hero-animate opacity-0">
              <div className="row g-4 justify-content-center">
                {stats.map((stat, index) => {
                  const IconComponent = stat.icon;
                  return (
                    <div key={index} className="col-6 col-md-3">
                      <div className="stat-card text-center">
                        <div className="stat-icon mb-3">
                          <IconComponent className={`${stat.color}`} size={32} />
                        </div>
                        <div className="stat-value h4 fw-bold text-white mb-1">
                          {stat.value}
                        </div>
                        <div className="stat-label text-white-75 small">
                          {stat.label}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 波浪分隔線 */}
      <div className="hero-wave">
        <svg viewBox="0 0 1200 120" preserveAspectRatio="none">
          <path d="M0,0V46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1113-14.29,1200,52.47V0Z" opacity=".25" className="shape-fill"></path>
          <path d="M0,0V15.81C13,36.92,27.64,56.86,47.69,72.05,99.41,111.27,165,111,224.58,91.58c31.15-10.15,60.09-26.07,89.67-39.8,40.92-19,84.73-46,130.83-49.67,36.26-2.85,70.9,9.42,98.6,31.56,31.77,25.39,62.32,62,103.63,73,40.44,10.79,81.35-6.69,119.13-24.28s75.16-39,116.92-43.05c59.73-5.85,113.28,22.88,168.9,38.84,30.2,8.66,59,6.17,87.09-7.5,22.43-10.89,48-26.93,60.65-49.24V0Z" opacity=".5" className="shape-fill"></path>
          <path d="M0,0V5.63C149.93,59,314.09,71.32,475.83,42.57c43-7.64,84.23-20.12,127.61-26.46,59-8.63,112.48,12.24,165.56,35.4C827.93,77.22,886,95.24,951.2,90c86.53-7,172.46-45.71,248.8-84.81V0Z" className="shape-fill"></path>
        </svg>
      </div>
    </section>
  );
};

export default HeroSection;