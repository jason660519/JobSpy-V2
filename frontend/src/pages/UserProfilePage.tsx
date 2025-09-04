/**
 * 用戶資料頁面組件
 * 提供用戶個人資料管理、工作經歷、技能專長等資訊展示與編輯功能
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  User,
  Mail,
  Phone,
  Calendar,
  MapPin,
  Building,
  GraduationCap,
  Award,
  Edit,
  Camera,
  Plus,
  Trash2,
  Save,
  X,
  Briefcase,
  Clock,
  DollarSign,
  Target,
  TrendingUp,
  CheckCircle,
  Linkedin,
  Github,
  Twitter,
  Globe,
  Link as LinkIcon
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useUserStore } from '../stores/userStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 工作經歷項目
 */
interface WorkExperience {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  isCurrent: boolean;
  description: string;
  achievements: string[];
}

/**
 * 教育背景項目
 */
interface Education {
  id: string;
  school: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string;
  description: string;
}

/**
 * 技能項目
 */
interface Skill {
  id: string;
  name: string;
  level: number; // 1-5
  category: string;
}

/**
 * 用戶資料頁面組件
 */
export const UserProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user: authUser, isAuthenticated } = useAuthStore();
  const { userProfile, fetchUserProfile, updateUserProfile } = useUserStore();
  const { addNotification } = useUIStore();
  
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    birthDate: '',
    location: '',
    currentPosition: '',
    company: '',
    experience: '',
    education: '',
    skills: [] as string[],
    bio: '',
    jobPreferences: {
      desiredPosition: '',
      desiredSalary: '',
      workLocation: '',
      jobType: '',
      remoteWork: false
    },
    socialLinks: {
      linkedin: '',
      github: '',
      twitter: '',
      website: ''
    },
    workExperience: [] as WorkExperience[],
    educationHistory: [] as Education[]
  });
  
  const [newSkill, setNewSkill] = useState('');
  const [showAvatarUpload, setShowAvatarUpload] = useState(false);
  
  // 檢查認證狀態
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    loadUserProfile();
  }, [isAuthenticated, navigate]);
  
  // 載入用戶資料
  const loadUserProfile = async () => {
    setIsLoading(true);
    try {
      await fetchUserProfile();
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '載入失敗',
        message: error.message || '載入用戶資料時發生錯誤',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // 同步用戶資料到表單
  useEffect(() => {
    if (userProfile) {
      setFormData({
        firstName: userProfile.firstName || '',
        lastName: userProfile.lastName || '',
        email: userProfile.email || '',
        phone: userProfile.phone || '',
        birthDate: userProfile.birthDate || '',
        location: userProfile.location || '',
        currentPosition: userProfile.currentPosition || '',
        company: userProfile.company || '',
        experience: userProfile.experience || '',
        education: userProfile.education || '',
        skills: userProfile.skills || [],
        bio: userProfile.bio || '',
        jobPreferences: {
          desiredPosition: userProfile.jobPreferences?.desiredPosition || '',
          desiredSalary: userProfile.jobPreferences?.desiredSalary || '',
          workLocation: userProfile.jobPreferences?.workLocation || '',
          jobType: userProfile.jobPreferences?.jobType || '',
          remoteWork: userProfile.jobPreferences?.remoteWork || false
        },
        socialLinks: {
          linkedin: userProfile.socialLinks?.linkedin || '',
          github: userProfile.socialLinks?.github || '',
          twitter: userProfile.socialLinks?.twitter || '',
          website: userProfile.socialLinks?.website || ''
        },
        workExperience: userProfile.workExperience || [],
        educationHistory: userProfile.educationHistory || []
      });
    }
  }, [userProfile]);
  
  // 處理表單輸入變化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    // 處理 checkbox
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      if (name.includes('.')) {
        const [parent, child] = name.split('.');
        setFormData(prev => ({
          ...prev,
          [parent]: {
            ...(prev as any)[parent],
            [child]: checked
          }
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          [name]: checked
        }));
      }
      return;
    }
    
    // 處理巢狀物件屬性
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...(prev as any)[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // 處理技能添加
  const handleAddSkill = () => {
    if (newSkill.trim() && !formData.skills.includes(newSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, newSkill.trim()]
      }));
      setNewSkill('');
    }
  };
  
  // 處理技能移除
  const handleRemoveSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }));
  };
  
  // 處理工作經歷添加
  const handleAddWorkExperience = () => {
    const newExperience: WorkExperience = {
      id: Date.now().toString(),
      company: '',
      position: '',
      startDate: '',
      endDate: '',
      isCurrent: false,
      description: '',
      achievements: []
    };
    
    setFormData(prev => ({
      ...prev,
      workExperience: [...prev.workExperience, newExperience]
    }));
  };
  
  // 處理工作經歷更新
  const handleWorkExperienceChange = (id: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      workExperience: prev.workExperience.map(exp => 
        exp.id === id ? { ...exp, [field]: value } : exp
      )
    }));
  };
  
  // 處理工作經歷移除
  const handleRemoveWorkExperience = (id: string) => {
    setFormData(prev => ({
      ...prev,
      workExperience: prev.workExperience.filter(exp => exp.id !== id)
    }));
  };
  
  // 處理教育背景添加
  const handleAddEducation = () => {
    const newEducation: Education = {
      id: Date.now().toString(),
      school: '',
      degree: '',
      field: '',
      startDate: '',
      endDate: '',
      description: ''
    };
    
    setFormData(prev => ({
      ...prev,
      educationHistory: [...prev.educationHistory, newEducation]
    }));
  };
  
  // 處理教育背景更新
  const handleEducationChange = (id: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      educationHistory: prev.educationHistory.map(edu => 
        edu.id === id ? { ...edu, [field]: value } : edu
      )
    }));
  };
  
  // 處理教育背景移除
  const handleRemoveEducation = (id: string) => {
    setFormData(prev => ({
      ...prev,
      educationHistory: prev.educationHistory.filter(edu => edu.id !== id)
    }));
  };
  
  // 處理表單提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await updateUserProfile(formData);
      
      addNotification({
        type: 'success',
        title: '更新成功',
        message: '個人資料已成功更新',
        duration: 3000
      });
      
      setIsEditing(false);
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '更新失敗',
        message: error.message || '更新個人資料時發生錯誤',
        duration: 5000
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // 處理取消編輯
  const handleCancel = () => {
    // 重置表單數據到原始狀態
    if (userProfile) {
      setFormData({
        firstName: userProfile.firstName || '',
        lastName: userProfile.lastName || '',
        email: userProfile.email || '',
        phone: userProfile.phone || '',
        birthDate: userProfile.birthDate || '',
        location: userProfile.location || '',
        currentPosition: userProfile.currentPosition || '',
        company: userProfile.company || '',
        experience: userProfile.experience || '',
        education: userProfile.education || '',
        skills: userProfile.skills || [],
        bio: userProfile.bio || '',
        jobPreferences: {
          desiredPosition: userProfile.jobPreferences?.desiredPosition || '',
          desiredSalary: userProfile.jobPreferences?.desiredSalary || '',
          workLocation: userProfile.jobPreferences?.workLocation || '',
          jobType: userProfile.jobPreferences?.jobType || '',
          remoteWork: userProfile.jobPreferences?.remoteWork || false
        },
        socialLinks: {
          linkedin: userProfile.socialLinks?.linkedin || '',
          github: userProfile.socialLinks?.github || '',
          twitter: userProfile.socialLinks?.twitter || '',
          website: userProfile.socialLinks?.website || ''
        },
        workExperience: userProfile.workExperience || [],
        educationHistory: userProfile.educationHistory || []
      });
    }
    setIsEditing(false);
  };
  
  // 處理頭像上傳
  const handleAvatarUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // 這裡應該調用上傳 API
      addNotification({
        type: 'success',
        title: '上傳成功',
        message: '頭像已更新',
        duration: 3000
      });
      setShowAvatarUpload(false);
    }
  };
  
  // 格式化日期
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('zh-TW');
  };
  
  if (!isAuthenticated) {
    return (
      <div className="user-profile-page">
        <div className="container py-5">
          <div className="text-center">
            <h2>請先登入</h2>
            <p>您需要登入才能查看個人資料</p>
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/login')}
            >
              前往登入
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (isLoading && !userProfile) {
    return (
      <div className="user-profile-page">
        <div className="container py-5">
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">載入中...</span>
              </div>
              <p className="mt-2">載入個人資料中...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="user-profile-page">
      <div className="container py-4">
        {/* 頁面標題和操作按鈕 */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="fw-bold mb-0">個人資料</h2>
          {!isEditing ? (
            <button 
              className="btn btn-outline-primary"
              onClick={() => setIsEditing(true)}
            >
              <Edit size={16} className="me-2" />
              編輯資料
            </button>
          ) : (
            <div className="d-flex gap-2">
              <button 
                className="btn btn-outline-secondary"
                onClick={handleCancel}
                disabled={isLoading}
              >
                <X size={16} className="me-2" />
                取消
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleSubmit}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    儲存中...
                  </>
                ) : (
                  <>
                    <Save size={16} className="me-2" />
                    儲存變更
                  </>
                )}
              </button>
            </div>
          )}
        </div>
        
        {/* 移動端標籤導航 */}
        <div className="d-md-none mb-4">
          <div className="d-flex overflow-auto">
            <button
              className={`flex-shrink-0 px-3 py-2 border-0 ${activeTab === 'profile' ? 'btn-primary text-white' : 'btn-light'}`}
              onClick={() => setActiveTab('profile')}
            >
              個人資料
            </button>
            <button
              className={`flex-shrink-0 px-3 py-2 border-0 ${activeTab === 'experience' ? 'btn-primary text-white' : 'btn-light'}`}
              onClick={() => setActiveTab('experience')}
            >
              工作經歷
            </button>
            <button
              className={`flex-shrink-0 px-3 py-2 border-0 ${activeTab === 'education' ? 'btn-primary text-white' : 'btn-light'}`}
              onClick={() => setActiveTab('education')}
            >
              教育背景
            </button>
            <button
              className={`flex-shrink-0 px-3 py-2 border-0 ${activeTab === 'skills' ? 'btn-primary text-white' : 'btn-light'}`}
              onClick={() => setActiveTab('skills')}
            >
              技能專長
            </button>
            <button
              className={`flex-shrink-0 px-3 py-2 border-0 ${activeTab === 'preferences' ? 'btn-primary text-white' : 'btn-light'}`}
              onClick={() => setActiveTab('preferences')}
            >
              求職偏好
            </button>
          </div>
        </div>
        
        <div className="row">
          {/* 左側欄位 - 個人資訊 */}
          <div className="col-lg-4">
            <div className="card border-0 shadow-sm mb-4">
              <div className="card-body text-center p-4">
                {/* 頭像 */}
                <div className="position-relative d-inline-block mb-3">
                  <div className="bg-light rounded-circle d-flex align-items-center justify-content-center mx-auto" 
                       style={{ width: '120px', height: '120px' }}>
                    <User size={48} className="text-muted" />
                  </div>
                  {isEditing && (
                    <button 
                      className="btn btn-primary btn-sm position-absolute bottom-0 end-0 rounded-circle"
                      style={{ width: '36px', height: '36px' }}
                      onClick={() => setShowAvatarUpload(true)}
                      title="更換頭像"
                    >
                      <Camera size={16} />
                    </button>
                  )}
                </div>
                
                {/* 基本資訊 */}
                <h4 className="fw-bold mb-1">
                  {formData.firstName} {formData.lastName}
                </h4>
                <p className="text-muted mb-3">
                  {formData.currentPosition || '未設定職位'} {formData.company && `@ ${formData.company}`}
                </p>
                
                {/* 社交連結 */}
                <div className="d-flex justify-content-center gap-2 mb-3">
                  {formData.socialLinks.linkedin && (
                    <a href={formData.socialLinks.linkedin} target="_blank" rel="noopener noreferrer" className="btn btn-outline-primary btn-sm rounded-circle">
                      <Linkedin size={16} />
                    </a>
                  )}
                  {formData.socialLinks.github && (
                    <a href={formData.socialLinks.github} target="_blank" rel="noopener noreferrer" className="btn btn-outline-dark btn-sm rounded-circle">
                      <Github size={16} />
                    </a>
                  )}
                  {formData.socialLinks.twitter && (
                    <a href={formData.socialLinks.twitter} target="_blank" rel="noopener noreferrer" className="btn btn-outline-info btn-sm rounded-circle">
                      <Twitter size={16} />
                    </a>
                  )}
                  {formData.socialLinks.website && (
                    <a href={formData.socialLinks.website} target="_blank" rel="noopener noreferrer" className="btn btn-outline-secondary btn-sm rounded-circle">
                      <Globe size={16} />
                    </a>
                  )}
                </div>
                
                {/* 統計資訊 */}
                <div className="row text-center mb-4">
                  <div className="col-4">
                    <div className="fw-bold text-primary">12</div>
                    <small className="text-muted">已申請</small>
                  </div>
                  <div className="col-4">
                    <div className="fw-bold text-success">5</div>
                    <small className="text-muted">面試邀請</small>
                  </div>
                  <div className="col-4">
                    <div className="fw-bold text-warning">8</div>
                    <small className="text-muted">收藏職位</small>
                  </div>
                </div>
                
                {/* 聯絡資訊 */}
                <div className="text-start">
                  <h6 className="fw-bold mb-3">聯絡資訊</h6>
                  <div className="d-flex align-items-center mb-2">
                    <Mail size={16} className="text-muted me-2" />
                    <span>{formData.email}</span>
                  </div>
                  {formData.phone && (
                    <div className="d-flex align-items-center mb-2">
                      <Phone size={16} className="text-muted me-2" />
                      <span>{formData.phone}</span>
                    </div>
                  )}
                  {formData.location && (
                    <div className="d-flex align-items-center mb-2">
                      <MapPin size={16} className="text-muted me-2" />
                      <span>{formData.location}</span>
                    </div>
                  )}
                  {formData.birthDate && (
                    <div className="d-flex align-items-center">
                      <Calendar size={16} className="text-muted me-2" />
                      <span>{formatDate(formData.birthDate)}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* 求職偏好 */}
            <div className="card border-0 shadow-sm d-none d-lg-block">
              <div className="card-header bg-white border-0 py-3">
                <h6 className="fw-bold mb-0">求職偏好</h6>
              </div>
              <div className="card-body p-4">
                <div className="mb-3">
                  <label className="form-label small text-muted">期望職位</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="form-control"
                      name="jobPreferences.desiredPosition"
                      value={formData.jobPreferences.desiredPosition}
                      onChange={handleInputChange}
                    />
                  ) : (
                    <p className="mb-0">{formData.jobPreferences.desiredPosition || '未設定'}</p>
                  )}
                </div>
                
                <div className="mb-3">
                  <label className="form-label small text-muted">期望薪資</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="form-control"
                      name="jobPreferences.desiredSalary"
                      value={formData.jobPreferences.desiredSalary}
                      onChange={handleInputChange}
                    />
                  ) : (
                    <p className="mb-0">{formData.jobPreferences.desiredSalary || '面議'}</p>
                  )}
                </div>
                
                <div className="mb-3">
                  <label className="form-label small text-muted">工作地點</label>
                  {isEditing ? (
                    <input
                      type="text"
                      className="form-control"
                      name="jobPreferences.workLocation"
                      value={formData.jobPreferences.workLocation}
                      onChange={handleInputChange}
                    />
                  ) : (
                    <p className="mb-0">{formData.jobPreferences.workLocation || '不限'}</p>
                  )}
                </div>
                
                <div className="mb-3">
                  <label className="form-label small text-muted">工作類型</label>
                  {isEditing ? (
                    <select
                      className="form-select"
                      name="jobPreferences.jobType"
                      value={formData.jobPreferences.jobType}
                      onChange={handleInputChange}
                    >
                      <option value="">請選擇</option>
                      <option value="fulltime">全職</option>
                      <option value="parttime">兼職</option>
                      <option value="contract">合約</option>
                      <option value="internship">實習</option>
                      <option value="remote">遠端</option>
                    </select>
                  ) : (
                    <p className="mb-0">
                      {formData.jobPreferences.jobType 
                        ? formData.jobPreferences.jobType === 'fulltime' ? '全職' :
                          formData.jobPreferences.jobType === 'parttime' ? '兼職' :
                          formData.jobPreferences.jobType === 'contract' ? '合約' :
                          formData.jobPreferences.jobType === 'internship' ? '實習' : '遠端'
                        : '未設定'}
                    </p>
                  )}
                </div>
                
                <div className="form-check">
                  {isEditing ? (
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="remoteWork"
                      name="jobPreferences.remoteWork"
                      checked={formData.jobPreferences.remoteWork}
                      onChange={handleInputChange}
                    />
                  ) : (
                    <input
                      type="checkbox"
                      className="form-check-input"
                      id="remoteWork"
                      checked={formData.jobPreferences.remoteWork}
                      disabled
                    />
                  )}
                  <label className="form-check-label" htmlFor="remoteWork">
                    可接受遠端工作
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          {/* 右側內容區域 */}
          <div className="col-lg-8">
            {/* 桌面端標籤導航 */}
            <div className="card border-0 shadow-sm mb-4 d-none d-md-block">
              <div className="card-header bg-white border-0">
                <ul className="nav nav-tabs card-header-tabs">
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                      onClick={() => setActiveTab('profile')}
                    >
                      個人資料
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'experience' ? 'active' : ''}`}
                      onClick={() => setActiveTab('experience')}
                    >
                      工作經歷
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'education' ? 'active' : ''}`}
                      onClick={() => setActiveTab('education')}
                    >
                      教育背景
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'skills' ? 'active' : ''}`}
                      onClick={() => setActiveTab('skills')}
                    >
                      技能專長
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'preferences' ? 'active' : ''}`}
                      onClick={() => setActiveTab('preferences')}
                    >
                      求職偏好
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            
            {/* 個人資料標籤內容 */}
            {(activeTab === 'profile' || activeTab === 'all') && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="fw-bold mb-0">個人簡介</h5>
                </div>
                <div className="card-body p-4">
                  {isEditing ? (
                    <textarea
                      className="form-control"
                      rows={4}
                      name="bio"
                      value={formData.bio}
                      onChange={handleInputChange}
                      placeholder="請輸入您的個人簡介..."
                    />
                  ) : (
                    <p className="mb-0">{formData.bio || '暫無個人簡介'}</p>
                  )}
                </div>
              </div>
            )}
            
            {/* 工作經歷標籤內容 */}
            {activeTab === 'experience' && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                  <h5 className="fw-bold mb-0">工作經歷</h5>
                  {isEditing && (
                    <button 
                      className="btn btn-outline-primary btn-sm"
                      onClick={handleAddWorkExperience}
                    >
                      <Plus size={16} className="me-1" />
                      新增經歷
                    </button>
                  )}
                </div>
                <div className="card-body p-4">
                  {formData.workExperience.length === 0 ? (
                    <div className="text-center py-5">
                      <Briefcase size={48} className="text-muted mb-3" />
                      <p className="text-muted">暫無工作經歷</p>
                      {isEditing && (
                        <button 
                          className="btn btn-outline-primary"
                          onClick={handleAddWorkExperience}
                        >
                          <Plus size={16} className="me-1" />
                          新增第一份工作經歷
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className="timeline">
                      {formData.workExperience.map((exp, index) => (
                        <div key={exp.id} className="timeline-item mb-4">
                          <div className="d-flex">
                            <div className="timeline-icon bg-primary text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 me-3" 
                                 style={{ width: '40px', height: '40px' }}>
                              <Briefcase size={20} />
                            </div>
                            <div className="flex-grow-1">
                              {isEditing ? (
                                <>
                                  <div className="row g-3 mb-3">
                                    <div className="col-md-6">
                                      <input
                                        type="text"
                                        className="form-control"
                                        placeholder="公司名稱"
                                        value={exp.company}
                                        onChange={(e) => handleWorkExperienceChange(exp.id, 'company', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-6">
                                      <input
                                        type="text"
                                        className="form-control"
                                        placeholder="職位"
                                        value={exp.position}
                                        onChange={(e) => handleWorkExperienceChange(exp.id, 'position', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-6">
                                      <input
                                        type="date"
                                        className="form-control"
                                        placeholder="開始日期"
                                        value={exp.startDate}
                                        onChange={(e) => handleWorkExperienceChange(exp.id, 'startDate', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-6">
                                      {exp.isCurrent ? (
                                        <input
                                          type="text"
                                          className="form-control"
                                          value="至今"
                                          disabled
                                        />
                                      ) : (
                                        <input
                                          type="date"
                                          className="form-control"
                                          placeholder="結束日期"
                                          value={exp.endDate}
                                          onChange={(e) => handleWorkExperienceChange(exp.id, 'endDate', e.target.value)}
                                        />
                                      )}
                                    </div>
                                    <div className="col-12">
                                      <div className="form-check">
                                        <input
                                          type="checkbox"
                                          className="form-check-input"
                                          id={`current-${exp.id}`}
                                          checked={exp.isCurrent}
                                          onChange={(e) => handleWorkExperienceChange(exp.id, 'isCurrent', e.target.checked)}
                                        />
                                        <label className="form-check-label" htmlFor={`current-${exp.id}`}>
                                          目前在職
                                        </label>
                                      </div>
                                    </div>
                                    <div className="col-12">
                                      <textarea
                                        className="form-control"
                                        rows={3}
                                        placeholder="工作描述"
                                        value={exp.description}
                                        onChange={(e) => handleWorkExperienceChange(exp.id, 'description', e.target.value)}
                                      />
                                    </div>
                                  </div>
                                  <div className="d-flex justify-content-end">
                                    <button
                                      className="btn btn-outline-danger btn-sm"
                                      onClick={() => handleRemoveWorkExperience(exp.id)}
                                    >
                                      <Trash2 size={16} className="me-1" />
                                      刪除
                                    </button>
                                  </div>
                                </>
                              ) : (
                                <>
                                  <h6 className="fw-bold mb-1">{exp.position}</h6>
                                  <p className="text-primary mb-1">{exp.company}</p>
                                  <p className="text-muted small mb-2">
                                    {formatDate(exp.startDate)} - {exp.isCurrent ? '至今' : formatDate(exp.endDate)}
                                  </p>
                                  {exp.description && (
                                    <p className="mb-2">{exp.description}</p>
                                  )}
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* 教育背景標籤內容 */}
            {activeTab === 'education' && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                  <h5 className="fw-bold mb-0">教育背景</h5>
                  {isEditing && (
                    <button 
                      className="btn btn-outline-primary btn-sm"
                      onClick={handleAddEducation}
                    >
                      <Plus size={16} className="me-1" />
                      新增教育背景
                    </button>
                  )}
                </div>
                <div className="card-body p-4">
                  {formData.educationHistory.length === 0 ? (
                    <div className="text-center py-5">
                      <GraduationCap size={48} className="text-muted mb-3" />
                      <p className="text-muted">暫無教育背景</p>
                      {isEditing && (
                        <button 
                          className="btn btn-outline-primary"
                          onClick={handleAddEducation}
                        >
                          <Plus size={16} className="me-1" />
                          新增教育背景
                        </button>
                      )}
                    </div>
                  ) : (
                    <div className="timeline">
                      {formData.educationHistory.map((edu) => (
                        <div key={edu.id} className="timeline-item mb-4">
                          <div className="d-flex">
                            <div className="timeline-icon bg-success text-white rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 me-3" 
                                 style={{ width: '40px', height: '40px' }}>
                              <GraduationCap size={20} />
                            </div>
                            <div className="flex-grow-1">
                              {isEditing ? (
                                <>
                                  <div className="row g-3 mb-3">
                                    <div className="col-md-6">
                                      <input
                                        type="text"
                                        className="form-control"
                                        placeholder="學校名稱"
                                        value={edu.school}
                                        onChange={(e) => handleEducationChange(edu.id, 'school', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-6">
                                      <input
                                        type="text"
                                        className="form-control"
                                        placeholder="學位"
                                        value={edu.degree}
                                        onChange={(e) => handleEducationChange(edu.id, 'degree', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-6">
                                      <input
                                        type="text"
                                        className="form-control"
                                        placeholder="科系"
                                        value={edu.field}
                                        onChange={(e) => handleEducationChange(edu.id, 'field', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-3">
                                      <input
                                        type="date"
                                        className="form-control"
                                        placeholder="開始日期"
                                        value={edu.startDate}
                                        onChange={(e) => handleEducationChange(edu.id, 'startDate', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-md-3">
                                      <input
                                        type="date"
                                        className="form-control"
                                        placeholder="結束日期"
                                        value={edu.endDate}
                                        onChange={(e) => handleEducationChange(edu.id, 'endDate', e.target.value)}
                                      />
                                    </div>
                                    <div className="col-12">
                                      <textarea
                                        className="form-control"
                                        rows={2}
                                        placeholder="描述"
                                        value={edu.description}
                                        onChange={(e) => handleEducationChange(edu.id, 'description', e.target.value)}
                                      />
                                    </div>
                                  </div>
                                  <div className="d-flex justify-content-end">
                                    <button
                                      className="btn btn-outline-danger btn-sm"
                                      onClick={() => handleRemoveEducation(edu.id)}
                                    >
                                      <Trash2 size={16} className="me-1" />
                                      刪除
                                    </button>
                                  </div>
                                </>
                              ) : (
                                <>
                                  <h6 className="fw-bold mb-1">{edu.school}</h6>
                                  <p className="text-primary mb-1">{edu.degree} in {edu.field}</p>
                                  <p className="text-muted small mb-2">
                                    {formatDate(edu.startDate)} - {formatDate(edu.endDate)}
                                  </p>
                                  {edu.description && (
                                    <p className="mb-2">{edu.description}</p>
                                  )}
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* 技能專長標籤內容 */}
            {activeTab === 'skills' && (
              <div className="card border-0 shadow-sm mb-4">
                <div className="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center">
                  <h5 className="fw-bold mb-0">技能專長</h5>
                  {isEditing && (
                    <div className="d-flex gap-2">
                      <input
                        type="text"
                        className="form-control form-control-sm"
                        placeholder="新增技能"
                        value={newSkill}
                        onChange={(e) => setNewSkill(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                      />
                      <button 
                        className="btn btn-outline-primary btn-sm"
                        onClick={handleAddSkill}
                      >
                        <Plus size={16} />
                      </button>
                    </div>
                  )}
                </div>
                <div className="card-body p-4">
                  {formData.skills.length === 0 ? (
                    <div className="text-center py-5">
                      <Award size={48} className="text-muted mb-3" />
                      <p className="text-muted">暫無技能專長</p>
                      {isEditing && (
                        <div className="d-flex gap-2 justify-content-center">
                          <input
                            type="text"
                            className="form-control form-control-sm w-auto"
                            placeholder="新增技能"
                            value={newSkill}
                            onChange={(e) => setNewSkill(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                          />
                          <button 
                            className="btn btn-outline-primary btn-sm"
                            onClick={handleAddSkill}
                          >
                            <Plus size={16} className="me-1" />
                            新增
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="d-flex flex-wrap gap-2">
                      {formData.skills.map((skill, index) => (
                        <span key={index} className="badge bg-primary d-flex align-items-center">
                          {skill}
                          {isEditing && (
                            <button
                              className="btn btn-sm btn-link text-white p-0 ms-1"
                              onClick={() => handleRemoveSkill(skill)}
                            >
                              <X size={14} />
                            </button>
                          )}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            {/* 求職偏好標籤內容 (移動端) */}
            {activeTab === 'preferences' && (
              <div className="card border-0 shadow-sm mb-4 d-md-none">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="fw-bold mb-0">求職偏好</h5>
                </div>
                <div className="card-body p-4">
                  <div className="mb-3">
                    <label className="form-label small text-muted">期望職位</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="form-control"
                        name="jobPreferences.desiredPosition"
                        value={formData.jobPreferences.desiredPosition}
                        onChange={handleInputChange}
                      />
                    ) : (
                      <p className="mb-0">{formData.jobPreferences.desiredPosition || '未設定'}</p>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label small text-muted">期望薪資</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="form-control"
                        name="jobPreferences.desiredSalary"
                        value={formData.jobPreferences.desiredSalary}
                        onChange={handleInputChange}
                      />
                    ) : (
                      <p className="mb-0">{formData.jobPreferences.desiredSalary || '面議'}</p>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label small text-muted">工作地點</label>
                    {isEditing ? (
                      <input
                        type="text"
                        className="form-control"
                        name="jobPreferences.workLocation"
                        value={formData.jobPreferences.workLocation}
                        onChange={handleInputChange}
                      />
                    ) : (
                      <p className="mb-0">{formData.jobPreferences.workLocation || '不限'}</p>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label small text-muted">工作類型</label>
                    {isEditing ? (
                      <select
                        className="form-select"
                        name="jobPreferences.jobType"
                        value={formData.jobPreferences.jobType}
                        onChange={handleInputChange}
                      >
                        <option value="">請選擇</option>
                        <option value="fulltime">全職</option>
                        <option value="parttime">兼職</option>
                        <option value="contract">合約</option>
                        <option value="internship">實習</option>
                        <option value="remote">遠端</option>
                      </select>
                    ) : (
                      <p className="mb-0">
                        {formData.jobPreferences.jobType 
                          ? formData.jobPreferences.jobType === 'fulltime' ? '全職' :
                            formData.jobPreferences.jobType === 'parttime' ? '兼職' :
                            formData.jobPreferences.jobType === 'contract' ? '合約' :
                            formData.jobPreferences.jobType === 'internship' ? '實習' : '遠端'
                          : '未設定'}
                      </p>
                    )}
                  </div>
                  
                  <div className="form-check">
                    {isEditing ? (
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="remoteWorkMobile"
                        name="jobPreferences.remoteWork"
                        checked={formData.jobPreferences.remoteWork}
                        onChange={handleInputChange}
                      />
                    ) : (
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="remoteWorkMobile"
                        checked={formData.jobPreferences.remoteWork}
                        disabled
                      />
                    )}
                    <label className="form-check-label" htmlFor="remoteWorkMobile">
                      可接受遠端工作
                    </label>
                  </div>
                </div>
              </div>
            )}
            
            {/* 社交連結 (編輯模式) */}
            {isEditing && (
              <div className="card border-0 shadow-sm">
                <div className="card-header bg-white border-0 py-3">
                  <h5 className="fw-bold mb-0">社交連結</h5>
                </div>
                <div className="card-body p-4">
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label small text-muted">
                        <Linkedin size={14} className="me-1" />
                        LinkedIn
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        name="socialLinks.linkedin"
                        value={formData.socialLinks.linkedin}
                        onChange={handleInputChange}
                        placeholder="https://linkedin.com/in/username"
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small text-muted">
                        <Github size={14} className="me-1" />
                        GitHub
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        name="socialLinks.github"
                        value={formData.socialLinks.github}
                        onChange={handleInputChange}
                        placeholder="https://github.com/username"
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small text-muted">
                        <Twitter size={14} className="me-1" />
                        Twitter
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        name="socialLinks.twitter"
                        value={formData.socialLinks.twitter}
                        onChange={handleInputChange}
                        placeholder="https://twitter.com/username"
                      />
                    </div>
                    <div className="col-md-6">
                      <label className="form-label small text-muted">
                        <Globe size={14} className="me-1" />
                        個人網站
                      </label>
                      <input
                        type="url"
                        className="form-control"
                        name="socialLinks.website"
                        value={formData.socialLinks.website}
                        onChange={handleInputChange}
                        placeholder="https://yourwebsite.com"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* 頭像上傳模態框 */}
      {showAvatarUpload && (
        <div className="modal show d-block" tabIndex={-1} role="dialog">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">更換頭像</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowAvatarUpload(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="text-center">
                  <div className="mb-3">
                    <div className="bg-light rounded-circle d-flex align-items-center justify-content-center mx-auto" 
                         style={{ width: '120px', height: '120px' }}>
                      <User size={48} className="text-muted" />
                    </div>
                  </div>
                  <input
                    type="file"
                    className="form-control mb-3"
                    accept="image/*"
                    onChange={handleAvatarUpload}
                  />
                  <p className="text-muted small">支援 JPG, PNG 格式，檔案大小不超過 2MB</p>
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

export default UserProfilePage;