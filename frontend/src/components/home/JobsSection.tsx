/**
 * 首頁推薦職位區塊組件
 * 展示熱門職位和推薦職位
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  MapPin, 
  Clock, 
  DollarSign, 
  Building, 
  Users, 
  Star, 
  TrendingUp, 
  Filter,
  ChevronRight,
  Bookmark,
  BookmarkCheck,
  ExternalLink
} from 'lucide-react';
import { useJobStore } from '../../stores/jobStore';
import { useAuthStore } from '../../stores/authStore';
import { useUIStore } from '../../stores/uiStore';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: {
    min?: number;
    max?: number;
    currency: string;
    period: 'monthly' | 'yearly';
  };
  type: 'full-time' | 'part-time' | 'contract' | 'internship';
  experience: string;
  postedAt: string;
  description: string;
  tags: string[];
  isHot?: boolean;
  isFeatured?: boolean;
  companyLogo?: string;
  source: string;
}

interface JobsSectionProps {
  className?: string;
}

/**
 * 職位卡片組件
 */
const JobCard: React.FC<{ job: Job; onSave: (jobId: string) => void; isSaved: boolean }> = ({ 
  job, 
  onSave, 
  isSaved 
}) => {
  const navigate = useNavigate();
  const { addNotification } = useUIStore();
  
  // 格式化薪資
  const formatSalary = (salary?: Job['salary']) => {
    if (!salary) return '面議';
    
    const { min, max, currency, period } = salary;
    const periodText = period === 'monthly' ? '/月' : '/年';
    
    if (min && max) {
      return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()}${periodText}`;
    } else if (min) {
      return `${currency} ${min.toLocaleString()}+${periodText}`;
    } else if (max) {
      return `${currency} ${max.toLocaleString()}以下${periodText}`;
    }
    
    return '面議';
  };
  
  // 格式化發布時間
  const formatPostedTime = (postedAt: string) => {
    const now = new Date();
    const posted = new Date(postedAt);
    const diffInHours = Math.floor((now.getTime() - posted.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return '剛剛發布';
    if (diffInHours < 24) return `${diffInHours} 小時前`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} 天前`;
    
    return posted.toLocaleDateString('zh-TW');
  };
  
  // 處理職位點擊
  const handleJobClick = () => {
    navigate(`/jobs/${job.id}`);
  };
  
  // 處理收藏
  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSave(job.id);
    
    addNotification({
      type: isSaved ? 'info' : 'success',
      title: isSaved ? '已取消收藏' : '已收藏職位',
      message: `職位「${job.title}」${isSaved ? '已從收藏中移除' : '已加入收藏'}`,
      duration: 3000
    });
  };
  
  return (
    <div className="job-card card border-0 shadow-sm h-100 hover-lift" onClick={handleJobClick}>
      <div className="card-body p-4">
        {/* 職位標題和標籤 */}
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div className="flex-grow-1">
            <div className="d-flex align-items-center mb-2">
              <h5 className="job-title fw-bold mb-0 me-2">{job.title}</h5>
              {job.isHot && (
                <span className="badge bg-danger small">
                  <TrendingUp size={12} className="me-1" />
                  熱門
                </span>
              )}
              {job.isFeatured && (
                <span className="badge bg-warning text-dark small ms-1">
                  <Star size={12} className="me-1" />
                  推薦
                </span>
              )}
            </div>
          </div>
          <button 
            className="btn btn-link p-0 text-muted hover-primary"
            onClick={handleSave}
            title={isSaved ? '取消收藏' : '收藏職位'}
          >
            {isSaved ? (
              <BookmarkCheck size={20} className="text-primary" />
            ) : (
              <Bookmark size={20} />
            )}
          </button>
        </div>
        
        {/* 公司信息 */}
        <div className="company-info d-flex align-items-center mb-3">
          {job.companyLogo ? (
            <img 
              src={job.companyLogo} 
              alt={job.company}
              className="company-logo rounded me-3"
              style={{ width: '40px', height: '40px', objectFit: 'cover' }}
            />
          ) : (
            <div className="company-logo-placeholder bg-light rounded d-flex align-items-center justify-content-center me-3" style={{ width: '40px', height: '40px' }}>
              <Building size={20} className="text-muted" />
            </div>
          )}
          <div>
            <div className="company-name fw-semibold">{job.company}</div>
            <div className="job-meta small text-muted">
              <MapPin size={14} className="me-1" />
              {job.location}
            </div>
          </div>
        </div>
        
        {/* 職位詳情 */}
        <div className="job-details mb-3">
          <div className="row g-2">
            <div className="col-12">
              <div className="job-salary d-flex align-items-center text-success">
                <DollarSign size={16} className="me-1" />
                <span className="fw-semibold">{formatSalary(job.salary)}</span>
              </div>
            </div>
            <div className="col-6">
              <div className="job-type small text-muted">
                <Users size={14} className="me-1" />
                {job.type === 'full-time' ? '全職' : 
                 job.type === 'part-time' ? '兼職' : 
                 job.type === 'contract' ? '合約' : '實習'}
              </div>
            </div>
            <div className="col-6">
              <div className="job-experience small text-muted">
                <Clock size={14} className="me-1" />
                {job.experience}
              </div>
            </div>
          </div>
        </div>
        
        {/* 職位描述 */}
        <div className="job-description mb-3">
          <p className="text-muted small mb-0" style={{ 
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {job.description}
          </p>
        </div>
        
        {/* 技能標籤 */}
        {job.tags.length > 0 && (
          <div className="job-tags mb-3">
            <div className="d-flex flex-wrap gap-1">
              {job.tags.slice(0, 3).map((tag, index) => (
                <span key={index} className="badge bg-light text-dark small">
                  {tag}
                </span>
              ))}
              {job.tags.length > 3 && (
                <span className="badge bg-light text-muted small">
                  +{job.tags.length - 3}
                </span>
              )}
            </div>
          </div>
        )}
        
        {/* 底部信息 */}
        <div className="job-footer d-flex justify-content-between align-items-center">
          <div className="job-posted small text-muted">
            {formatPostedTime(job.postedAt)}
          </div>
          <div className="job-source d-flex align-items-center">
            <span className="small text-muted me-2">來源: {job.source}</span>
            <ExternalLink size={14} className="text-muted" />
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * 推薦職位區塊組件
 */
export const JobsSection: React.FC<JobsSectionProps> = ({ className = '' }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const { savedJobs, saveJob, unsaveJob } = useJobStore();
  const [activeTab, setActiveTab] = useState<'hot' | 'recommended' | 'recent'>('hot');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 模擬職位數據
  const mockJobs: Job[] = [
    {
      id: '1',
      title: 'Senior Frontend Developer',
      company: 'TechCorp Taiwan',
      location: '台北市信義區',
      salary: { min: 80000, max: 120000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '3-5年經驗',
      postedAt: '2024-01-15T10:00:00Z',
      description: '我們正在尋找一位經驗豐富的前端開發工程師，負責開發現代化的 Web 應用程式。需要熟悉 React、TypeScript 和現代前端工具鏈。',
      tags: ['React', 'TypeScript', 'JavaScript', 'CSS', 'Git'],
      isHot: true,
      isFeatured: true,
      source: '104人力銀行'
    },
    {
      id: '2',
      title: 'Full Stack Engineer',
      company: 'StartupXYZ',
      location: '台北市松山區',
      salary: { min: 70000, max: 100000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '2-4年經驗',
      postedAt: '2024-01-14T15:30:00Z',
      description: '加入我們的新創團隊，參與產品從零到一的開發過程。需要具備前後端開發能力，熟悉 Node.js 和 React。',
      tags: ['Node.js', 'React', 'MongoDB', 'AWS'],
      isHot: true,
      source: 'LinkedIn'
    },
    {
      id: '3',
      title: 'UI/UX Designer',
      company: 'Design Studio',
      location: '台中市西區',
      salary: { min: 50000, max: 80000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '1-3年經驗',
      postedAt: '2024-01-13T09:15:00Z',
      description: '負責產品的使用者介面和使用者體驗設計，與開發團隊緊密合作，創造優秀的數位產品體驗。',
      tags: ['Figma', 'Sketch', 'Prototyping', 'User Research'],
      isFeatured: true,
      source: 'Indeed'
    },
    {
      id: '4',
      title: 'Data Scientist',
      company: 'AI Solutions Inc.',
      location: '新竹市東區',
      salary: { min: 90000, max: 150000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '3-6年經驗',
      postedAt: '2024-01-12T14:20:00Z',
      description: '運用機器學習和統計分析技術，從大數據中挖掘商業洞察，推動數據驅動的決策制定。',
      tags: ['Python', 'Machine Learning', 'SQL', 'TensorFlow'],
      isHot: true,
      source: '104人力銀行'
    },
    {
      id: '5',
      title: 'DevOps Engineer',
      company: 'CloudTech',
      location: '台北市內湖區',
      salary: { min: 85000, max: 130000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '2-5年經驗',
      postedAt: '2024-01-11T11:45:00Z',
      description: '負責建置和維護 CI/CD 流程，管理雲端基礎設施，確保系統的穩定性和可擴展性。',
      tags: ['Docker', 'Kubernetes', 'AWS', 'Jenkins'],
      source: 'LinkedIn'
    },
    {
      id: '6',
      title: 'Product Manager',
      company: 'E-commerce Giant',
      location: '台北市大安區',
      salary: { min: 100000, max: 160000, currency: 'NT$', period: 'monthly' },
      type: 'full-time',
      experience: '4-7年經驗',
      postedAt: '2024-01-10T16:30:00Z',
      description: '負責產品策略規劃和執行，與跨功能團隊合作，推動產品創新和市場成功。',
      tags: ['Product Strategy', 'Agile', 'Analytics', 'Leadership'],
      isFeatured: true,
      source: 'Indeed'
    }
  ];
  
  // 載入職位數據
  useEffect(() => {
    setLoading(true);
    // 模擬 API 調用
    setTimeout(() => {
      let filteredJobs = [...mockJobs];
      
      switch (activeTab) {
        case 'hot':
          filteredJobs = mockJobs.filter(job => job.isHot);
          break;
        case 'recommended':
          filteredJobs = mockJobs.filter(job => job.isFeatured);
          break;
        case 'recent':
          filteredJobs = mockJobs.sort((a, b) => 
            new Date(b.postedAt).getTime() - new Date(a.postedAt).getTime()
          );
          break;
      }
      
      setJobs(filteredJobs.slice(0, 6));
      setLoading(false);
    }, 500);
  }, [activeTab]);
  
  // 處理職位收藏
  const handleSaveJob = (jobId: string) => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    const isSaved = savedJobs.includes(jobId);
    if (isSaved) {
      unsaveJob(jobId);
    } else {
      saveJob(jobId);
    }
  };
  
  return (
    <section className={`jobs-section py-5 ${className}`}>
      <div className="container">
        {/* 區塊標題 */}
        <div className="row justify-content-center mb-5">
          <div className="col-lg-8 text-center">
            <h2 className="section-title display-5 fw-bold mb-4">
              熱門 <span className="gradient-text">推薦職位</span>
            </h2>
            <p className="section-subtitle lead text-muted">
              精選最新、最熱門的職位機會，為您的職涯發展提供最佳選擇。
            </p>
          </div>
        </div>
        
        {/* 職位分類標籤 */}
        <div className="row justify-content-center mb-4">
          <div className="col-lg-8">
            <div className="job-tabs d-flex justify-content-center">
              <div className="btn-group" role="group">
                <button
                  type="button"
                  className={`btn ${activeTab === 'hot' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveTab('hot')}
                >
                  <TrendingUp size={16} className="me-2" />
                  熱門職位
                </button>
                <button
                  type="button"
                  className={`btn ${activeTab === 'recommended' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveTab('recommended')}
                >
                  <Star size={16} className="me-2" />
                  推薦職位
                </button>
                <button
                  type="button"
                  className={`btn ${activeTab === 'recent' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setActiveTab('recent')}
                >
                  <Clock size={16} className="me-2" />
                  最新職位
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* 職位列表 */}
        <div className="jobs-grid">
          {loading ? (
            <div className="row">
              {[...Array(6)].map((_, index) => (
                <div key={index} className="col-lg-4 col-md-6 mb-4">
                  <div className="card border-0 shadow-sm h-100">
                    <div className="card-body p-4">
                      <div className="placeholder-glow">
                        <div className="placeholder col-8 mb-3"></div>
                        <div className="placeholder col-6 mb-2"></div>
                        <div className="placeholder col-4 mb-3"></div>
                        <div className="placeholder col-12 mb-2"></div>
                        <div className="placeholder col-12 mb-3"></div>
                        <div className="placeholder col-5"></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="row">
              {jobs.map((job) => (
                <div key={job.id} className="col-lg-4 col-md-6 mb-4">
                  <JobCard 
                    job={job} 
                    onSave={handleSaveJob}
                    isSaved={savedJobs.includes(job.id)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* 查看更多按鈕 */}
        <div className="row mt-4">
          <div className="col-12 text-center">
            <button 
              className="btn btn-outline-primary btn-lg"
              onClick={() => navigate('/jobs')}
            >
              查看更多職位
              <ChevronRight size={20} className="ms-2" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default JobsSection;