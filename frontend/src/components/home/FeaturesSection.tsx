/**
 * 首頁特色功能區塊組件
 * 展示 JobSpy v2 平台的主要功能和優勢
 */

import React from 'react';
import {
  Search,
  Zap,
  Shield,
  Bell,
  BarChart3,
  Users,
  Globe,
  Smartphone,
  Clock,
  Target,
  Heart,
  Award
} from 'lucide-react';

interface Feature {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  description: string;
  color: string;
  gradient: string;
}

interface FeaturesSectionProps {
  className?: string;
}

/**
 * 特色功能區塊組件
 */
export const FeaturesSection: React.FC<FeaturesSectionProps> = ({ className = '' }) => {
  // 主要功能特色
  const mainFeatures: Feature[] = [
    {
      icon: Search,
      title: '智能搜索',
      description: '整合多個求職平台，一次搜索獲得最全面的職位信息，節省您的時間和精力。',
      color: 'text-primary',
      gradient: 'gradient-bg-primary'
    },
    {
      icon: Zap,
      title: '即時更新',
      description: '職位信息實時同步更新，確保您第一時間獲得最新的工作機會。',
      color: 'text-warning',
      gradient: 'gradient-bg-warning'
    },
    {
      icon: Target,
      title: '精準匹配',
      description: 'AI 智能算法根據您的技能和偏好，為您推薦最適合的職位。',
      color: 'text-success',
      gradient: 'gradient-bg-success'
    },
    {
      icon: Bell,
      title: '職位提醒',
      description: '設置關鍵詞提醒，新職位發布時立即通知，不錯過任何機會。',
      color: 'text-info',
      gradient: 'gradient-bg-info'
    },
    {
      icon: BarChart3,
      title: '數據分析',
      description: '詳細的市場分析和薪資趨勢，幫助您做出明智的職業決策。',
      color: 'text-danger',
      gradient: 'gradient-bg-danger'
    },
    {
      icon: Shield,
      title: '隱私保護',
      description: '嚴格的隱私保護機制，確保您的個人信息安全無憂。',
      color: 'text-secondary',
      gradient: 'gradient-bg-secondary'
    }
  ];
  
  // 額外優勢
  const additionalFeatures = [
    {
      icon: Globe,
      title: '多平台整合',
      description: '支持 104、LinkedIn、Indeed 等主流求職平台'
    },
    {
      icon: Smartphone,
      title: '移動優先',
      description: '完美的移動端體驗，隨時隨地搜索職位'
    },
    {
      icon: Clock,
      title: '24/7 服務',
      description: '全天候服務，不間斷為您提供最新職位信息'
    },
    {
      icon: Users,
      title: '社群支持',
      description: '活躍的求職者社群，分享經驗和機會'
    },
    {
      icon: Heart,
      title: '個人化體驗',
      description: '根據您的偏好定制個人化的求職體驗'
    },
    {
      icon: Award,
      title: '專業認證',
      description: '經過驗證的企業和職位，確保信息真實可靠'
    }
  ];
  
  return (
    <section className={`features-section py-5 ${className}`}>
      <div className="container">
        {/* 區塊標題 */}
        <div className="row justify-content-center mb-5">
          <div className="col-lg-8 text-center">
            <h2 className="section-title display-5 fw-bold mb-4">
              為什麼選擇 <span className="gradient-text">JobSpy v2</span>？
            </h2>
            <p className="section-subtitle lead text-muted">
              我們致力於為求職者提供最優質的職位搜索體驗，
              讓您的求職之路更加高效和成功。
            </p>
          </div>
        </div>
        
        {/* 主要功能卡片 */}
        <div className="row g-4 mb-5">
          {mainFeatures.map((feature, index) => {
            const IconComponent = feature.icon;
            return (
              <div key={index} className="col-lg-4 col-md-6">
                <div className="feature-card h-100 card border-0 shadow-sm hover-lift">
                  <div className="card-body p-4 text-center">
                    <div className={`feature-icon mb-4 ${feature.gradient} rounded-circle d-inline-flex align-items-center justify-content-center`} style={{ width: '80px', height: '80px' }}>
                      <IconComponent className="text-white" size={32} />
                    </div>
                    <h4 className="feature-title h5 fw-bold mb-3">
                      {feature.title}
                    </h4>
                    <p className="feature-description text-muted mb-0">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* 額外優勢 */}
        <div className="row">
          <div className="col-12">
            <div className="additional-features-section">
              <div className="row justify-content-center mb-4">
                <div className="col-lg-8 text-center">
                  <h3 className="h4 fw-bold mb-4">更多優勢特色</h3>
                </div>
              </div>
              
              <div className="row g-4">
                {additionalFeatures.map((feature, index) => {
                  const IconComponent = feature.icon;
                  return (
                    <div key={index} className="col-lg-4 col-md-6">
                      <div className="additional-feature-item d-flex align-items-start">
                        <div className="feature-icon-small me-3 flex-shrink-0">
                          <div className="icon-wrapper bg-light rounded-circle d-flex align-items-center justify-content-center" style={{ width: '48px', height: '48px' }}>
                            <IconComponent className="text-primary" size={24} />
                          </div>
                        </div>
                        <div className="feature-content">
                          <h5 className="feature-title h6 fw-bold mb-2">
                            {feature.title}
                          </h5>
                          <p className="feature-description text-muted small mb-0">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
        
        {/* CTA 區塊 */}
        <div className="row mt-5">
          <div className="col-12">
            <div className="cta-section text-center">
              <div className="cta-card card border-0 shadow-lg">
                <div className="card-body p-5">
                  <div className="row align-items-center">
                    <div className="col-lg-8">
                      <h3 className="cta-title h4 fw-bold mb-3">
                        準備好開始您的求職之旅了嗎？
                      </h3>
                      <p className="cta-description text-muted mb-lg-0">
                        立即註冊 JobSpy v2，體驗最智能的職位搜索服務，
                        讓我們幫助您找到理想的工作機會。
                      </p>
                    </div>
                    <div className="col-lg-4">
                      <div className="cta-buttons d-flex flex-column flex-sm-row flex-lg-column gap-3">
                        <button className="btn btn-primary btn-lg btn-gradient">
                          免費註冊
                        </button>
                        <button className="btn btn-outline-primary btn-lg">
                          了解更多
                        </button>
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

export default FeaturesSection;