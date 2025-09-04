/**
 * 認證狀態管理 Store
 * 管理用戶登入、註冊、登出等認證相關狀態
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin';
  emailVerified: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AuthState {
  // 狀態
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // 動作
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  updateUser: (userData: Partial<User>) => void;
  refreshToken: () => Promise<void>;
  
  // 社交登入
  loginWithGoogle: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  loginWithLinkedIn: () => Promise<void>;
}

/**
 * 認證 API 服務
 */
class AuthService {
  private baseURL = 'http://localhost:8000/api/v1/auth';
  
  /**
   * 用戶登入
   */
  async login(email: string, password: string): Promise<{ user: User; token: string }> {
    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '登入失敗');
    }
    
    return response.json();
  }
  
  /**
   * 用戶註冊
   */
  async register(email: string, password: string, name: string): Promise<{ user: User; token: string }> {
    const response = await fetch(`${this.baseURL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '註冊失敗');
    }
    
    return response.json();
  }
  
  /**
   * 刷新 token
   */
  async refreshToken(): Promise<{ user: User; token: string }> {
    const token = localStorage.getItem('auth-token');
    
    const response = await fetch(`${this.baseURL}/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Token 刷新失敗');
    }
    
    return response.json();
  }
  
  /**
   * 社交登入
   */
  async socialLogin(provider: 'google' | 'github' | 'linkedin'): Promise<{ user: User; token: string }> {
    // 這裡實現社交登入邏輯
    // 通常會重定向到第三方認證頁面
    window.location.href = `${this.baseURL}/social/${provider}`;
    throw new Error('重定向中...');
  }
}

const authService = new AuthService();

/**
 * 認證狀態 Store
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      /**
       * 用戶登入
       */
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const { user, token } = await authService.login(email, password);
          
          // 保存 token
          localStorage.setItem('auth-token', token);
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '登入失敗',
          });
          throw error;
        }
      },
      
      /**
       * 用戶註冊
       */
      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const { user, token } = await authService.register(email, password, name);
          
          // 保存 token
          localStorage.setItem('auth-token', token);
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : '註冊失敗',
          });
          throw error;
        }
      },
      
      /**
       * 用戶登出
       */
      logout: () => {
        localStorage.removeItem('auth-token');
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },
      
      /**
       * 清除錯誤
       */
      clearError: () => {
        set({ error: null });
      },
      
      /**
       * 更新用戶資料
       */
      updateUser: (userData: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({
            user: { ...user, ...userData },
          });
        }
      },
      
      /**
       * 刷新 token
       */
      refreshToken: async () => {
        set({ isLoading: true });
        
        try {
          const { user, token } = await authService.refreshToken();
          
          localStorage.setItem('auth-token', token);
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          // Token 無效，登出用戶
          get().logout();
          set({ isLoading: false });
        }
      },
      
      /**
       * Google 登入
       */
      loginWithGoogle: async () => {
        set({ isLoading: true, error: null });
        
        try {
          await authService.socialLogin('google');
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Google 登入失敗',
          });
        }
      },
      
      /**
       * GitHub 登入
       */
      loginWithGitHub: async () => {
        set({ isLoading: true, error: null });
        
        try {
          await authService.socialLogin('github');
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'GitHub 登入失敗',
          });
        }
      },
      
      /**
       * LinkedIn 登入
       */
      loginWithLinkedIn: async () => {
        set({ isLoading: true, error: null });
        
        try {
          await authService.socialLogin('linkedin');
        } catch (error) {
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'LinkedIn 登入失敗',
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);