/**
 * 職位詳情頁面組件
 * 提供職位詳細資訊展示、申請功能、相似職位推薦等
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  MapPin,
  Calendar,
  DollarSign,
  Clock,
  Users,
  Building,
  Briefcase,
  GraduationCap,
  Heart,
  Share2,
  Send,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  Star,
  Eye,
  Bookmark,
  Flag,
  Globe,
  Phone,
  Mail,
  Award,
  TrendingUp,
  Target,
  Zap,
  Menu,
  X
} from 'lucide-react';
import { useJobStore } from '../stores/jobStore';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 職位詳情頁面組件
 */
export const JobDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { 
    currentJob, 
    similarJobs,
    fetchJobDetails, 
    fetchSimilarJobs,
    toggleFavorite, 
    applyToJob,
    isLoading 
  } = useJobStore();
  const { isAuthenticated, user } = useAuthStore();
  const { addNotification } = useUIStore();
  
  const [isApplying, setIsApplying] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [activeTab, setActiveTab] = useState('description');
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  
  // 載入職位詳情
  useEffect(() => {
    if (id) {
      fetchJobDetails(id);
      fetchSimilarJobs(id);
    }
  }, [id, fetchJobDetails, fetchSimilarJobs]);
  
  /**
   * 處理職位申請
   */
  const handleApply = async () => {
    if (!isAuthenticated) {
      addNotification({
        type: 'warning',
        title: '請先登入',
        message: '申請職位前請先登入您的帳戶',
        duration: 3000
      });
      navigate('/login');
      return;
    }
    
    if (!currentJob) return;
    
    setIsApplying(true);
    
    try {
      await applyToJob(currentJob.id);
      
      addNotification({
        type: 'success',
        title: '申請成功',
        message: '您的申請已提交，我們會盡快與您聯繫',
        duration: 5000
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '申請失敗',
        message: error.message || '申請職位時發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsApplying(false);
    }
  };
  
  /**
   * 處理收藏切換
   */
  const handleToggleFavorite = async () => {
    if (!isAuthenticated) {
      addNotification({
        type: 'warning',
        title: '請先登入',
        message: '收藏職位前請先登入您的帳戶',
        duration: 3000
      });
      return;
    }
    
    if (!currentJob) return;
    
    try {
      await toggleFavorite(currentJob.id);
      
      addNotification({
        type: 'success',
        title: currentJob.isFavorited ? '已取消收藏' : '已加入收藏',
        message: currentJob.isFavorited ? '職位已從收藏中移除' : '職位已加入您的收藏',
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
  const handleShare = () => {
    if (navigator.share && currentJob) {
      navigator.share({
        title: currentJob.title,
        text: `${currentJob.company} - ${currentJob.title}`,
        url: window.location.href
      });
    } else {
      setShowShareModal(true);
    }
  };
  
  /**
   * 複製連結
   */
  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    addNotification({
      type: 'success',
      title: '連結已複製',
      message: '職位連結已複製到剪貼簿',
      duration: 3000
    });
    setShowShareModal(false);
  };
  
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
  
  if (isLoading) {
    return (
      <div className="job-details-page">
        <div className="container py-4">
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
            <div className="text-center">
              <div className="spinner-border text-warning mb-3" role="status">
                <span className="visually-hidden">載入中...</span>
              </div>
              <p className="text-muted">載入職位詳情中...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (!currentJob) {
    return (
      <div className="job-details-page">
        <div className="container py-4">
          <div className="text-center py-5">
            <AlertCircle size={64} className="text-muted mb-3" />
            <h4 className="text-muted mb-3">找不到職位</h4>
            <p className="text-muted mb-4">您要查看的職位可能已被移除或不存在</p>
            <Link to="/search" className="btn btn-warning">
              <ArrowLeft size={16} className="me-2" />
              返回搜尋
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="job-details-page">
      {/* 移動端返回按鈕和菜單 */}
      <div className="d-md-none mb-3">
        <div className="d-flex justify-content-between align-items-center">
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} className="me-2" />
            返回
          </button>
          <button 
            className="btn btn-outline-primary btn-sm"
            onClick={() => setShowMobileMenu(!showMobileMenu)}
          >
            {showMobileMenu ? <X size={16} /> : <Menu size={16} />}
          </button>
        </div>
        
        {/* 移動端菜單 */}
        {showMobileMenu && (
          <div className="mt-2 p-3 bg-light rounded">
            <div className="d-flex gap-2 flex-wrap">
              <button
                className={`btn btn-sm ${activeTab === 'description' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => {
                  setActiveTab('description');
                  setShowMobileMenu(false);
                }}
              >
                職位描述
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'requirements' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => {
                  setActiveTab('requirements');
                  setShowMobileMenu(false);
                }}
              >
                職位要求
              </button>
              <button
                className={`btn btn-sm ${activeTab === 'company' ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => {
                  setActiveTab('company');
                  setShowMobileMenu(false);
                }}
              >
                公司資訊
              </button>
            </div>
          </div>
        )}
      </div>
      
      <div className="container py-4">
        {/* 桌面端返回按鈕 */}
        <div className="d-none d-md-block mb-4">
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft size={16} className="me-2" />
            返回
          </button>
        </div>
        
        <div className="row">
          {/* 主要內容 */}
          <div className="col-lg-8">
            {/* 職位標題卡片 */}
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body p-4">
                <div className="d-flex justify-content-between align-items-start mb-3">
                  <div className="flex-grow-1">
                    <div className="d-flex align-items-center mb-2">
                      <img
                        src={currentJob.companyLogo || `https://ui-avatars.com/api/?name=${currentJob.company}&background=ffc107&color=fff&size=48`}
                        alt={currentJob.company}
                        className="rounded me-3"
                        style={{ width: '48px', height: '48px', objectFit: 'cover' }}
                      />
                      <div>
                        <h1 className="h3 fw-bold mb-1">{currentJob.title}</h1>
                        <p className="text-primary mb-0 fw-semibold">{currentJob.company}</p>
                      </div>
                    </div>
                    
                    {/* 職位基本資訊 */}
                    <div className="job-meta d-flex flex-wrap gap-3 mb-3">
                      <span className="text-muted d-flex align-items-center">
                        <MapPin size={16} className="me-1" />
                        {currentJob.location}
                      </span>
                      <span className="text-muted d-flex align-items-center">
                        <Briefcase size={16} className="me-1" />
                        {currentJob.type}
                      </span>
                      <span className="text-muted d-flex align-items-center">
                        <Clock size={16} className="me-1" />
                        {formatDate(currentJob.postedDate)}
                      </span>
                      <span className="text-muted d-flex align-items-center">
                        <Eye size={16} className="me-1" />
                        {currentJob.views || 0} 次瀏覽
                      </span>
                    </div>
                    
                    {/* 薪資資訊 */}
                    {(currentJob.salaryMin || currentJob.salaryMax) && (
                      <div className="salary-info mb-3">
                        <span className="badge bg-success fs-6 px-3 py-2">
                          <DollarSign size={16} className="me-1" />
                          {formatSalary(currentJob.salaryMin, currentJob.salaryMax)}
                        </span>
                      </div>
                    )}
                    
                    {/* 標籤 */}
                    {currentJob.tags && currentJob.tags.length > 0 && (
                      <div className="job-tags">
                        {currentJob.tags.map((tag, index) => (
                          <span key={index} className="badge bg-light text-dark me-2 mb-2">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  
                  {/* 操作按鈕 */}
                  <div className="action-buttons d-flex flex-column gap-2">
                    <button
                      className="btn btn-outline-secondary btn-sm"
                      onClick={handleToggleFavorite}
                    >
                      <Heart 
                        size={16} 
                        className={currentJob.isFavorited ? 'text-danger' : ''}
                        fill={currentJob.isFavorited ? 'currentColor' : 'none'}
                      />
                    </button>
                    <button
                      className="btn btn-outline-secondary btn-sm"
                      onClick={handleShare}
                    >
                      <Share2 size={16} />
                    </button>
                    <button className="btn btn-outline-secondary btn-sm">
                      <Flag size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            {/* 移動端固定標籤導航 */}
            <div className="d-md-none mobile-tab-navigation mb-4">
              <div className="d-flex">
                <button
                  className={`flex-grow-1 py-3 border-0 ${activeTab === 'description' ? 'btn-primary text-white' : 'btn-light'}`}
                  onClick={() => setActiveTab('description')}
                >
                  職位描述
                </button>
                <button
                  className={`flex-grow-1 py-3 border-0 ${activeTab === 'requirements' ? 'btn-primary text-white' : 'btn-light'}`}
                  onClick={() => setActiveTab('requirements')}
                >
                  職位要求
                </button>
                <button
                  className={`flex-grow-1 py-3 border-0 ${activeTab === 'company' ? 'btn-primary text-white' : 'btn-light'}`}
                  onClick={() => setActiveTab('company')}
                >
                  公司資訊
                </button>
              </div>
            </div>
            
            {/* 內容標籤 */}
            <div className="card border-0 shadow-sm d-none d-md-block">
              <div className="card-header bg-white border-0">
                <ul className="nav nav-tabs card-header-tabs">
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'description' ? 'active' : ''}`}
                      onClick={() => setActiveTab('description')}
                    >
                      職位描述
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'requirements' ? 'active' : ''}`}
                      onClick={() => setActiveTab('requirements')}
                    >
                      職位要求
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'company' ? 'active' : ''}`}
                      onClick={() => setActiveTab('company')}
                    >
                      公司資訊
                    </button>
                  </li>
                </ul>
              </div>
              
              <div className="card-body p-4">
                {/* 職位描述 */}
                {activeTab === 'description' && (
                  <div className="job-description">
                    <h5 className="fw-bold mb-3">職位描述</h5>
                    <div className="content mb-4">
                      {currentJob.description ? (
                        <div dangerouslySetInnerHTML={{ __html: currentJob.description }} />
                      ) : (
                        <p className="text-muted">暫無職位描述</p>
                      )}
                    </div>
                    
                    {/* 職位亮點 */}
                    {currentJob.highlights && currentJob.highlights.length > 0 && (
                      <div className="job-highlights mb-4">
                        <h6 className="fw-bold mb-3">
                          <Zap size={16} className="me-2 text-warning" />
                          職位亮點
                        </h6>
                        <div className="row g-2">
                          {currentJob.highlights.map((highlight, index) => (
                            <div key={index} className="col-md-6">
                              <div className="d-flex align-items-center p-2 bg-light rounded">
                                <CheckCircle size={16} className="text-success me-2 flex-shrink-0" />
                                <span className="small">{highlight}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* 福利待遇 */}
                    {currentJob.benefits && currentJob.benefits.length > 0 && (
                      <div className="job-benefits">
                        <h6 className="fw-bold mb-3">
                          <Award size={16} className="me-2 text-primary" />
                          福利待遇
                        </h6>
                        <div className="row g-2">
                          {currentJob.benefits.map((benefit, index) => (
                            <div key={index} className="col-md-6">
                              <div className="d-flex align-items-center p-2 bg-light rounded">
                                <CheckCircle size={16} className="text-success me-2 flex-shrink-0" />
                                <span className="small">{benefit}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* 職位要求 */}
                {activeTab === 'requirements' && (
                  <div className="job-requirements">
                    <h5 className="fw-bold mb-3">職位要求</h5>
                    
                    {/* 必備技能 */}
                    {currentJob.requiredSkills && currentJob.requiredSkills.length > 0 && (
                      <div className="required-skills mb-4">
                        <h6 className="fw-bold mb-3">
                          <Target size={16} className="me-2 text-danger" />
                          必備技能
                        </h6>
                        <div className="d-flex flex-wrap gap-2">
                          {currentJob.requiredSkills.map((skill, index) => (
                            <span key={index} className="badge bg-primary">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* 加分條件 */}
                    {currentJob.preferredSkills && currentJob.preferredSkills.length > 0 && (
                      <div className="preferred-skills mb-4">
                        <h6 className="fw-bold mb-3">
                          <Star size={16} className="me-2 text-warning" />
                          加分條件
                        </h6>
                        <ul className="list-unstyled">
                          {currentJob.preferredSkills.map((skill, index) => (
                            <li key={index} className="mb-2">
                              <div className="d-flex align-items-center">
                                <Plus size={16} className="text-warning me-2" />
                                <span>{skill}</span>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* 工作經驗 */}
                    {currentJob.experience && (
                      <div className="experience-requirements mb-4">
                        <h6 className="fw-bold mb-3">
                          <TrendingUp size={16} className="me-2 text-info" />
                          工作經驗
                        </h6>
                        <p>{currentJob.experience}</p>
                      </div>
                    )}
                    
                    {/* 學歷要求 */}
                    {currentJob.education && (
                      <div className="education-requirements">
                        <h6 className="fw-bold mb-3">
                          <GraduationCap size={16} className="me-2 text-success" />
                          學歷要求
                        </h6>
                        <p>{currentJob.education}</p>
                      </div>
                    )}
                  </div>
                )}
                
                {/* 公司資訊 */}
                {activeTab === 'company' && (
                  <div className="company-info">
                    <h5 className="fw-bold mb-3">公司資訊</h5>
                    
                    <div className="d-flex align-items-center mb-4">
                      <img
                        src={currentJob.companyLogo || `https://ui-avatars.com/api/?name=${currentJob.company}&background=ffc107&color=fff&size=64`}
                        alt={currentJob.company}
                        className="rounded me-3"
                        style={{ width: '64px', height: '64px', objectFit: 'cover' }}
                      />
                      <div>
                        <h6 className="fw-bold mb-1">{currentJob.company}</h6>
                        <p className="text-muted small mb-1">{currentJob.industry}</p>
                        <div className="d-flex gap-3">
                          <span className="text-muted small">
                            <Users size={14} className="me-1" />
                            {currentJob.companySize || '規模未公開'}
                          </span>
                          <span className="text-muted small">
                            <Globe size={14} className="me-1" />
                            {currentJob.companyLocation || '地點未公開'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* 公司描述 */}
                    {currentJob.companyDescription && (
                      <div className="company-description mb-4">
                        <h6 className="fw-bold mb-3">公司簡介</h6>
                        <p>{currentJob.companyDescription}</p>
                      </div>
                    )}
                    
                    {/* 聯絡資訊 */}
                    <div className="contact-info">
                      <h6 className="fw-bold mb-3">聯絡資訊</h6>
                      <div className="row g-3">
                        <div className="col-md-6">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Phone size={16} className="text-primary me-2" />
                            <span>{currentJob.contactPhone || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Mail size={16} className="text-primary me-2" />
                            <span>{currentJob.contactEmail || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Globe size={16} className="text-primary me-2" />
                            <span>{currentJob.companyWebsite || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-md-6">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <MapPin size={16} className="text-primary me-2" />
                            <span>{currentJob.companyAddress || '未提供'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* 移動端內容區域 */}
            <div className="d-md-none">
              {/* 職位描述 */}
              {activeTab === 'description' && (
                <div className="job-description card border-0 shadow-sm mb-4">
                  <div className="card-body p-4">
                    <h5 className="fw-bold mb-3">職位描述</h5>
                    <div className="content mb-4">
                      {currentJob.description ? (
                        <div dangerouslySetInnerHTML={{ __html: currentJob.description }} />
                      ) : (
                        <p className="text-muted">暫無職位描述</p>
                      )}
                    </div>
                    
                    {/* 職位亮點 */}
                    {currentJob.highlights && currentJob.highlights.length > 0 && (
                      <div className="job-highlights mb-4">
                        <h6 className="fw-bold mb-3">
                          <Zap size={16} className="me-2 text-warning" />
                          職位亮點
                        </h6>
                        <div className="row g-2">
                          {currentJob.highlights.map((highlight, index) => (
                            <div key={index} className="col-12">
                              <div className="d-flex align-items-center p-2 bg-light rounded">
                                <CheckCircle size={16} className="text-success me-2 flex-shrink-0" />
                                <span className="small">{highlight}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* 福利待遇 */}
                    {currentJob.benefits && currentJob.benefits.length > 0 && (
                      <div className="job-benefits">
                        <h6 className="fw-bold mb-3">
                          <Award size={16} className="me-2 text-primary" />
                          福利待遇
                        </h6>
                        <div className="row g-2">
                          {currentJob.benefits.map((benefit, index) => (
                            <div key={index} className="col-12">
                              <div className="d-flex align-items-center p-2 bg-light rounded">
                                <CheckCircle size={16} className="text-success me-2 flex-shrink-0" />
                                <span className="small">{benefit}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* 職位要求 */}
              {activeTab === 'requirements' && (
                <div className="job-requirements card border-0 shadow-sm mb-4">
                  <div className="card-body p-4">
                    <h5 className="fw-bold mb-3">職位要求</h5>
                    
                    {/* 必備技能 */}
                    {currentJob.requiredSkills && currentJob.requiredSkills.length > 0 && (
                      <div className="required-skills mb-4">
                        <h6 className="fw-bold mb-3">
                          <Target size={16} className="me-2 text-danger" />
                          必備技能
                        </h6>
                        <div className="d-flex flex-wrap gap-2">
                          {currentJob.requiredSkills.map((skill, index) => (
                            <span key={index} className="badge bg-primary">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* 加分條件 */}
                    {currentJob.preferredSkills && currentJob.preferredSkills.length > 0 && (
                      <div className="preferred-skills mb-4">
                        <h6 className="fw-bold mb-3">
                          <Star size={16} className="me-2 text-warning" />
                          加分條件
                        </h6>
                        <ul className="list-unstyled">
                          {currentJob.preferredSkills.map((skill, index) => (
                            <li key={index} className="mb-2">
                              <div className="d-flex align-items-center">
                                <Plus size={16} className="text-warning me-2" />
                                <span>{skill}</span>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* 工作經驗 */}
                    {currentJob.experience && (
                      <div className="experience-requirements mb-4">
                        <h6 className="fw-bold mb-3">
                          <TrendingUp size={16} className="me-2 text-info" />
                          工作經驗
                        </h6>
                        <p>{currentJob.experience}</p>
                      </div>
                    )}
                    
                    {/* 學歷要求 */}
                    {currentJob.education && (
                      <div className="education-requirements">
                        <h6 className="fw-bold mb-3">
                          <GraduationCap size={16} className="me-2 text-success" />
                          學歷要求
                        </h6>
                        <p>{currentJob.education}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* 公司資訊 */}
              {activeTab === 'company' && (
                <div className="company-info card border-0 shadow-sm mb-4">
                  <div className="card-body p-4">
                    <h5 className="fw-bold mb-3">公司資訊</h5>
                    
                    <div className="d-flex align-items-center mb-4">
                      <img
                        src={currentJob.companyLogo || `https://ui-avatars.com/api/?name=${currentJob.company}&background=ffc107&color=fff&size=64`}
                        alt={currentJob.company}
                        className="rounded me-3"
                        style={{ width: '64px', height: '64px', objectFit: 'cover' }}
                      />
                      <div>
                        <h6 className="fw-bold mb-1">{currentJob.company}</h6>
                        <p className="text-muted small mb-1">{currentJob.industry}</p>
                        <div className="d-flex gap-3">
                          <span className="text-muted small">
                            <Users size={14} className="me-1" />
                            {currentJob.companySize || '規模未公開'}
                          </span>
                          <span className="text-muted small">
                            <Globe size={14} className="me-1" />
                            {currentJob.companyLocation || '地點未公開'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* 公司描述 */}
                    {currentJob.companyDescription && (
                      <div className="company-description mb-4">
                        <h6 className="fw-bold mb-3">公司簡介</h6>
                        <p>{currentJob.companyDescription}</p>
                      </div>
                    )}
                    
                    {/* 聯絡資訊 */}
                    <div className="contact-info">
                      <h6 className="fw-bold mb-3">聯絡資訊</h6>
                      <div className="row g-3">
                        <div className="col-12">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Phone size={16} className="text-primary me-2" />
                            <span>{currentJob.contactPhone || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Mail size={16} className="text-primary me-2" />
                            <span>{currentJob.contactEmail || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <Globe size={16} className="text-primary me-2" />
                            <span>{currentJob.companyWebsite || '未提供'}</span>
                          </div>
                        </div>
                        <div className="col-12">
                          <div className="d-flex align-items-center p-3 bg-light rounded">
                            <MapPin size={16} className="text-primary me-2" />
                            <span>{currentJob.companyAddress || '未提供'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {/* 相關職位 */}
            {similarJobs && similarJobs.length > 0 && (
              <div className="similar-jobs card border-0 shadow-sm">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="fw-bold mb-0">相關職位推薦</h5>
                </div>
                <div className="card-body p-4">
                  <div className="row g-3">
                    {similarJobs.slice(0, 3).map((job) => (
                      <div key={job.id} className="col-md-12">
                        <div className="d-flex align-items-center p-3 border rounded">
                          <img
                            src={job.companyLogo || `https://ui-avatars.com/api/?name=${job.company}&background=ffc107&color=fff&size=40`}
                            alt={job.company}
                            className="rounded me-3"
                            style={{ width: '40px', height: '40px', objectFit: 'cover' }}
                          />
                          <div className="flex-grow-1 min-w-0">
                            <h6 className="mb-1 text-truncate">{job.title}</h6>
                            <p className="text-muted mb-1 small">{job.company}</p>
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="text-success small fw-medium">
                                {formatSalary(job.salaryMin, job.salaryMax)}
                              </span>
                              <button 
                                className="btn btn-outline-primary btn-sm"
                                onClick={() => navigate(`/jobs/${job.id}`)}
                              >
                                查看
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
          
          {/* 側邊欄 */}
          <div className="col-lg-4 d-none d-lg-block">
            <div className="sticky-top" style={{ top: '100px' }}>
              <div className="card border-0 shadow-sm">
                <div className="card-body p-4">
                  <button
                    className="btn btn-warning w-100 mb-3"
                    onClick={handleApply}
                    disabled={isApplying}
                  >
                    {isApplying ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        申請中...
                      </>
                    ) : (
                      <>
                        <Send size={16} className="me-2" />
                        立即申請這個職位
                      </>
                    )}
                  </button>
                  
                  <button
                    className="btn btn-outline-warning w-100 mb-3"
                    onClick={handleToggleFavorite}
                  >
                    <Heart 
                      size={16} 
                      className="me-2"
                      fill={currentJob.isFavorited ? 'currentColor' : 'none'}
                    />
                    {currentJob.isFavorited ? '已收藏' : '收藏職位'}
                  </button>
                  
                  <button
                    className="btn btn-outline-primary w-100"
                    onClick={handleShare}
                  >
                    <Share2 size={16} className="me-2" />
                    分享職位
                  </button>
                </div>
              </div>
              
              <div className="card border-0 shadow-sm mt-4">
                <div className="card-header bg-white border-0 py-3">
                  <h6 className="fw-bold mb-0">職位統計</h6>
                </div>
                <div className="card-body p-4">
                  <div className="d-flex justify-content-between mb-3">
                    <span className="text-muted">瀏覽次數</span>
                    <span className="fw-bold">{currentJob.views || 0}</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3">
                    <span className="text-muted">申請人數</span>
                    <span className="fw-bold">{currentJob.applications || 0}</span>
                  </div>
                  <div className="d-flex justify-content-between">
                    <span className="text-muted">發布時間</span>
                    <span className="fw-bold">{formatDate(currentJob.postedDate)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 移動端固定申請按鈕 */}
      <div className="d-lg-none mobile-fixed-apply">
        <div className="d-flex gap-2">
          <button
            className="btn btn-outline-warning flex-shrink-0"
            onClick={handleToggleFavorite}
          >
            <Heart 
              size={20} 
              fill={currentJob.isFavorited ? 'currentColor' : 'none'}
            />
          </button>
          <button
            className="btn btn-warning flex-grow-1"
            onClick={handleApply}
            disabled={isApplying}
          >
            {isApplying ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                申請中...
              </>
            ) : (
              <>
                <Send size={16} className="me-2" />
                立即申請
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* 分享模態框 */}
      {showShareModal && (
        <div className="modal show d-block" tabIndex={-1} role="dialog">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">分享職位</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowShareModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="d-grid gap-2">
                  <button 
                    className="btn btn-outline-primary"
                    onClick={handleCopyLink}
                  >
                    <ExternalLink size={16} className="me-2" />
                    複製連結
                  </button>
                  <button 
                    className="btn btn-outline-success"
                    onClick={() => {
                      if (navigator.share) {
                        navigator.share({
                          title: currentJob.title,
                          text: `${currentJob.company} - ${currentJob.title}`,
                          url: window.location.href
                        });
                      }
                    }}
                  >
                    <Share2 size={16} className="me-2" />
                    系統分享
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-backdrop show"></div>
        </div>
      )}
    </div>
  );
};

export default JobDetailsPage;