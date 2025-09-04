/**
 * 首頁統計數據區塊組件
 * 展示平台的成就數據和用戶統計
 */

import React, { useState, useEffect, useRef } from 'react';
import { Briefcase, Users, Building, TrendingUp, Award, Globe, Clock, CheckCircle } from 'lucide-react';

interface StatItem {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  value: number;
  suffix: string;
  label: string;
  color: string;
  description: string;
}

interface StatsSectionProps {
  className?: string;
}

/**
 * 數字動畫 Hook
 */
const useCountUp = (end: number, duration: number = 2000, start: number = 0) => {
  const [count, setCount] = useState(start);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.3 }
    );
    
    if (ref.current) {
      observer.observe(ref.current);
    }
    
    return () => observer.disconnect();
  }, [isVisible]);
  
  useEffect(() => {
    if (!isVisible) return;
    
    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      // 使用 easeOutCubic 緩動函數
      const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
      const currentCount = start + (end - start) * easeOutCubic(progress);
      
      setCount(Math.floor(currentCount));
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [isVisible, end, duration, start]);
  
  return { count, ref };
};

/**
 * 統計數據區塊組件
 */
export const StatsSection: React.FC<StatsSectionProps> = ({ className = '' }) => {
  // 統計數據
  const stats: StatItem[] = [
    {
      icon: Briefcase,
      value: 50000,
      suffix: '+',
      label: '活躍職位',
      color: 'text-primary',
      description: '來自各大求職平台的最新職位'
    },
    {
      icon: Users,
      value: 100000,
      suffix: '+',
      label: '註冊用戶',
      color: 'text-success',
      description: '信任我們的求職者和雇主'
    },
    {
      icon: Building,
      value: 5000,
      suffix: '+',
      label: '合作企業',
      color: 'text-info',
      description: '包括知名企業和新創公司'
    },
    {
      icon: CheckCircle,
      value: 25000,
      suffix: '+',
      label: '成功媒合',
      color: 'text-warning',
      description: '幫助求職者找到理想工作'
    },
    {
      icon: Globe,
      value: 15,
      suffix: '個',
      label: '支持城市',
      color: 'text-danger',
      description: '覆蓋台灣主要城市地區'
    },
    {
      icon: Award,
      value: 98,
      suffix: '%',
      label: '滿意度',
      color: 'text-purple',
      description: '用戶對我們服務的滿意度'
    }
  ];
  
  // 成就里程碑
  const milestones = [
    {
      year: '2023',
      title: 'JobSpy v2 正式上線',
      description: '全新的用戶界面和智能搜索功能'
    },
    {
      year: '2023',
      title: '整合主流求職平台',
      description: '支持 104、LinkedIn、Indeed 等平台'
    },
    {
      year: '2024',
      title: 'AI 智能推薦系統',
      description: '基於機器學習的職位匹配算法'
    },
    {
      year: '2024',
      title: '移動端應用發布',
      description: '完美的移動端求職體驗'
    }
  ];
  
  return (
    <section className={`stats-section py-5 ${className}`}>
      <div className="container">
        {/* 區塊標題 */}
        <div className="row justify-content-center mb-5">
          <div className="col-lg-8 text-center">
            <h2 className="section-title display-5 fw-bold mb-4">
              我們的 <span className="gradient-text">成就數據</span>
            </h2>
            <p className="section-subtitle lead text-muted">
              數字說話，見證 JobSpy v2 在求職市場的影響力和成功。
            </p>
          </div>
        </div>
        
        {/* 統計數據卡片 */}
        <div className="row g-4 mb-5">
          {stats.map((stat, index) => {
            const IconComponent = stat.icon;
            const { count, ref } = useCountUp(stat.value, 2000 + index * 200);
            
            return (
              <div key={index} className="col-lg-4 col-md-6">
                <div ref={ref} className="stat-card card border-0 shadow-sm h-100 hover-lift">
                  <div className="card-body p-4 text-center">
                    <div className="stat-icon mb-3">
                      <IconComponent className={`${stat.color}`} size={48} />
                    </div>
                    <div className="stat-number mb-2">
                      <span className="display-4 fw-bold">
                        {count.toLocaleString()}
                      </span>
                      <span className="h4 fw-bold">{stat.suffix}</span>
                    </div>
                    <h4 className="stat-label h5 fw-bold mb-3">
                      {stat.label}
                    </h4>
                    <p className="stat-description text-muted small mb-0">
                      {stat.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* 成就時間線 */}
        <div className="row">
          <div className="col-12">
            <div className="milestones-section">
              <div className="row justify-content-center mb-4">
                <div className="col-lg-8 text-center">
                  <h3 className="h4 fw-bold mb-4">發展里程碑</h3>
                  <p className="text-muted">
                    回顧我們的發展歷程，見證 JobSpy 的成長軌跡。
                  </p>
                </div>
              </div>
              
              <div className="timeline">
                <div className="row">
                  {milestones.map((milestone, index) => (
                    <div key={index} className="col-lg-3 col-md-6 mb-4">
                      <div className="milestone-item">
                        <div className="milestone-card card border-0 shadow-sm h-100">
                          <div className="card-body p-4">
                            <div className="milestone-year mb-3">
                              <span className="badge bg-primary fs-6 px-3 py-2">
                                {milestone.year}
                              </span>
                            </div>
                            <h5 className="milestone-title fw-bold mb-3">
                              {milestone.title}
                            </h5>
                            <p className="milestone-description text-muted small mb-0">
                              {milestone.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* 信任指標 */}
        <div className="row mt-5">
          <div className="col-12">
            <div className="trust-indicators">
              <div className="card border-0 shadow-lg">
                <div className="card-body p-5">
                  <div className="row align-items-center">
                    <div className="col-lg-6">
                      <h3 className="h4 fw-bold mb-3">
                        值得信賴的求職夥伴
                      </h3>
                      <p className="text-muted mb-4">
                        我們致力於為每一位用戶提供最優質的服務，
                        建立可信賴的求職生態系統。
                      </p>
                      <div className="trust-features">
                        <div className="row g-3">
                          <div className="col-6">
                            <div className="trust-feature d-flex align-items-center">
                              <CheckCircle className="text-success me-2" size={20} />
                              <span className="small">資料安全保護</span>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="trust-feature d-flex align-items-center">
                              <CheckCircle className="text-success me-2" size={20} />
                              <span className="small">24/7 客戶支援</span>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="trust-feature d-flex align-items-center">
                              <CheckCircle className="text-success me-2" size={20} />
                              <span className="small">職位真實驗證</span>
                            </div>
                          </div>
                          <div className="col-6">
                            <div className="trust-feature d-flex align-items-center">
                              <CheckCircle className="text-success me-2" size={20} />
                              <span className="small">免費使用服務</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="col-lg-6">
                      <div className="trust-visual text-center">
                        <div className="trust-badge">
                          <div className="badge-circle bg-gradient-primary d-inline-flex align-items-center justify-content-center" style={{ width: '120px', height: '120px' }}>
                            <Award className="text-white" size={48} />
                          </div>
                          <div className="mt-3">
                            <div className="h5 fw-bold mb-1">認證平台</div>
                            <div className="text-muted small">值得信賴的求職服務</div>
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
      </div>
    </section>
  );
};

export default StatsSection;