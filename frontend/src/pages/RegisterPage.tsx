/**
 * 註冊頁面組件
 * 提供用戶註冊功能，包含表單驗證和社交註冊選項
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  User, 
  UserPlus, 
  ArrowLeft,
  Github,
  Chrome,
  Linkedin,
  AlertCircle,
  CheckCircle,
  Phone,
  Calendar,
  Shield,
  Info
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 註冊表單驗證 Schema
 */
const registerSchema = z.object({
  firstName: z
    .string()
    .min(1, '請輸入名字')
    .min(2, '名字至少需要 2 個字符')
    .max(50, '名字不能超過 50 個字符'),
  lastName: z
    .string()
    .min(1, '請輸入姓氏')
    .min(2, '姓氏至少需要 2 個字符')
    .max(50, '姓氏不能超過 50 個字符'),
  email: z
    .string()
    .min(1, '請輸入電子郵件')
    .email('請輸入有效的電子郵件格式'),
  phone: z
    .string()
    .optional()
    .refine((val) => !val || /^[0-9+\-\s()]+$/.test(val), {
      message: '請輸入有效的電話號碼格式'
    }),
  password: z
    .string()
    .min(8, '密碼至少需要 8 個字符')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '密碼必須包含大小寫字母和數字'),
  confirmPassword: z
    .string()
    .min(1, '請確認密碼'),
  birthDate: z
    .string()
    .optional()
    .refine((val) => {
      if (!val) return true;
      const date = new Date(val);
      const now = new Date();
      const age = now.getFullYear() - date.getFullYear();
      return age >= 16 && age <= 100;
    }, {
      message: '年齡必須在 16-100 歲之間'
    }),
  agreeToTerms: z
    .boolean()
    .refine((val) => val === true, {
      message: '請同意服務條款和隱私政策'
    }),
  subscribeNewsletter: z.boolean().optional()
}).refine((data) => data.password === data.confirmPassword, {
  message: '密碼確認不一致',
  path: ['confirmPassword']
});

type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * 註冊頁面組件
 */
export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register: registerUser, socialLogin, isLoading, isAuthenticated } = useAuthStore();
  const { addNotification } = useUIStore();
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [showPasswordRequirements, setShowPasswordRequirements] = useState(false);
  
  // 如果已登入，重定向到首頁
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/');
    }
  }, [isAuthenticated, navigate]);
  
  // 表單處理
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    trigger
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    mode: 'onChange',
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      password: '',
      confirmPassword: '',
      birthDate: '',
      agreeToTerms: false,
      subscribeNewsletter: false
    }
  });
  
  const watchPassword = watch('password');
  
  /**
   * 處理表單提交
   */
  const onSubmit = async (data: RegisterFormData) => {
    setIsSubmitting(true);
    
    try {
      await registerUser({
        firstName: data.firstName,
        lastName: data.lastName,
        email: data.email,
        phone: data.phone,
        password: data.password,
        birthDate: data.birthDate,
        subscribeNewsletter: data.subscribeNewsletter
      });
      
      addNotification({
        type: 'success',
        title: '註冊成功',
        message: '歡迎加入 JobSpy！請檢查您的電子郵件以驗證帳戶',
        duration: 5000
      });
      
      // 重定向到登入頁面
      navigate('/login', { 
        state: { 
          message: '註冊成功，請登入您的帳戶' 
        } 
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '註冊失敗',
        message: error.message || '註冊過程中發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 處理社交註冊
   */
  const handleSocialRegister = async (provider: 'google' | 'github' | 'linkedin') => {
    setIsSubmitting(true);
    
    try {
      await socialLogin(provider);
      
      addNotification({
        type: 'success',
        title: '註冊成功',
        message: `已透過 ${provider === 'google' ? 'Google' : provider === 'github' ? 'GitHub' : 'LinkedIn'} 成功註冊`,
        duration: 3000
      });
      
      navigate('/');
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '社交註冊失敗',
        message: error.message || '社交註冊過程中發生錯誤',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 切換密碼顯示狀態
   */
  const togglePasswordVisibility = (field: 'password' | 'confirmPassword') => {
    if (field === 'password') {
      setShowPassword(!showPassword);
    } else {
      setShowConfirmPassword(!showConfirmPassword);
    }
  };
  
  /**
   * 處理步驟切換
   */
  const handleNextStep = async () => {
    const fieldsToValidate = currentStep === 1 
      ? ['firstName', 'lastName', 'email'] 
      : ['password', 'confirmPassword'];
    
    const isStepValid = await trigger(fieldsToValidate as any);
    
    if (isStepValid) {
      setCurrentStep(currentStep + 1);
    }
  };
  
  /**
   * 處理步驟返回
   */
  const handlePrevStep = () => {
    setCurrentStep(currentStep - 1);
  };
  
  /**
   * 檢查密碼強度
   */
  const checkPasswordStrength = (password: string) => {
    const requirements = [
      { test: password.length >= 8, text: '至少 8 個字符' },
      { test: /[a-z]/.test(password), text: '包含小寫字母' },
      { test: /[A-Z]/.test(password), text: '包含大寫字母' },
      { test: /\d/.test(password), text: '包含數字' }
    ];
    
    return requirements;
  };
  
  const passwordRequirements = checkPasswordStrength(watchPassword || '');
  
  return (
    <div className="register-page min-vh-100 d-flex align-items-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-8 col-md-10">
            {/* 返回按鈕 */}
            <div className="mb-4">
              <Link 
                to="/" 
                className="btn btn-outline-secondary btn-sm"
              >
                <ArrowLeft size={16} className="me-2" />
                返回首頁
              </Link>
            </div>
            
            {/* 註冊卡片 */}
            <div className="card shadow-lg border-0">
              <div className="card-body p-5">
                {/* 標題 */}
                <div className="text-center mb-4">
                  <div className="mb-3">
                    <div className="bg-gradient-primary rounded-circle d-inline-flex align-items-center justify-content-center" style={{width: '60px', height: '60px'}}>
                      <UserPlus size={30} className="text-white" />
                    </div>
                  </div>
                  <h2 className="fw-bold mb-2">建立帳戶</h2>
                  <p className="text-muted">加入 JobSpy 開始您的求職之旅</p>
                </div>
                
                {/* 步驟指示器 */}
                <div className="d-flex justify-content-center mb-4">
                  <div className="d-flex align-items-center">
                    <div className={`rounded-circle d-flex align-items-center justify-content-center ${currentStep >= 1 ? 'bg-primary text-white' : 'bg-light text-muted'}`} style={{width: '32px', height: '32px'}}>
                      1
                    </div>
                    <div className={`mx-2 ${currentStep > 1 ? 'text-primary' : 'text-muted'}`}>基本資訊</div>
                    
                    <div className="mx-2">•</div>
                    
                    <div className={`rounded-circle d-flex align-items-center justify-content-center ${currentStep >= 2 ? 'bg-primary text-white' : 'bg-light text-muted'}`} style={{width: '32px', height: '32px'}}>
                      2
                    </div>
                    <div className={`mx-2 ${currentStep > 2 ? 'text-primary' : 'text-muted'}`}>密碼設定</div>
                    
                    <div className="mx-2">•</div>
                    
                    <div className={`rounded-circle d-flex align-items-center justify-content-center ${currentStep >= 3 ? 'bg-primary text-white' : 'bg-light text-muted'}`} style={{width: '32px', height: '32px'}}>
                      3
                    </div>
                    <div className={`mx-2 ${currentStep === 3 ? 'text-primary' : 'text-muted'}`}>完成註冊</div>
                  </div>
                </div>
                
                {/* 社交註冊 */}
                {currentStep === 1 && (
                  <div className="social-register mb-4">
                    <div className="row g-2">
                      <div className="col-4">
                        <button
                          type="button"
                          className="btn btn-outline-danger w-100 d-flex align-items-center justify-content-center"
                          onClick={() => handleSocialRegister('google')}
                          disabled={isLoading || isSubmitting}
                        >
                          <Chrome size={18} />
                        </button>
                      </div>
                      <div className="col-4">
                        <button
                          type="button"
                          className="btn btn-outline-dark w-100 d-flex align-items-center justify-content-center"
                          onClick={() => handleSocialRegister('github')}
                          disabled={isLoading || isSubmitting}
                        >
                          <Github size={18} />
                        </button>
                      </div>
                      <div className="col-4">
                        <button
                          type="button"
                          className="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center"
                          onClick={() => handleSocialRegister('linkedin')}
                          disabled={isLoading || isSubmitting}
                        >
                          <Linkedin size={18} />
                        </button>
                      </div>
                    </div>
                    
                    <div className="divider my-4">
                      <div className="divider-text text-muted small">或填寫表單註冊</div>
                    </div>
                  </div>
                )}
                
                {/* 註冊表單 */}
                <form onSubmit={handleSubmit(onSubmit)}>
                  {/* 第一步：基本資訊 */}
                  {currentStep === 1 && (
                    <div>
                      <div className="row g-3">
                        {/* 名字 */}
                        <div className="col-md-6">
                          <label htmlFor="firstName" className="form-label">名字 *</label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <User size={18} />
                            </span>
                            <input
                              type="text"
                              className={`form-control ${errors.firstName ? 'is-invalid' : ''}`}
                              id="firstName"
                              placeholder="請輸入您的名字"
                              {...register('firstName')}
                              disabled={isLoading || isSubmitting}
                            />
                          </div>
                          {errors.firstName && (
                            <div className="invalid-feedback">
                              {errors.firstName.message}
                            </div>
                          )}
                        </div>
                        
                        {/* 姓氏 */}
                        <div className="col-md-6">
                          <label htmlFor="lastName" className="form-label">姓氏 *</label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <User size={18} />
                            </span>
                            <input
                              type="text"
                              className={`form-control ${errors.lastName ? 'is-invalid' : ''}`}
                              id="lastName"
                              placeholder="請輸入您的姓氏"
                              {...register('lastName')}
                              disabled={isLoading || isSubmitting}
                            />
                          </div>
                          {errors.lastName && (
                            <div className="invalid-feedback">
                              {errors.lastName.message}
                            </div>
                          )}
                        </div>
                        
                        {/* 電子郵件 */}
                        <div className="col-12">
                          <label htmlFor="email" className="form-label">電子郵件 *</label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <Mail size={18} />
                            </span>
                            <input
                              type="email"
                              className={`form-control ${errors.email ? 'is-invalid' : ''}`}
                              id="email"
                              placeholder="your@email.com"
                              {...register('email')}
                              disabled={isLoading || isSubmitting}
                            />
                          </div>
                          {errors.email && (
                            <div className="invalid-feedback">
                              {errors.email.message}
                            </div>
                          )}
                        </div>
                        
                        {/* 電話號碼 */}
                        <div className="col-md-6">
                          <label htmlFor="phone" className="form-label">電話號碼</label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <Phone size={18} />
                            </span>
                            <input
                              type="tel"
                              className={`form-control ${errors.phone ? 'is-invalid' : ''}`}
                              id="phone"
                              placeholder="可選填"
                              {...register('phone')}
                              disabled={isLoading || isSubmitting}
                            />
                          </div>
                          {errors.phone && (
                            <div className="invalid-feedback">
                              {errors.phone.message}
                            </div>
                          )}
                        </div>
                        
                        {/* 生日 */}
                        <div className="col-md-6">
                          <label htmlFor="birthDate" className="form-label">生日</label>
                          <div className="input-group">
                            <span className="input-group-text">
                              <Calendar size={18} />
                            </span>
                            <input
                              type="date"
                              className={`form-control ${errors.birthDate ? 'is-invalid' : ''}`}
                              id="birthDate"
                              {...register('birthDate')}
                              disabled={isLoading || isSubmitting}
                            />
                          </div>
                          {errors.birthDate && (
                            <div className="invalid-feedback">
                              {errors.birthDate.message}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      {/* 下一步按鈕 */}
                      <div className="d-flex justify-content-end mt-4">
                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={handleNextStep}
                          disabled={isLoading || isSubmitting}
                        >
                          下一步
                          <ArrowLeft size={18} className="ms-2 rotate-180" />
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* 第二步：密碼設定 */}
                  {currentStep === 2 && (
                    <div>
                      {/* 密碼 */}
                      <div className="mb-3">
                        <label htmlFor="password" className="form-label">密碼 *</label>
                        <div className="input-group">
                          <span className="input-group-text">
                            <Lock size={18} />
                          </span>
                          <input
                            type={showPassword ? 'text' : 'password'}
                            className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                            id="password"
                            placeholder="至少 8 個字符，包含大小寫字母和數字"
                            {...register('password')}
                            disabled={isLoading || isSubmitting}
                            onFocus={() => setShowPasswordRequirements(true)}
                            onBlur={() => setShowPasswordRequirements(false)}
                          />
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={() => togglePasswordVisibility('password')}
                            disabled={isLoading || isSubmitting}
                          >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                          </button>
                        </div>
                        {errors.password && (
                          <div className="invalid-feedback">
                            {errors.password.message}
                          </div>
                        )}
                        
                        {/* 密碼要求提示 */}
                        {showPasswordRequirements && (
                          <div className="mt-2 p-3 bg-light rounded">
                            <div className="d-flex align-items-center mb-2">
                              <Info size={16} className="me-2 text-primary" />
                              <small className="fw-bold">密碼要求</small>
                            </div>
                            <ul className="list-unstyled mb-0">
                              {passwordRequirements.map((req, index) => (
                                <li key={index} className="d-flex align-items-center mb-1">
                                  {req.test ? (
                                    <CheckCircle size={14} className="text-success me-2" />
                                  ) : (
                                    <AlertCircle size={14} className="text-muted me-2" />
                                  )}
                                  <small className={req.test ? 'text-success' : 'text-muted'}>
                                    {req.text}
                                  </small>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                      
                      {/* 確認密碼 */}
                      <div className="mb-4">
                        <label htmlFor="confirmPassword" className="form-label">確認密碼 *</label>
                        <div className="input-group">
                          <span className="input-group-text">
                            <Lock size={18} />
                          </span>
                          <input
                            type={showConfirmPassword ? 'text' : 'password'}
                            className={`form-control ${errors.confirmPassword ? 'is-invalid' : ''}`}
                            id="confirmPassword"
                            placeholder="請再次輸入密碼"
                            {...register('confirmPassword')}
                            disabled={isLoading || isSubmitting}
                          />
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={() => togglePasswordVisibility('confirmPassword')}
                            disabled={isLoading || isSubmitting}
                          >
                            {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                          </button>
                        </div>
                        {errors.confirmPassword && (
                          <div className="invalid-feedback">
                            {errors.confirmPassword.message}
                          </div>
                        )}
                      </div>
                      
                      {/* 上一步和下一步按鈕 */}
                      <div className="d-flex justify-content-between mt-4">
                        <button
                          type="button"
                          className="btn btn-outline-secondary"
                          onClick={handlePrevStep}
                          disabled={isLoading || isSubmitting}
                        >
                          <ArrowLeft size={18} className="me-2" />
                          上一步
                        </button>
                        <button
                          type="button"
                          className="btn btn-primary"
                          onClick={handleNextStep}
                          disabled={isLoading || isSubmitting}
                        >
                          下一步
                          <ArrowLeft size={18} className="ms-2 rotate-180" />
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {/* 第三步：完成註冊 */}
                  {currentStep === 3 && (
                    <div>
                      {/* 服務條款同意 */}
                      <div className="mb-3">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            className={`form-check-input ${errors.agreeToTerms ? 'is-invalid' : ''}`}
                            id="agreeToTerms"
                            {...register('agreeToTerms')}
                            disabled={isLoading || isSubmitting}
                          />
                          <label className="form-check-label" htmlFor="agreeToTerms">
                            我同意 <Link to="/terms" className="text-decoration-none">服務條款</Link> 和 <Link to="/privacy" className="text-decoration-none">隱私政策</Link> *
                          </label>
                        </div>
                        {errors.agreeToTerms && (
                          <div className="invalid-feedback d-block">
                            {errors.agreeToTerms.message}
                          </div>
                        )}
                      </div>
                      
                      {/* 訂閱電子報 */}
                      <div className="mb-4">
                        <div className="form-check">
                          <input
                            type="checkbox"
                            className="form-check-input"
                            id="subscribeNewsletter"
                            {...register('subscribeNewsletter')}
                            disabled={isLoading || isSubmitting}
                          />
                          <label className="form-check-label" htmlFor="subscribeNewsletter">
                            訂閱 JobSpy 電子報（可隨時取消）
                          </label>
                        </div>
                      </div>
                      
                      {/* 註冊按鈕 */}
                      <button
                        type="submit"
                        className="btn btn-primary w-100 mb-3"
                        disabled={isLoading || isSubmitting || !isValid}
                      >
                        {isSubmitting ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            註冊中...
                          </>
                        ) : (
                          <>
                            <UserPlus size={18} className="me-2" />
                            完成註冊
                          </>
                        )}
                      </button>
                      
                      {/* 上一步按鈕 */}
                      <div className="d-flex justify-content-center">
                        <button
                          type="button"
                          className="btn btn-outline-secondary"
                          onClick={handlePrevStep}
                          disabled={isLoading || isSubmitting}
                        >
                          <ArrowLeft size={18} className="me-2" />
                          上一步
                        </button>
                      </div>
                    </div>
                  )}
                </form>
                
                {/* 登入連結 */}
                <div className="text-center mt-4">
                  <p className="text-muted mb-0">
                    已有帳戶？{' '}
                    <Link to="/login" className="text-decoration-none fw-medium">
                      立即登入
                    </Link>
                  </p>
                </div>
              </div>
            </div>
            
            {/* 安全認證標章 */}
            <div className="text-center mt-4">
              <div className="d-flex justify-content-center align-items-center text-muted small">
                <Shield size={14} className="me-1" />
                <span>安全加密保護</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;