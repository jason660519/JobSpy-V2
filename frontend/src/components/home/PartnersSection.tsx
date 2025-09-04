/**
 * 首頁合作夥伴和見證區塊組件
 * 展示合作企業和用戶評價見證
 */

import React, { useState, useEffect } from 'react';
import { Star, Quote, ChevronLeft, ChevronRight, Building, Users, Award } from 'lucide-react';

interface Partner {
  id: string;
  name: string;
  logo: string;
  description: string;
  category: 'tech' | 'finance' | 'startup' | 'enterprise';
}

interface Testimonial {
  id: string;
  name: string;
  position: string;
  company: string;
  avatar?: string;
  content: string;
  rating: number;
  date: string;
}

interface PartnersSectionProps {
  className?: string;
}

/**
 * 合作夥伴標誌組件
 */
const PartnerLogo: React.FC<{ partner: Partner }> = ({ partner }) => {
  return (
    <div className="partner-item">
      <div className="partner-card card border-0 shadow-sm h-100 hover-lift">
        <div className="card-body p-4 text-center">
          <div className="partner-logo mb-3">
            {partner.logo ? (
              <img 
                src={partner.logo} 
                alt={partner.name}
                className="img-fluid"
                style={{ maxHeight: '60px', objectFit: 'contain' }}
              />
            ) : (
              <div className="logo-placeholder bg-light rounded d-flex align-items-center justify-content-center" style={{ height: '60px' }}>
                <Building size={32} className="text-muted" />
              </div>
            )}
          </div>
          <h6 className="partner-name fw-bold mb-2">{partner.name}</h6>
          <p className="partner-description text-muted small mb-0">
            {partner.description}
          </p>
        </div>
      </div>
    </div>
  );
};

/**
 * 用戶見證卡片組件
 */
const TestimonialCard: React.FC<{ testimonial: Testimonial }> = ({ testimonial }) => {
  // 渲染星級評分
  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, index) => (
      <Star
        key={index}
        size={16}
        className={index < rating ? 'text-warning' : 'text-muted'}
        fill={index < rating ? 'currentColor' : 'none'}
      />
    ));
  };
  
  return (
    <div className="testimonial-card card border-0 shadow-lg h-100">
      <div className="card-body p-4">
        {/* 引用圖標 */}
        <div className="quote-icon mb-3">
          <Quote size={32} className="text-primary opacity-50" />
        </div>
        
        {/* 評分 */}
        <div className="rating mb-3">
          <div className="d-flex align-items-center">
            {renderStars(testimonial.rating)}
            <span className="ms-2 small text-muted">({testimonial.rating}/5)</span>
          </div>
        </div>
        
        {/* 見證內容 */}
        <blockquote className="testimonial-content mb-4">
          <p className="mb-0 text-muted" style={{ lineHeight: '1.6' }}>
            "{testimonial.content}"
          </p>
        </blockquote>
        
        {/* 用戶信息 */}
        <div className="testimonial-author d-flex align-items-center">
          <div className="author-avatar me-3">
            {testimonial.avatar ? (
              <img 
                src={testimonial.avatar} 
                alt={testimonial.name}
                className="rounded-circle"
                style={{ width: '48px', height: '48px', objectFit: 'cover' }}
              />
            ) : (
              <div className="avatar-placeholder bg-primary rounded-circle d-flex align-items-center justify-content-center" style={{ width: '48px', height: '48px' }}>
                <span className="text-white fw-bold">
                  {testimonial.name.charAt(0)}
                </span>
              </div>
            )}
          </div>
          <div className="author-info">
            <div className="author-name fw-bold">{testimonial.name}</div>
            <div className="author-position small text-muted">
              {testimonial.position} @ {testimonial.company}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 合作夥伴和見證區塊組件
 */
export const PartnersSection: React.FC<PartnersSectionProps> = ({ className = '' }) => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  
  // 模擬合作夥伴數據
  const partners: Partner[] = [
    {
      id: '1',
      name: 'TechCorp',
      logo: '/api/placeholder/120/60',
      description: '領先的科技公司',
      category: 'tech'
    },
    {
      id: '2',
      name: 'StartupXYZ',
      logo: '/api/placeholder/120/60',
      description: '創新新創企業',
      category: 'startup'
    },
    {
      id: '3',
      name: 'FinanceGroup',
      logo: '/api/placeholder/120/60',
      description: '金融服務集團',
      category: 'finance'
    },
    {
      id: '4',
      name: 'Enterprise Inc',
      logo: '/api/placeholder/120/60',
      description: '大型企業集團',
      category: 'enterprise'
    },
    {
      id: '5',
      name: 'CloudTech',
      logo: '/api/placeholder/120/60',
      description: '雲端技術公司',
      category: 'tech'
    },
    {
      id: '6',
      name: 'AI Solutions',
      logo: '/api/placeholder/120/60',
      description: 'AI 解決方案提供商',
      category: 'tech'
    }
  ];
  
  // 模擬用戶見證數據
  const testimonials: Testimonial[] = [
    {
      id: '1',
      name: '王小明',
      position: 'Frontend Developer',
      company: 'TechCorp',
      avatar: '/api/placeholder/48/48',
      content: 'JobSpy v2 真的改變了我的求職體驗！整合多個平台的功能讓我能夠一次搜尋所有職位，而且推薦系統非常精準，幫我找到了現在這份理想的工作。',
      rating: 5,
      date: '2024-01-15'
    },
    {
      id: '2',
      name: '李美華',
      position: 'Product Manager',
      company: 'StartupXYZ',
      avatar: '/api/placeholder/48/48',
      content: '作為一個忙碌的產品經理，JobSpy v2 的智能搜索功能為我節省了大量時間。不用再在多個網站間切換，一個平台就能找到所有相關職位。',
      rating: 5,
      date: '2024-01-10'
    },
    {
      id: '3',
      name: '張志強',
      position: 'Data Scientist',
      company: 'AI Solutions',
      avatar: '/api/placeholder/48/48',
      content: '平台的職位匹配算法很棒，推薦的職位都很符合我的技能和興趣。而且介面設計簡潔直觀，使用起來非常順手。',
      rating: 4,
      date: '2024-01-05'
    },
    {
      id: '4',
      name: '陳雅婷',
      position: 'UX Designer',
      company: 'Design Studio',
      avatar: '/api/placeholder/48/48',
      content: 'JobSpy v2 的移動端體驗非常好，讓我可以隨時隨地查看新職位。收藏和申請功能也很方便，整體使用體驗很棒！',
      rating: 5,
      date: '2023-12-28'
    }
  ];
  
  // 自動輪播見證
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [testimonials.length]);
  
  // 手動切換見證
  const nextTestimonial = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
  };
  
  const prevTestimonial = () => {
    setCurrentTestimonial((prev) => (prev - 1 + testimonials.length) % testimonials.length);
  };
  
  return (
    <section className={`partners-section py-5 bg-light ${className}`}>
      <div className="container">
        {/* 合作夥伴區塊 */}
        <div className="partners-block mb-5">
          {/* 區塊標題 */}
          <div className="row justify-content-center mb-5">
            <div className="col-lg-8 text-center">
              <h2 className="section-title display-5 fw-bold mb-4">
                信任我們的 <span className="gradient-text">合作夥伴</span>
              </h2>
              <p className="section-subtitle lead text-muted">
                與各行各業的優秀企業合作，為求職者提供更多優質職位機會。
              </p>
            </div>
          </div>
          
          {/* 合作夥伴標誌 */}
          <div className="partners-grid">
            <div className="row g-4">
              {partners.map((partner) => (
                <div key={partner.id} className="col-lg-2 col-md-4 col-6">
                  <PartnerLogo partner={partner} />
                </div>
              ))}
            </div>
          </div>
          
          {/* 合作統計 */}
          <div className="row mt-5">
            <div className="col-12">
              <div className="partnership-stats">
                <div className="row text-center">
                  <div className="col-md-4">
                    <div className="stat-item">
                      <Building className="text-primary mb-2" size={32} />
                      <div className="h4 fw-bold mb-1">500+</div>
                      <div className="text-muted small">合作企業</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="stat-item">
                      <Users className="text-success mb-2" size={32} />
                      <div className="h4 fw-bold mb-1">10,000+</div>
                      <div className="text-muted small">活躍雇主</div>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="stat-item">
                      <Award className="text-warning mb-2" size={32} />
                      <div className="h4 fw-bold mb-1">98%</div>
                      <div className="text-muted small">合作滿意度</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 用戶見證區塊 */}
        <div className="testimonials-block">
          {/* 區塊標題 */}
          <div className="row justify-content-center mb-5">
            <div className="col-lg-8 text-center">
              <h2 className="section-title display-5 fw-bold mb-4">
                用戶 <span className="gradient-text">真實評價</span>
              </h2>
              <p className="section-subtitle lead text-muted">
                聽聽成功求職者的真實分享，了解 JobSpy v2 如何改變他們的職涯。
              </p>
            </div>
          </div>
          
          {/* 見證輪播 */}
          <div className="testimonials-carousel">
            <div className="row justify-content-center">
              <div className="col-lg-8">
                <div className="position-relative">
                  {/* 見證卡片 */}
                  <div className="testimonial-wrapper">
                    <TestimonialCard testimonial={testimonials[currentTestimonial]} />
                  </div>
                  
                  {/* 導航按鈕 */}
                  <div className="carousel-controls">
                    <button 
                      className="btn btn-outline-primary rounded-circle position-absolute top-50 start-0 translate-middle-y"
                      style={{ left: '-60px' }}
                      onClick={prevTestimonial}
                      aria-label="上一個見證"
                    >
                      <ChevronLeft size={20} />
                    </button>
                    <button 
                      className="btn btn-outline-primary rounded-circle position-absolute top-50 end-0 translate-middle-y"
                      style={{ right: '-60px' }}
                      onClick={nextTestimonial}
                      aria-label="下一個見證"
                    >
                      <ChevronRight size={20} />
                    </button>
                  </div>
                  
                  {/* 指示器 */}
                  <div className="carousel-indicators d-flex justify-content-center mt-4">
                    {testimonials.map((_, index) => (
                      <button
                        key={index}
                        className={`btn btn-sm rounded-circle mx-1 ${
                          index === currentTestimonial ? 'btn-primary' : 'btn-outline-primary'
                        }`}
                        style={{ width: '12px', height: '12px', padding: 0 }}
                        onClick={() => setCurrentTestimonial(index)}
                        aria-label={`見證 ${index + 1}`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* 見證統計 */}
          <div className="row mt-5">
            <div className="col-12">
              <div className="testimonial-stats">
                <div className="card border-0 shadow-sm">
                  <div className="card-body p-4">
                    <div className="row text-center">
                      <div className="col-md-3">
                        <div className="stat-item">
                          <div className="h3 fw-bold text-primary mb-1">4.8/5</div>
                          <div className="text-muted small">平均評分</div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="stat-item">
                          <div className="h3 fw-bold text-success mb-1">95%</div>
                          <div className="text-muted small">推薦率</div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="stat-item">
                          <div className="h3 fw-bold text-info mb-1">1,200+</div>
                          <div className="text-muted small">用戶評價</div>
                        </div>
                      </div>
                      <div className="col-md-3">
                        <div className="stat-item">
                          <div className="h3 fw-bold text-warning mb-1">30天</div>
                          <div className="text-muted small">平均求職時間</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PartnersSection;