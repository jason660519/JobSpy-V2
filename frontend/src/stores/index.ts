/**
 * Zustand 狀態管理主入口
 * 導出所有 store 模組和相關類型
 */

// 導出 store hooks
export { useAuthStore } from './authStore';
export { useJobStore } from './jobStore';
export { useSearchStore } from './searchStore';
export { useUIStore } from './uiStore';
export { useUserStore } from './userStore';

// 導出類型定義
export type {
  User,
  AuthState,
} from './authStore';

export type {
  Job,
  JobApplication,
  JobState,
} from './jobStore';

export type {
  SearchQuery,
  SearchFilters,
  SearchState,
} from './searchStore';

export type {
  Notification,
  Modal,
  Breadcrumb,
  UIState,
} from './uiStore';

export type {
  UserProfile,
  Education,
  Certification,
  Resume,
  WorkExperience,
  Project,
  Language,
  UserPreferences,
  UserState,
} from './userStore';

/**
 * 組合所有 store 的根狀態類型
 */
export interface RootState {
  auth: any;
  job: any;
  search: any;
  ui: any;
  user: any;
}

/**
 * Store 工具函數
 */
export const storeUtils = {
  /**
   * 重置所有 store 到初始狀態
   */
  resetAllStores: () => {
    // 這裡可以添加重置邏輯，例如清除 localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-storage');
      localStorage.removeItem('job-storage');
      localStorage.removeItem('search-storage');
      localStorage.removeItem('ui-storage');
      localStorage.removeItem('user-storage');
    }
    
    // 重新載入頁面以重置所有狀態
    if (typeof window !== 'undefined') {
      window.location.reload();
    }
  },
  
  /**
   * 獲取所有 store 的當前狀態（用於調試）
   * 注意：這個函數只能在 React 組件內部使用
   */
  getAllStates: () => {
    // 這個函數需要在組件內部調用，不能在模組級別使用
    console.warn('getAllStates should be called inside React components');
    return {};
  },
};