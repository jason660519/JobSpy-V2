/**
 * 登入頁面組件
 * 提供用戶登入功能，包含表單驗證和社交登入選項
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  LogIn, 
  ArrowLeft,
  Github,
  Chrome,
  Linkedin,
  AlertCircle,
  CheckCircle,
  Fingerprint,
  Shield
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 登入表單驗證 Schema
 */
const loginSchema = z.object({
  email: z
    .string()
    .min(1, '請輸入電子郵件')
    .email('請輸入有效的電子郵件格式'),
  password: z
    .string()
    .min(1, '請輸入密碼')
    .min(6, '密碼至少需要 6 個字符'),
  rememberMe: z.boolean().optional()
});

type LoginFormData = z.infer<typeof loginSchema>;

/**
 * 登入頁面組件
 */
export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, socialLogin, isLoading, isAuthenticated } = useAuthStore();
  const { addNotification } = useUIStore();
  
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showBiometricLogin, setShowBiometricLogin] = useState(false);
  
  // 獲取重定向路徑
  const from = (location.state as any)?.from?.pathname || '/';
  
  // 如果已登入，重定向到首頁
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);
  
  // 表單處理
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onChange',
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false
    }
  });
  
  /**
   * 處理表單提交
   */
  const onSubmit = async (data: LoginFormData) => {
    setIsSubmitting(true);
    
    try {
      await login(data.email, data.password, data.rememberMe);
      
      addNotification({
        type: 'success',
        title: '登入成功',
        message: '歡迎回來！',
        duration: 3000
      });
      
      // 重定向到原來的頁面或首頁
      navigate(from, { replace: true });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '登入失敗',
        message: error.message || '登入過程中發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 處理社交登入
   */
  const handleSocialLogin = async (provider: 'google' | 'github' | 'linkedin') => {
    setIsSubmitting(true);
    
    try {
      await socialLogin(provider);
      
      addNotification({
        type: 'success',
        title: '登入成功',
        message: `已透過 ${provider === 'google' ? 'Google' : provider === 'github' ? 'GitHub' : 'LinkedIn'} 成功登入`,
        duration: 3000
      });
      
      navigate(from, { replace: true });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '社交登入失敗',
        message: error.message || '社交登入過程中發生錯誤',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 處理生物識別登入
   */
  const handleBiometricLogin = async () => {
    setIsSubmitting(true);
    
    try {
      // 模擬生物識別登入
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification({
        type: 'success',
        title: '登入成功',
        message: '已透過生物識別驗證登入',
        duration: 3000
      });
      
      // 模擬登入成功
      navigate(from, { replace: true });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '生物識別登入失敗',
        message: error.message || '生物識別驗證失敗',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 切換密碼顯示狀態
   */
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };
  
  return (
    <div className="login-page min-vh-100 d-flex align-items-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-5 col-md-7">
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
            
            {/* 登入卡片 */}
            <div className="card shadow-lg border-0">
              <div className="card-body p-5">
                {/* 標題 */}
                <div className="text-center mb-4">
                  <div className="mb-3">
                    <div className="bg-gradient-primary rounded-circle d-inline-flex align-items-center justify-content-center" style={{width: '60px', height: '60px'}}>
                      <LogIn size={30} className="text-white" />
                    </div>
                  </div>
                  <h2 className="fw-bold mb-2">歡迎回來</h2>
                  <p className="text-muted">登入您的 JobSpy 帳戶</p>
                </div>
                
                {/* 社交登入 */}
                <div className="social-login mb-4">
                  <div className="row g-2">
                    <div className="col-4">
                      <button
                        type="button"
                        className="btn btn-outline-danger w-100 d-flex align-items-center justify-content-center"
                        onClick={() => handleSocialLogin('google')}
                        disabled={isLoading || isSubmitting}
                      >
                        <Chrome size={18} />
                      </button>
                    </div>
                    <div className="col-4">
                      <button
                        type="button"
                        className="btn btn-outline-dark w-100 d-flex align-items-center justify-content-center"
                        onClick={() => handleSocialLogin('github')}
                        disabled={isLoading || isSubmitting}
                      >
                        <Github size={18} />
                      </button>
                    </div>
                    <div className="col-4">
                      <button
                        type="button"
                        className="btn btn-outline-primary w-100 d-flex align-items-center justify-content-center"
                        onClick={() => handleSocialLogin('linkedin')}
                        disabled={isLoading || isSubmitting}
                      >
                        <Linkedin size={18} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="divider my-4">
                    <div className="divider-text text-muted small">或使用電子郵件登入</div>
                  </div>
                </div>
                
                {/* 登入表單 */}
                <form onSubmit={handleSubmit(onSubmit)}>
                  {/* 電子郵件 */}
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">電子郵件</label>
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
                  
                  {/* 密碼 */}
                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">密碼</label>
                    <div className="input-group">
                      <span className="input-group-text">
                        <Lock size={18} />
                      </span>
                      <input
                        type={showPassword ? 'text' : 'password'}
                        className={`form-control ${errors.password ? 'is-invalid' : ''}`}
                        id="password"
                        placeholder="至少 6 個字符"
                        {...register('password')}
                        disabled={isLoading || isSubmitting}
                      />
                      <button
                        type="button"
                        className="btn btn-outline-secondary"
                        onClick={togglePasswordVisibility}
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
                  </div>
                  
                  {/* 記住我 和 忘記密碼 */}
                  <div className="d-flex justify-content-between align-items-center mb-4">
                    <div className="form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="rememberMe"
                        {...register('rememberMe')}
                        disabled={isLoading || isSubmitting}
                      />
                      <label className="form-check-label" htmlFor="rememberMe">
                        記住我
                      </label>
                    </div>
                    <Link to="/forgot-password" className="text-decoration-none">
                      忘記密碼？
                    </Link>
                  </div>
                  
                  {/* 登入按鈕 */}
                  <button
                    type="submit"
                    className="btn btn-primary w-100 mb-3"
                    disabled={isLoading || isSubmitting || !isValid}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        登入中...
                      </>
                    ) : (
                      <>
                        <LogIn size={18} className="me-2" />
                        登入
                      </>
                    )}
                  </button>
                </form>
                
                {/* 生物識別登入 */}
                <div className="text-center mb-3">
                  <button
                    type="button"
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => setShowBiometricLogin(!showBiometricLogin)}
                    disabled={isLoading || isSubmitting}
                  >
                    <Fingerprint size={16} className="me-1" />
                    生物識別登入
                  </button>
                </div>
                
                {showBiometricLogin && (
                  <div className="alert alert-info d-flex align-items-center mb-3">
                    <Shield size={18} className="me-2 flex-shrink-0" />
                    <div>
                      <div className="fw-bold mb-1">安全提示</div>
                      <p className="mb-2 small">
                        生物識別登入提供額外的安全保護層
                      </p>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-primary"
                        onClick={handleBiometricLogin}
                        disabled={isLoading || isSubmitting}
                      >
                        <Fingerprint size={14} className="me-1" />
                        開始驗證
                      </button>
                    </div>
                  </div>
                )}
                
                {/* 註冊連結 */}
                <div className="text-center">
                  <p className="text-muted mb-0">
                    還沒有帳戶？{' '}
                    <Link to="/register" className="text-decoration-none fw-medium">
                      立即註冊
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

export default LoginPage;