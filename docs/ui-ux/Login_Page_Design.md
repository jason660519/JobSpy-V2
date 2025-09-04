# 登入/註冊頁面設計規格

## 📋 設計概述

### 設計目標
- **簡潔優雅** - 最小化表單欄位，減少用戶認知負荷
- **多元登入** - 支援傳統登入和社交媒體登入
- **安全性優先** - 強密碼要求、雙因素認證、安全提示
- **用戶引導** - 清晰的註冊流程和錯誤處理
- **品牌一致性** - 與主站設計風格保持一致

### 技術要求
- **框架**: React 18 + TypeScript + Bootstrap 5
- **表單處理**: React Hook Form + Zod 驗證
- **狀態管理**: Zustand
- **API 整合**: TanStack Query
- **國際化**: i18next
- **圖標**: Lucide React

## 🎨 視覺設計

### 頁面佈局

```
┌─────────────────────────────────────────────────────────────┐
│                        頂部導航                             │
│  [Logo] jobseeker                           [語言切換] [?]  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │                 │    │                                 │ │
│  │   品牌展示區     │    │           登入表單              │ │
│  │                 │    │                                 │ │
│  │ ┌─────────────┐ │    │ ┌─────────────────────────────┐ │ │
│  │ │    Logo     │ │    │ │        電子郵件             │ │ │
│  │ │  jobseeker  │ │    │ └─────────────────────────────┘ │ │
│  │ └─────────────┘ │    │ ┌─────────────────────────────┐ │ │
│  │                 │    │ │        密碼                 │ │ │
│  │ 智能求職平台     │    │ └─────────────────────────────┘ │ │
│  │ AI 驅動職位搜尋  │    │                                 │ │
│  │                 │    │ ☑ 記住我    [忘記密碼?]         │ │
│  │ ✓ 多平台整合     │    │                                 │ │
│  │ ✓ 智能匹配       │    │ ┌─────────────────────────────┐ │ │
│  │ ✓ 隱私保護       │    │ │        登入按鈕             │ │ │
│  │                 │    │ └─────────────────────────────┘ │ │
│  │ 「找到理想工作   │    │                                 │ │
│  │  從這裡開始」    │    │        ── 或者 ──               │ │
│  │                 │    │                                 │ │
│  │ ⭐⭐⭐⭐⭐        │    │ ┌─────┐ ┌─────┐ ┌─────────┐     │ │
│  │ "介面直觀易用"   │    │ │Google│ │GitHub│ │LinkedIn │     │ │
│  │ - 張小明         │    │ └─────┘ └─────┘ └─────────┘     │ │
│  │                 │    │                                 │ │
│  │                 │    │ 還沒有帳號? [立即註冊]           │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                        頁腳資訊                             │
│  © 2024 JobSpy. 隱私政策 | 服務條款 | 聯絡我們              │
└─────────────────────────────────────────────────────────────┘
```

### 色彩方案

```css
/* 登入頁面專用色彩 */
:root {
  --auth-primary: #667eea;
  --auth-primary-hover: #5a6fd8;
  --auth-secondary: #764ba2;
  --auth-background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --auth-card-bg: rgba(255, 255, 255, 0.95);
  --auth-input-border: #e1e5e9;
  --auth-input-focus: #667eea;
  --auth-text-primary: #2d3748;
  --auth-text-secondary: #718096;
  --auth-success: #48bb78;
  --auth-error: #f56565;
  --auth-warning: #ed8936;
}
```

## 🔐 登入頁面設計

### 組件結構

```typescript
// LoginPage.tsx
interface LoginPageProps {
  redirectTo?: string;
}

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

const LoginPage: React.FC<LoginPageProps> = ({ redirectTo = '/' }) => {
  // 組件邏輯
};
```

### 表單設計

#### 1. 電子郵件輸入
```html
<div className="form-floating mb-3">
  <input
    type="email"
    className="form-control"
    id="email"
    placeholder="name@example.com"
    required
    autoComplete="email"
  />
  <label htmlFor="email">
    <i className="lucide-mail me-2"></i>
    電子郵件地址
  </label>
  <div className="invalid-feedback">
    請輸入有效的電子郵件地址
  </div>
</div>
```

#### 2. 密碼輸入
```html
<div className="form-floating mb-3">
  <input
    type="password"
    className="form-control"
    id="password"
    placeholder="密碼"
    required
    autoComplete="current-password"
  />
  <label htmlFor="password">
    <i className="lucide-lock me-2"></i>
    密碼
  </label>
  <button 
    type="button" 
    className="btn btn-link position-absolute end-0 top-50 translate-middle-y me-3"
    style="z-index: 10;"
  >
    <i className="lucide-eye"></i>
  </button>
  <div className="invalid-feedback">
    密碼不能為空
  </div>
</div>
```

#### 3. 記住我和忘記密碼
```html
<div className="d-flex justify-content-between align-items-center mb-4">
  <div className="form-check">
    <input 
      className="form-check-input" 
      type="checkbox" 
      id="rememberMe"
    />
    <label className="form-check-label" for="rememberMe">
      記住我
    </label>
  </div>
  <a href="/forgot-password" className="text-decoration-none">
    忘記密碼？
  </a>
</div>
```

#### 4. 登入按鈕
```html
<button 
  type="submit" 
  className="btn btn-primary btn-lg w-100 mb-3"
  disabled={isLoading}
>
  {isLoading ? (
    <>
      <span className="spinner-border spinner-border-sm me-2"></span>
      登入中...
    </>
  ) : (
    <>
      <i className="lucide-log-in me-2"></i>
      登入
    </>
  )}
</button>
```

### 社交登入設計

#### 分隔線
```html
<div className="position-relative my-4">
  <hr className="border-secondary-subtle">
  <span className="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
    或者
  </span>
</div>
```

#### 社交登入按鈕
```html
<div className="row g-2 mb-4">
  <div className="col-4">
    <button className="btn btn-outline-danger w-100" type="button">
      <i className="lucide-chrome me-1"></i>
      Google
    </button>
  </div>
  <div className="col-4">
    <button className="btn btn-outline-dark w-100" type="button">
      <i className="lucide-github me-1"></i>
      GitHub
    </button>
  </div>
  <div className="col-4">
    <button className="btn btn-outline-primary w-100" type="button">
      <i className="lucide-linkedin me-1"></i>
      LinkedIn
    </button>
  </div>
</div>
```

## 📝 註冊頁面設計

### 多步驟註冊流程

```
步驟 1: 基本資訊     步驟 2: 職業資訊     步驟 3: 偏好設定
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ • 姓名       │    │ • 職位       │    │ • 期望地點   │
│ • 郵件       │    │ • 經驗年數   │    │ • 薪資範圍   │
│ • 密碼       │    │ • 技能標籤   │    │ • 工作類型   │
│ • 確認密碼   │    │ • 學歷       │    │ • 通知設定   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 步驟 1: 基本資訊

```html
<div className="registration-step" data-step="1">
  <h4 className="mb-4">
    <i className="lucide-user-plus me-2"></i>
    建立您的帳號
  </h4>
  
  <!-- 姓名 -->
  <div className="row g-3 mb-3">
    <div className="col-md-6">
      <div className="form-floating">
        <input type="text" className="form-control" id="firstName" placeholder="名字">
        <label for="firstName">名字</label>
      </div>
    </div>
    <div className="col-md-6">
      <div className="form-floating">
        <input type="text" className="form-control" id="lastName" placeholder="姓氏">
        <label for="lastName">姓氏</label>
      </div>
    </div>
  </div>
  
  <!-- 電子郵件 -->
  <div className="form-floating mb-3">
    <input type="email" className="form-control" id="email" placeholder="name@example.com">
    <label for="email">
      <i className="lucide-mail me-2"></i>
      電子郵件地址
    </label>
  </div>
  
  <!-- 密碼 -->
  <div className="form-floating mb-3">
    <input type="password" className="form-control" id="password" placeholder="密碼">
    <label for="password">
      <i className="lucide-lock me-2"></i>
      密碼
    </label>
    <!-- 密碼強度指示器 -->
    <div className="password-strength mt-2">
      <div className="progress" style="height: 4px;">
        <div className="progress-bar bg-danger" style="width: 25%"></div>
      </div>
      <small className="text-muted">密碼強度: 弱</small>
    </div>
  </div>
  
  <!-- 確認密碼 -->
  <div className="form-floating mb-4">
    <input type="password" className="form-control" id="confirmPassword" placeholder="確認密碼">
    <label for="confirmPassword">
      <i className="lucide-lock me-2"></i>
      確認密碼
    </label>
  </div>
  
  <!-- 服務條款 -->
  <div className="form-check mb-4">
    <input className="form-check-input" type="checkbox" id="agreeTerms" required>
    <label className="form-check-label" for="agreeTerms">
      我同意 <a href="/terms" target="_blank">服務條款</a> 和 <a href="/privacy" target="_blank">隱私政策</a>
    </label>
  </div>
  
  <button type="button" className="btn btn-primary btn-lg w-100">
    下一步
    <i className="lucide-arrow-right ms-2"></i>
  </button>
</div>
```

### 步驟 2: 職業資訊

```html
<div className="registration-step" data-step="2">
  <h4 className="mb-4">
    <i className="lucide-briefcase me-2"></i>
    告訴我們您的職業背景
  </h4>
  
  <!-- 目前職位 -->
  <div className="form-floating mb-3">
    <input type="text" className="form-control" id="currentPosition" placeholder="目前職位">
    <label for="currentPosition">目前職位</label>
  </div>
  
  <!-- 經驗年數 -->
  <div className="form-floating mb-3">
    <select className="form-select" id="experience">
      <option value="">選擇經驗年數</option>
      <option value="0-1">0-1 年</option>
      <option value="1-3">1-3 年</option>
      <option value="3-5">3-5 年</option>
      <option value="5-10">5-10 年</option>
      <option value="10+">10+ 年</option>
    </select>
    <label for="experience">工作經驗</label>
  </div>
  
  <!-- 技能標籤 -->
  <div className="mb-3">
    <label className="form-label">技能標籤</label>
    <div className="skills-input">
      <input type="text" className="form-control" placeholder="輸入技能並按 Enter 添加">
      <div className="skills-tags mt-2">
        <span className="badge bg-primary me-2 mb-2">React <i className="lucide-x ms-1"></i></span>
        <span className="badge bg-primary me-2 mb-2">TypeScript <i className="lucide-x ms-1"></i></span>
        <span className="badge bg-primary me-2 mb-2">Node.js <i className="lucide-x ms-1"></i></span>
      </div>
    </div>
  </div>
  
  <!-- 學歷 -->
  <div className="form-floating mb-4">
    <select className="form-select" id="education">
      <option value="">選擇學歷</option>
      <option value="high-school">高中</option>
      <option value="associate">專科</option>
      <option value="bachelor">學士</option>
      <option value="master">碩士</option>
      <option value="phd">博士</option>
    </select>
    <label for="education">最高學歷</label>
  </div>
  
  <div className="d-flex gap-3">
    <button type="button" className="btn btn-outline-secondary flex-fill">
      <i className="lucide-arrow-left me-2"></i>
      上一步
    </button>
    <button type="button" className="btn btn-primary flex-fill">
      下一步
      <i className="lucide-arrow-right ms-2"></i>
    </button>
  </div>
</div>
```

### 步驟 3: 偏好設定

```html
<div className="registration-step" data-step="3">
  <h4 className="mb-4">
    <i className="lucide-settings me-2"></i>
    設定您的求職偏好
  </h4>
  
  <!-- 期望地點 -->
  <div className="mb-3">
    <label className="form-label">期望工作地點</label>
    <div className="location-options">
      <div className="row g-2">
        <div className="col-6 col-md-4">
          <input type="checkbox" className="btn-check" id="taipei" autocomplete="off">
          <label className="btn btn-outline-primary w-100" for="taipei">台北市</label>
        </div>
        <div className="col-6 col-md-4">
          <input type="checkbox" className="btn-check" id="newtaipei" autocomplete="off">
          <label className="btn btn-outline-primary w-100" for="newtaipei">新北市</label>
        </div>
        <div className="col-6 col-md-4">
          <input type="checkbox" className="btn-check" id="remote" autocomplete="off">
          <label className="btn btn-outline-primary w-100" for="remote">遠端工作</label>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 薪資範圍 -->
  <div className="mb-3">
    <label class="form-label">期望薪資範圍 (年薪)</label>
    <div className="row g-3">
      <div className="col-6">
        <div className="form-floating">
          <input type="number" className="form-control" id="salaryMin" placeholder="最低薪資">
          <label for="salaryMin">最低 (萬)</label>
        </div>
      </div>
      <div className="col-6">
        <div className="form-floating">
          <input type="number" className="form-control" id="salaryMax" placeholder="最高薪資">
          <label for="salaryMax">最高 (萬)</label>
        </div>
      </div>
    </div>
  </div>
  
  <!-- 工作類型 -->
  <div className="mb-3">
    <label className="form-label">工作類型</label>
    <div className="work-type-options">
      <div className="form-check">
        <input className="form-check-input" type="checkbox" id="fulltime">
        <label className="form-check-label" for="fulltime">全職</label>
      </div>
      <div className="form-check">
        <input className="form-check-input" type="checkbox" id="parttime">
        <label className="form-check-label" for="parttime">兼職</label>
      </div>
      <div className="form-check">
        <input className="form-check-input" type="checkbox" id="contract">
        <label className="form-check-label" for="contract">約聘</label>
      </div>
      <div className="form-check">
        <input className="form-check-input" type="checkbox" id="freelance">
        <label className="form-check-label" for="freelance">自由接案</label>
      </div>
    </div>
  </div>
  
  <!-- 通知設定 -->
  <div className="mb-4">
    <label className="form-label">通知設定</label>
    <div className="notification-options">
      <div className="form-check form-switch">
        <input className="form-check-input" type="checkbox" id="emailNotifications" checked>
        <label className="form-check-label" for="emailNotifications">
          郵件通知新職位
        </label>
      </div>
      <div className="form-check form-switch">
        <input className="form-check-input" type="checkbox" id="weeklyDigest" checked>
        <label className="form-check-label" for="weeklyDigest">
          每週職位摘要
        </label>
      </div>
      <div className="form-check form-switch">
        <input className="form-check-input" type="checkbox" id="marketingEmails">
        <label className="form-check-label" for="marketingEmails">
          產品更新和優惠資訊
        </label>
      </div>
    </div>
  </div>
  
  <div className="d-flex gap-3">
    <button type="button" className="btn btn-outline-secondary flex-fill">
      <i className="lucide-arrow-left me-2"></i>
      上一步
    </button>
    <button type="submit" className="btn btn-success flex-fill">
      <i className="lucide-check me-2"></i>
      完成註冊
    </button>
  </div>
</div>
```

## 🔒 安全功能設計

### 密碼強度檢測

```typescript
interface PasswordStrength {
  score: number; // 0-4
  feedback: string[];
  color: 'danger' | 'warning' | 'info' | 'success';
}

const checkPasswordStrength = (password: string): PasswordStrength => {
  let score = 0;
  const feedback: string[] = [];
  
  // 長度檢查
  if (password.length >= 8) score++;
  else feedback.push('至少需要 8 個字符');
  
  // 大小寫檢查
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
  else feedback.push('需要包含大小寫字母');
  
  // 數字檢查
  if (/\d/.test(password)) score++;
  else feedback.push('需要包含數字');
  
  // 特殊字符檢查
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;
  else feedback.push('建議包含特殊字符');
  
  const colors = ['danger', 'danger', 'warning', 'info', 'success'] as const;
  
  return {
    score,
    feedback,
    color: colors[score]
  };
};
```

### 雙因素認證設定

```html
<!-- 2FA 設定模態框 -->
<div className="modal fade" id="twoFactorModal">
  <div className="modal-dialog">
    <div className="modal-content">
      <div className="modal-header">
        <h5 className="modal-title">
          <i className="lucide-shield me-2"></i>
          設定雙因素認證
        </h5>
        <button type="button" className="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div className="modal-body">
        <div className="text-center mb-4">
          <div className="qr-code-container">
            <!-- QR Code 會在這裡顯示 -->
            <img src="data:image/png;base64,..." alt="QR Code" className="img-fluid">
          </div>
          <p className="mt-3 text-muted">
            使用 Google Authenticator 或其他 TOTP 應用程式掃描此 QR 碼
          </p>
        </div>
        
        <div className="form-floating mb-3">
          <input type="text" className="form-control" id="totpCode" placeholder="驗證碼">
          <label for="totpCode">輸入 6 位數驗證碼</label>
        </div>
        
        <div className="alert alert-info">
          <i className="lucide-info me-2"></i>
          請妥善保存備用恢復碼，以防遺失驗證器設備
        </div>
      </div>
      <div className="modal-footer">
        <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">取消</button>
        <button type="button" className="btn btn-primary">啟用 2FA</button>
      </div>
    </div>
  </div>
</div>
```

## 📱 響應式設計

### 移動端佈局

```css
/* 移動端樣式 */
@media (max-width: 767.98px) {
  .auth-container {
    padding: 1rem;
  }
  
  .auth-brand-section {
    display: none; /* 隱藏品牌展示區 */
  }
  
  .auth-form-section {
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
  }
  
  .social-login-buttons .col-4 {
    flex: 0 0 100%;
    max-width: 100%;
    margin-bottom: 0.5rem;
  }
  
  .registration-steps {
    padding: 1rem;
  }
}

/* 平板端樣式 */
@media (min-width: 768px) and (max-width: 991.98px) {
  .auth-brand-section {
    padding: 2rem;
  }
  
  .auth-form-section {
    padding: 2rem;
  }
}
```

### 觸控優化

```css
/* 觸控友好的按鈕尺寸 */
.btn-touch {
  min-height: 44px;
  min-width: 44px;
}

/* 表單元素間距 */
.form-floating {
  margin-bottom: 1rem;
}

/* 社交登入按鈕 */
.social-login-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## 🌐 國際化支援

### 語言切換

```typescript
// 語言切換組件
const LanguageSwitch: React.FC = () => {
  const { i18n } = useTranslation();
  
  const languages = [
    { code: 'zh', name: '中文', flag: '🇹🇼' },
    { code: 'en', name: 'English', flag: '🇺🇸' }
  ];
  
  return (
    <div className="dropdown">
      <button 
        className="btn btn-outline-secondary dropdown-toggle" 
        type="button" 
        data-bs-toggle="dropdown"
      >
        {languages.find(lang => lang.code === i18n.language)?.flag} 
        {languages.find(lang => lang.code === i18n.language)?.name}
      </button>
      <ul className="dropdown-menu">
        {languages.map(lang => (
          <li key={lang.code}>
            <button 
              className="dropdown-item" 
              onClick={() => i18n.changeLanguage(lang.code)}
            >
              {lang.flag} {lang.name}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
```

### 翻譯資源

```json
// zh.json
{
  "auth": {
    "login": {
      "title": "登入您的帳號",
      "email": "電子郵件地址",
      "password": "密碼",
      "rememberMe": "記住我",
      "forgotPassword": "忘記密碼？",
      "loginButton": "登入",
      "socialLogin": "或者",
      "noAccount": "還沒有帳號？",
      "signUp": "立即註冊"
    },
    "register": {
      "title": "建立新帳號",
      "step1Title": "基本資訊",
      "step2Title": "職業背景",
      "step3Title": "求職偏好",
      "firstName": "名字",
      "lastName": "姓氏",
      "confirmPassword": "確認密碼",
      "agreeTerms": "我同意服務條款和隱私政策",
      "nextStep": "下一步",
      "previousStep": "上一步",
      "complete": "完成註冊"
    }
  }
}
```

## 🔧 技術實作

### 表單驗證

```typescript
// 使用 Zod 進行表單驗證
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('請輸入有效的電子郵件地址'),
  password: z.string().min(1, '密碼不能為空'),
  rememberMe: z.boolean().optional()
});

const registerSchema = z.object({
  firstName: z.string().min(1, '請輸入名字'),
  lastName: z.string().min(1, '請輸入姓氏'),
  email: z.string().email('請輸入有效的電子郵件地址'),
  password: z.string()
    .min(8, '密碼至少需要 8 個字符')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, '密碼需要包含大小寫字母和數字'),
  confirmPassword: z.string(),
  agreeTerms: z.boolean().refine(val => val === true, '請同意服務條款')
}).refine(data => data.password === data.confirmPassword, {
  message: '密碼確認不匹配',
  path: ['confirmPassword']
});
```

### API 整合

```typescript
// 認證 API
interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('登入失敗');
    }
    
    return response.json();
  },
  
  register: async (data: RegisterRequest): Promise<LoginResponse> => {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error('註冊失敗');
    }
    
    return response.json();
  },
  
  socialLogin: async (provider: string, token: string): Promise<LoginResponse> => {
    const response = await fetch(`/api/v1/auth/social/${provider}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
    
    return response.json();
  }
};
```

### 狀態管理

```typescript
// 認證狀態管理
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  
  login: async (credentials) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await authApi.login(credentials);
      
      // 儲存 token
      localStorage.setItem('accessToken', response.accessToken);
      localStorage.setItem('refreshToken', response.refreshToken);
      
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      set({ 
        error: error.message, 
        isLoading: false 
      });
    }
  },
  
  register: async (data) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await authApi.register(data);
      
      localStorage.setItem('accessToken', response.accessToken);
      localStorage.setItem('refreshToken', response.refreshToken);
      
      set({ 
        user: response.user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      set({ 
        error: error.message, 
        isLoading: false 
      });
    }
  },
  
  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    set({ 
      user: null, 
      isAuthenticated: false, 
      error: null 
    });
  },
  
  clearError: () => set({ error: null })
}));
```

## 📊 用戶體驗優化

### 載入狀態

```typescript
// 載入動畫組件
const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'spinner-border-sm',
    md: '',
    lg: 'spinner-border-lg'
  };
  
  return (
    <div className={`spinner-border ${sizeClasses[size]}`} role="status">
      <span className="visually-hidden">載入中...</span>
    </div>
  );
};
```

### 錯誤處理

```typescript
// 錯誤提示組件
const ErrorAlert: React.FC<{ error: string; onDismiss: () => void }> = ({ error, onDismiss }) => {
  return (
    <div className="alert alert-danger alert-dismissible fade show" role="alert">
      <i className="lucide-alert-circle me-2"></i>
      {error}
      <button 
        type="button" 
        className="btn-close" 
        onClick={onDismiss}
      ></button>
    </div>
  );
};
```

### 成功反饋

```typescript
// 成功提示組件
const SuccessToast: React.FC<{ message: string; show: boolean }> = ({ message, show }) => {
  return (
    <div className={`toast ${show ? 'show' : ''}`} role="alert">
      <div className="toast-header">
        <i className="lucide-check-circle text-success me-2"></i>
        <strong className="me-auto">成功</strong>
        <button type="button" className="btn-close" data-bs-dismiss="toast"></button>
      </div>
      <div className="toast-body">
        {message}
      </div>
    </div>
  );
};
```

## 🔐 安全性考量

### CSRF 保護

```typescript
// CSRF Token 處理
const getCsrfToken = (): string => {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta?.getAttribute('content') || '';
};

// 在 API 請求中包含 CSRF Token
const apiRequest = async (url: string, options: RequestInit = {}) => {
  const csrfToken = getCsrfToken();
  
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken,
      ...options.headers
    }
  });
};
```

### 輸入清理

```typescript
// 輸入清理函數
const sanitizeInput = (input: string): string => {
  return input
    .trim()
    .replace(/[<>"'&]/g, (match) => {
      const entities: Record<string, string> = {
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '&': '&amp;'
      };
      return entities[match] || match;
    });
};
```

### 速率限制

```typescript
// 客戶端速率限制
class RateLimiter {
  private attempts: Map<string, number[]> = new Map();
  
  canAttempt(key: string, maxAttempts: number, windowMs: number): boolean {
    const now = Date.now();
    const attempts = this.attempts.get(key) || [];
    
    // 清理過期的嘗試
    const validAttempts = attempts.filter(time => now - time < windowMs);
    
    if (validAttempts.length >= maxAttempts) {
      return false;
    }
    
    validAttempts.push(now);
    this.attempts.set(key, validAttempts);
    
    return true;
  }
}

const rateLimiter = new RateLimiter();

// 在登入嘗試前檢查
const handleLogin = async (credentials: LoginRequest) => {
  if (!rateLimiter.canAttempt('login', 5, 15 * 60 * 1000)) {
    throw new Error('嘗試次數過多，請稍後再試');
  }
  
  // 執行登入邏輯
};
```

## 📱 無障礙設計

### ARIA 標籤

```html
<!-- 表單無障礙標籤 -->
<form role="form" aria-labelledby="login-title">
  <h2 id="login-title">登入您的帳號</h2>
  
  <div className="form-floating">
    <input 
      type="email" 
      className="form-control" 
      id="email"
      aria-describedby="email-help email-error"
      aria-required="true"
    >
    <label for="email">電子郵件地址</label>
    <div id="email-help" className="form-text">我們不會分享您的郵件地址</div>
    <div id="email-error" className="invalid-feedback" aria-live="polite"></div>
  </div>
  
  <button type="submit" aria-describedby="login-status">
    登入
  </button>
  
  <div id="login-status" aria-live="polite" aria-atomic="true"></div>
</form>
```

### 鍵盤導航

```css
/* 焦點樣式 */
.form-control:focus,
.btn:focus {
  outline: 2px solid var(--auth-primary);
  outline-offset: 2px;
}

/* 跳過連結 */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--auth-primary);
  color: white;
  padding: 8px;
  text-decoration: none;
  z-index: 1000;
}

.skip-link:focus {
  top: 6px;
}
```

## 📈 性能優化

### 代碼分割

```typescript
// 懶加載認證頁面
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));

// 路由配置
const AuthRoutes = () => {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Routes>
    </Suspense>
  );
};
```

### 圖片優化

```typescript
// 響應式圖片組件
const ResponsiveImage: React.FC<{
  src: string;
  alt: string;
  sizes?: string;
}> = ({ src, alt, sizes = "(max-width: 768px) 100vw, 50vw" }) => {
  return (
    <picture>
      <source 
        media="(max-width: 768px)" 
        srcSet={`${src}?w=400 400w, ${src}?w=800 800w`}
      />
      <source 
        media="(min-width: 769px)" 
        srcSet={`${src}?w=600 600w, ${src}?w=1200 1200w`}
      />
      <img 
        src={`${src}?w=600`} 
        alt={alt} 
        sizes={sizes}
        loading="lazy"
        className="img-fluid"
      />
    </picture>
  );
};
```

## 🧪 測試策略

### 單元測試

```typescript
// LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('應該顯示必填欄位錯誤', async () => {
    render(<LoginForm />);
    
    const submitButton = screen.getByRole('button', { name: /登入/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('請輸入電子郵件地址')).toBeInTheDocument();
      expect(screen.getByText('密碼不能為空')).toBeInTheDocument();
    });
  });
  
  it('應該在成功登入後重定向', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: true });
    render(<LoginForm onLogin={mockLogin} />);
    
    fireEvent.change(screen.getByLabelText(/電子郵件/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/密碼/i), {
      target: { value: 'password123' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /登入/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false
      });
    });
  });
});
```

### E2E 測試

```typescript
// login.e2e.test.ts
import { test, expect } from '@playwright/test';

test.describe('登入流程', () => {
  test('用戶可以成功登入', async ({ page }) => {
    await page.goto('/login');
    
    // 填寫登入表單
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    
    // 點擊登入按鈕
    await page.click('[data-testid="login-button"]');
    
    // 驗證重定向到首頁
    await expect(page).toHaveURL('/');
    
    // 驗證用戶已登入
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });
  
  test('顯示無效憑證錯誤', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('[data-testid="email"]', 'invalid@example.com');
    await page.fill('[data-testid="password"]', 'wrongpassword');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('.alert-danger')).toContainText('登入失敗');
  });
});
```

## 📝 總結

本登入/註冊頁面設計規格提供了：

1. **完整的視覺設計** - 現代化、響應式的界面設計
2. **多步驟註冊流程** - 降低用戶註冊門檻
3. **多種登入方式** - 傳統登入 + 社交登入
4. **強化的安全性** - 密碼強度檢測、2FA、CSRF 保護
5. **優秀的用戶體驗** - 即時驗證、清晰的錯誤提示
6. **無障礙設計** - 符合 WCAG 2.1 AA 標準
7. **國際化支援** - 中英文切換
8. **完整的測試覆蓋** - 單元測試和 E2E 測試

這個設計將為 JobSpy v2 提供一個安全、易用、現代化的用戶認證系統。