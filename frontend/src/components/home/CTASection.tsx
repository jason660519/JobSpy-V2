/**
 * 首頁 CTA（Call To Action）區塊組件
 * 鼓勵用戶註冊和開始使用平台
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowRight, 
  Mail, 
  User, 
  Zap, 
  Shield, 
  Clock, 
  CheckCircle,
  Sparkles,
  Target,
  TrendingUp
} from 'lucide-react';
import { useAuthStore } from '../../stores/authStore';
import { useUIStore } from '../../stores/uiStore';

interface CTASectionProps {
  className?: string;
}

/**
 * CTA 區塊組件
 */
export const CTASection: React.FC<CTASectionProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const { addNotification } = useUIStore();
  const [email, setEmail] = useState('');
  const [isSubscribing, setIsSubscribing] = useState(false);
  
  // 處理註冊按鈕點擊
  const handleSignUp = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
  };
  
  // 處理開始搜索按鈕點擊
  const handleStartSearch = () => {
    navigate('/');
  };
  
  // 處理電子報訂閱
  const handleNewsletterSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      addNotification({
        type: 'error',
        title: '請輸入電子郵件',
        message: '請輸入有效的電子郵件地址',
        duration: 3000
      });
      return;
    }
    
    setIsSubscribing(true);
    
    try {
      // 模擬 API 調用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification({
        type: 'success',
        title: '訂閱成功！',
        message: '感謝您訂閱我們的電子報，您將收到最新的職位推薦和求職資訊。',
        duration: 5000
      });
      
      setEmail('');
    } catch (error) {
      addNotification({
        type: 'error',
        title: '訂閱失敗',
        message: '訂閱過程中發生錯誤，請稍後再試。',
        duration: 3000
      });
    } finally {
      setIsSubscribing(false);
    }
  };
  
  // 平台優勢
  const advantages = [
    {
      icon: Zap,
      title: '快速搜索',
      description: '一鍵搜索多個平台'
    },
    {
      icon: Shield,
      title: '安全可靠',
      description: '保護您的隱私資料'
    },
    {
      icon: Clock,
      title: '即時更新',
      description: '最新職位即時推送'
    },
    {
      icon: Target,
      title: '精準匹配',
      description: 'AI 智能職位推薦'
    }
  ];
  
  return (
    <section className={`cta-section py-5 ${className}`}>
      <div className="container">
        {/* 主要 CTA 區塊 */}
        <div className="main-cta mb-5">
          <div className="row justify-content-center">
            <div className="col-lg-10">
              <div className="cta-card card border-0 shadow-lg overflow-hidden">
                <div className="card-body p-0">
                  <div className="row g-0">
                    {/* 左側內容 */}
                    <div className="col-lg-8">
                      <div className="cta-content p-5">
                        <div className="cta-badge mb-4">
                          <span className="badge bg-primary fs-6 px-3 py-2">
                            <Sparkles size={16} className="me-2" />
                            開始您的職涯新旅程
                          </span>
                        </div>
                        
                        <h2 className="cta-title display-4 fw-bold mb-4">
                          準備好找到您的
                          <span className="gradient-text d-block">理想工作了嗎？</span>
                        </h2>
                        
                        <p className="cta-description lead text-muted mb-4">
                          加入 JobSpy v2，體驗最智能的求職平台。
                          我們整合了多個求職網站，為您提供最全面的職位搜索體驗。
                        </p>
                        
                        {/* 平台優勢 */}
                        <div className="advantages-grid mb-4">
                          <div className="row g-3">
                            {advantages.map((advantage, index) => {
                              const IconComponent = advantage.icon;
                              return (
                                <div key={index} className="col-6">
                                  <div className="advantage-item d-flex align-items-center">
                                    <div className="advantage-icon me-3">
                                      <IconComponent size={20} className="text-primary" />
                                    </div>
                                    <div>
                                      <div className="advantage-title fw-semibold small">
                                        {advantage.title}
                                      </div>
                                      <div className="advantage-description text-muted" style={{ fontSize: '0.75rem' }}>
                                        {advantage.description}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                        
                        {/* CTA 按鈕 */}
                        <div className="cta-buttons d-flex flex-wrap gap-3">
                          <button 
                            className="btn btn-primary btn-lg px-4 py-3"
                            onClick={handleSignUp}
                          >
                            <User size={20} className="me-2" />
                            {isAuthenticated ? '前往控制台' : '免費註冊'}
                            <ArrowRight size={20} className="ms-2" />
                          </button>
                          <button 
                            className="btn btn-outline-primary btn-lg px-4 py-3"
                            onClick={handleStartSearch}
                          >
                            立即搜索職位
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    {/* 右側視覺元素 */}
                    <div className="col-lg-4">
                      <div className="cta-visual bg-gradient-primary h-100 d-flex align-items-center justify-content-center position-relative">
                        {/* 背景裝飾 */}
                        <div className="position-absolute top-0 start-0 w-100 h-100 opacity-10">
                          <div className="floating-elements">
                            <div className="floating-element" style={{ top: '20%', left: '20%', animationDelay: '0s' }}>
                              <TrendingUp size={24} className="text-white" />
                            </div>
                            <div className="floating-element" style={{ top: '60%', right: '20%', animationDelay: '1s' }}>
                              <Target size={20} className="text-white" />
                            </div>
                            <div className="floating-element" style={{ bottom: '30%', left: '30%', animationDelay: '2s' }}>
                              <Zap size={18} className="text-white" />
                            </div>
                          </div>
                        </div>
                        
                        {/* 主要圖標 */}
                        <div className="cta-icon text-center">
                          <div className="icon-circle bg-white bg-opacity-20 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style={{ width: '80px', height: '80px' }}>
                            <Sparkles size={40} className="text-white" />
                          </div>
                          <div className="text-white">
                            <div className="h5 fw-bold mb-1">開始探索</div>
                            <div className="small opacity-75">無限可能</div>
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
        
        {/* 電子報訂閱區塊 */}
        <div className="newsletter-section">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="newsletter-card card border-0 shadow-sm">
                <div className="card-body p-4">
                  <div className="row align-items-center">
                    <div className="col-lg-6">
                      <div className="newsletter-content">
                        <h3 className="h5 fw-bold mb-2">
                          <Mail size={24} className="text-primary me-2" />
                          訂閱職位推薦
                        </h3>
                        <p className="text-muted mb-0">
                          每週收到最新的職位推薦和求職資訊，
                          不錯過任何機會。
                        </p>
                      </div>
                    </div>
                    <div className="col-lg-6">
                      <form onSubmit={handleNewsletterSubscribe} className="newsletter-form">
                        <div className="input-group">
                          <input
                            type="email"
                            className="form-control"
                            placeholder="輸入您的電子郵件"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isSubscribing}
                          />
                          <button 
                            className="btn btn-primary"
                            type="submit"
                            disabled={isSubscribing}
                          >
                            {isSubscribing ? (
                              <div className="spinner-border spinner-border-sm" role="status">
                                <span className="visually-hidden">Loading...</span>
                              </div>
                            ) : (
                              '訂閱'
                            )}
                          </button>
                        </div>
                      </form>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 信任指標 */}
        <div className="trust-section mt-5">
          <div className="row">
            <div className="col-12">
              <div className="trust-indicators text-center">
                <div className="row">
                  <div className="col-md-3">
                    <div className="trust-item">
                      <CheckCircle className="text-success mb-2" size={32} />
                      <div className="h6 fw-bold mb-1">100% 免費</div>
                      <div className="text-muted small">永久免費使用</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="trust-item">
                      <Shield className="text-primary mb-2" size={32} />
                      <div className="h6 fw-bold mb-1">隱私保護</div>
                      <div className="text-muted small">資料安全加密</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="trust-item">
                      <Clock className="text-info mb-2" size={32} />
                      <div className="h6 fw-bold mb-1">24/7 支援</div>
                      <div className="text-muted small">全天候客戶服務</div>
                    </div>
                  </div>
                  <div className="col-md-3">
                    <div className="trust-item">
                      <TrendingUp className="text-warning mb-2" size={32} />
                      <div className="h6 fw-bold mb-1">持續更新</div>
                      <div className="text-muted small">功能不斷優化</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* CSS 動畫樣式已移至內聯樣式 */}
    </section>
  );
};

export default CTASection;