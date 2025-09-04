/**
 * 忘記密碼頁面組件
 * 提供密碼重設功能
 */

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Mail, 
  ArrowLeft,
  Send,
  CheckCircle,
  AlertCircle,
  RefreshCw
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';

/**
 * 忘記密碼表單驗證 Schema
 */
const forgotPasswordSchema = z.object({
  email: z
    .string()
    .min(1, '請輸入電子郵件')
    .email('請輸入有效的電子郵件格式')
});

type ForgotPasswordFormData = z.infer<typeof forgotPasswordSchema>;

/**
 * 忘記密碼頁面組件
 */
export const ForgotPasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { resetPassword, isLoading } = useAuthStore();
  const { addNotification } = useUIStore();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isEmailSent, setIsEmailSent] = useState(false);
  const [countdown, setCountdown] = useState(0);
  
  // 表單處理
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    watch,
    getValues
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    mode: 'onChange'
  });
  
  /**
   * 處理表單提交
   */
  const onSubmit = async (data: ForgotPasswordFormData) => {
    setIsSubmitting(true);
    
    try {
      await resetPassword(data.email);
      
      setIsEmailSent(true);
      startCountdown();
      
      addNotification({
        type: 'success',
        title: '重設郵件已發送',
        message: '請檢查您的電子郵件，並點擊重設密碼連結',
        duration: 5000
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '發送失敗',
        message: error.message || '發送重設郵件時發生錯誤，請稍後再試',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 重新發送郵件
   */
  const handleResendEmail = async () => {
    if (countdown > 0) return;
    
    const email = getValues('email');
    if (!email) return;
    
    setIsSubmitting(true);
    
    try {
      await resetPassword(email);
      
      startCountdown();
      
      addNotification({
        type: 'success',
        title: '重設郵件已重新發送',
        message: '請檢查您的電子郵件',
        duration: 3000
      });
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: '重新發送失敗',
        message: error.message || '重新發送郵件時發生錯誤',
        duration: 5000
      });
    } finally {
      setIsSubmitting(false);
    }
  };
  
  /**
   * 開始倒數計時
   */
  const startCountdown = () => {
    setCountdown(60);
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };
  
  /**
   * 返回登入頁面
   */
  const handleBackToLogin = () => {
    navigate('/login');
  };
  
  return (
    <div className="forgot-password-page min-vh-100 d-flex align-items-center bg-light">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-5 col-md-7">
            {/* 返回按鈕 */}
            <div className="mb-4">
              <Link 
                to="/login" 
                className="btn btn-outline-secondary btn-sm"
              >
                <ArrowLeft size={16} className="me-2" />
                返回登入
              </Link>
            </div>
            
            {/* 忘記密碼卡片 */}
            <div className="card shadow-lg border-0">
              <div className="card-body p-5">
                {!isEmailSent ? (
                  // 輸入郵件階段
                  <>
                    {/* 標題 */}
                    <div className="text-center mb-4">
                      <div className="mb-3">
                        <div className="bg-warning rounded-circle d-inline-flex align-items-center justify-content-center" style={{width: '60px', height: '60px'}}>
                          <Mail size={30} className="text-white" />
                        </div>
                      </div>
                      <h2 className="fw-bold mb-2">忘記密碼？</h2>
                      <p className="text-muted">
                        請輸入您的電子郵件地址，我們將發送重設密碼的連結給您
                      </p>
                    </div>
                    
                    {/* 忘記密碼表單 */}
                    <form onSubmit={handleSubmit(onSubmit)}>
                      {/* 電子郵件 */}
                      <div className="mb-4">
                        <label htmlFor="email" className="form-label fw-semibold">
                          <Mail size={16} className="me-2" />
                          電子郵件 *
                        </label>
                        <input
                          type="email"
                          className={`form-control form-control-lg ${
                            errors.email ? 'is-invalid' : 
                            watch('email') && !errors.email ? 'is-valid' : ''
                          }`}
                          id="email"
                          placeholder="請輸入您註冊時使用的電子郵件"
                          {...register('email')}
                        />
                        {errors.email && (
                          <div className="invalid-feedback d-flex align-items-center">
                            <AlertCircle size={16} className="me-1" />
                            {errors.email.message}
                          </div>
                        )}
                        {watch('email') && !errors.email && (
                          <div className="valid-feedback d-flex align-items-center">
                            <CheckCircle size={16} className="me-1" />
                            電子郵件格式正確
                          </div>
                        )}
                      </div>
                      
                      {/* 發送按鈕 */}
                      <button
                        type="submit"
                        className="btn btn-warning btn-lg w-100 mb-3"
                        disabled={isSubmitting || !isValid}
                      >
                        {isSubmitting ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            發送中...
                          </>
                        ) : (
                          <>
                            <Send size={20} className="me-2" />
                            發送重設連結
                          </>
                        )}
                      </button>
                    </form>
                  </>
                ) : (
                  // 郵件已發送階段
                  <>
                    {/* 成功標題 */}
                    <div className="text-center mb-4">
                      <div className="mb-3">
                        <div className="bg-success rounded-circle d-inline-flex align-items-center justify-content-center" style={{width: '60px', height: '60px'}}>
                          <CheckCircle size={30} className="text-white" />
                        </div>
                      </div>
                      <h2 className="fw-bold mb-2">郵件已發送</h2>
                      <p className="text-muted">
                        我們已將重設密碼的連結發送到
                        <br />
                        <strong>{getValues('email')}</strong>
                      </p>
                    </div>
                    
                    {/* 說明和操作 */}
                    <div className="instructions mb-4">
                      <div className="alert alert-info border-0">
                        <h6 className="fw-bold mb-2">接下來該怎麼做？</h6>
                        <ol className="mb-0 ps-3">
                          <li>檢查您的電子郵件收件匣</li>
                          <li>點擊郵件中的「重設密碼」連結</li>
                          <li>設定您的新密碼</li>
                          <li>使用新密碼登入</li>
                        </ol>
                      </div>
                      
                      <div className="alert alert-warning border-0">
                        <small>
                          <strong>注意：</strong>
                          如果您沒有收到郵件，請檢查垃圾郵件資料夾。
                          重設連結將在 24 小時後失效。
                        </small>
                      </div>
                    </div>
                    
                    {/* 重新發送按鈕 */}
                    <button
                      type="button"
                      className="btn btn-outline-warning w-100 mb-3"
                      onClick={handleResendEmail}
                      disabled={isSubmitting || countdown > 0}
                    >
                      {isSubmitting ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                          重新發送中...
                        </>
                      ) : countdown > 0 ? (
                        <>
                          <RefreshCw size={20} className="me-2" />
                          重新發送 ({countdown}s)
                        </>
                      ) : (
                        <>
                          <RefreshCw size={20} className="me-2" />
                          重新發送郵件
                        </>
                      )}
                    </button>
                    
                    {/* 返回登入按鈕 */}
                    <button
                      type="button"
                      className="btn btn-primary w-100"
                      onClick={handleBackToLogin}
                    >
                      返回登入頁面
                    </button>
                  </>
                )}
                
                {/* 幫助連結 */}
                <div className="text-center mt-4">
                  <p className="text-muted small mb-2">
                    還是有問題？
                  </p>
                  <div className="d-flex justify-content-center gap-3">
                    <Link 
                      to="/contact" 
                      className="text-decoration-none small"
                    >
                      聯絡客服
                    </Link>
                    <span className="text-muted small">|</span>
                    <Link 
                      to="/help" 
                      className="text-decoration-none small"
                    >
                      幫助中心
                    </Link>
                  </div>
                </div>
              </div>
            </div>
            
            {/* 安全提示 */}
            <div className="security-notice mt-4">
              <div className="card bg-light border-0">
                <div className="card-body p-3">
                  <div className="d-flex align-items-start">
                    <AlertCircle size={20} className="text-info me-2 mt-1 flex-shrink-0" />
                    <div>
                      <h6 className="fw-bold mb-1">安全提示</h6>
                      <small className="text-muted">
                        為了您的帳戶安全，我們不會在郵件中要求您提供密碼或其他敏感資訊。
                        如果您收到可疑郵件，請勿點擊其中的連結。
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* 自定義樣式已移至內聯樣式 */}
    </div>
  );
};

export default ForgotPasswordPage;