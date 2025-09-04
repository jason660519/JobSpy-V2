/**
 * UI 狀態管理 Store
 * 管理主題、通知、模態框、側邊欄等 UI 相關狀態
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: number;
}

export interface Modal {
  id: string;
  type: string;
  props?: Record<string, any>;
  onClose?: () => void;
}

export interface Breadcrumb {
  label: string;
  href?: string;
  active?: boolean;
}

export interface UIState {
  // 主題設置
  theme: 'light' | 'dark' | 'auto';
  isDarkMode: boolean;
  
  // 布局狀態
  sidebarCollapsed: boolean;
  sidebarVisible: boolean;
  headerHeight: number;
  
  // 響應式狀態
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  screenSize: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';
  
  // 載入狀態
  isGlobalLoading: boolean;
  loadingMessage?: string;
  
  // 通知系統
  notifications: Notification[];
  maxNotifications: number;
  
  // 模態框系統
  modals: Modal[];
  
  // 麵包屑導航
  breadcrumbs: Breadcrumb[];
  
  // 頁面狀態
  pageTitle: string;
  pageDescription?: string;
  
  // 搜索狀態
  searchFocused: boolean;
  searchValue: string;
  
  // 滾動狀態
  scrollY: number;
  isScrolled: boolean;
  
  // 動作
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  toggleTheme: () => void;
  
  // 布局控制
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setSidebarVisible: (visible: boolean) => void;
  setHeaderHeight: (height: number) => void;
  
  // 響應式控制
  updateScreenSize: (width: number) => void;
  
  // 載入控制
  setGlobalLoading: (loading: boolean, message?: string) => void;
  
  // 通知管理
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // 模態框管理
  openModal: (modal: Omit<Modal, 'id'>) => void;
  closeModal: (id: string) => void;
  closeAllModals: () => void;
  
  // 麵包屑管理
  setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => void;
  addBreadcrumb: (breadcrumb: Breadcrumb) => void;
  
  // 頁面管理
  setPageTitle: (title: string) => void;
  setPageDescription: (description: string) => void;
  setPageMeta: (title: string, description?: string) => void;
  
  // 搜索控制
  setSearchFocused: (focused: boolean) => void;
  setSearchValue: (value: string) => void;
  
  // 滾動控制
  setScrollY: (y: number) => void;
  
  // 工具方法
  getNotificationsByType: (type: Notification['type']) => Notification[];
  hasModal: (type: string) => boolean;
  getModalByType: (type: string) => Modal | undefined;
}

/**
 * 生成唯一 ID
 */
function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

/**
 * 獲取屏幕尺寸類型
 */
function getScreenSize(width: number): UIState['screenSize'] {
  if (width < 576) return 'xs';
  if (width < 768) return 'sm';
  if (width < 992) return 'md';
  if (width < 1200) return 'lg';
  if (width < 1400) return 'xl';
  return 'xxl';
}

/**
 * 檢測系統主題偏好
 */
function getSystemTheme(): 'light' | 'dark' {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
}

/**
 * UI 狀態 Store
 */
export const useUIStore = create<UIState>()(
  persist(
    (set, get) => {
      // 監聽系統主題變化
      if (typeof window !== 'undefined' && window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
          const { theme } = get();
          if (theme === 'auto') {
            set({ isDarkMode: e.matches });
          }
        });
      }
      
      // 監聽窗口大小變化與滾動（在 store 方法可用前直接 set）
      if (typeof window !== 'undefined') {
        const handleResize = () => {
          const width = window.innerWidth;
          const screenSize = getScreenSize(width);
          const isMobile = width < 768;
          const isTablet = width >= 768 && width < 992;
          const isDesktop = width >= 992;
          set({
            screenSize,
            isMobile,
            isTablet,
            isDesktop,
            sidebarVisible: !isMobile,
          });
        };

        window.addEventListener('resize', handleResize);
        handleResize(); // 初始化

        const handleScroll = () => {
          const y = window.scrollY;
          set({ scrollY: y, isScrolled: y > 0 });
        };

        window.addEventListener('scroll', handleScroll);
      }
      
      return {
        // 初始狀態
        theme: 'auto',
        isDarkMode: getSystemTheme() === 'dark',
        
        sidebarCollapsed: false,
        sidebarVisible: true,
        headerHeight: 64,
        
        isMobile: false,
        isTablet: false,
        isDesktop: true,
        screenSize: 'xl',
        
        isGlobalLoading: false,
        loadingMessage: undefined,
        
        notifications: [],
        maxNotifications: 5,
        
        modals: [],
        
        breadcrumbs: [],
        
        pageTitle: 'JobSpy',
        pageDescription: undefined,
        
        searchFocused: false,
        searchValue: '',
        
        scrollY: 0,
        isScrolled: false,
        
        /**
         * 設置主題
         */
        setTheme: (theme: 'light' | 'dark' | 'auto') => {
          set({ theme });
          
          if (theme === 'auto') {
            set({ isDarkMode: getSystemTheme() === 'dark' });
          } else {
            set({ isDarkMode: theme === 'dark' });
          }
        },
        
        /**
         * 切換主題
         */
        toggleTheme: () => {
          const { theme } = get();
          if (theme === 'light') {
            get().setTheme('dark');
          } else if (theme === 'dark') {
            get().setTheme('auto');
          } else {
            get().setTheme('light');
          }
        },
        
        /**
         * 切換側邊欄
         */
        toggleSidebar: () => {
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
        },
        
        /**
         * 設置側邊欄摺疊狀態
         */
        setSidebarCollapsed: (collapsed: boolean) => {
          set({ sidebarCollapsed: collapsed });
        },
        
        /**
         * 設置側邊欄可見性
         */
        setSidebarVisible: (visible: boolean) => {
          set({ sidebarVisible: visible });
        },
        
        /**
         * 設置頭部高度
         */
        setHeaderHeight: (height: number) => {
          set({ headerHeight: height });
        },
        
        /**
         * 更新屏幕尺寸
         */
        updateScreenSize: (width: number) => {
          const screenSize = getScreenSize(width);
          const isMobile = width < 768;
          const isTablet = width >= 768 && width < 992;
          const isDesktop = width >= 992;
          
          set({
            screenSize,
            isMobile,
            isTablet,
            isDesktop,
            sidebarVisible: !isMobile, // 移動端默認隱藏側邊欄
          });
        },
        
        /**
         * 設置全局載入狀態
         */
        setGlobalLoading: (loading: boolean, message?: string) => {
          set({ isGlobalLoading: loading, loadingMessage: message });
        },
        
        /**
         * 添加通知
         */
        addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => {
          const newNotification: Notification = {
            ...notification,
            id: generateId(),
            createdAt: Date.now(),
          };
          
          set((state) => {
            const notifications = [newNotification, ...state.notifications];
            // 限制通知數量
            if (notifications.length > state.maxNotifications) {
              notifications.splice(state.maxNotifications);
            }
            return { notifications };
          });
          
          // 自動移除通知
          if (notification.duration !== 0) {
            const duration = notification.duration || 5000;
            setTimeout(() => {
              get().removeNotification(newNotification.id);
            }, duration);
          }
        },
        
        /**
         * 移除通知
         */
        removeNotification: (id: string) => {
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }));
        },
        
        /**
         * 清除所有通知
         */
        clearNotifications: () => {
          set({ notifications: [] });
        },
        
        /**
         * 打開模態框
         */
        openModal: (modal: Omit<Modal, 'id'>) => {
          const newModal: Modal = {
            ...modal,
            id: generateId(),
          };
          
          set((state) => ({
            modals: [...state.modals, newModal],
          }));
        },
        
        /**
         * 關閉模態框
         */
        closeModal: (id: string) => {
          set((state) => {
            const modal = state.modals.find((m) => m.id === id);
            if (modal?.onClose) {
              modal.onClose();
            }
            return {
              modals: state.modals.filter((m) => m.id !== id),
            };
          });
        },
        
        /**
         * 關閉所有模態框
         */
        closeAllModals: () => {
          const { modals } = get();
          modals.forEach((modal) => {
            if (modal.onClose) {
              modal.onClose();
            }
          });
          set({ modals: [] });
        },
        
        /**
         * 設置麵包屑
         */
        setBreadcrumbs: (breadcrumbs: Breadcrumb[]) => {
          set({ breadcrumbs });
        },
        
        /**
         * 添加麵包屑
         */
        addBreadcrumb: (breadcrumb: Breadcrumb) => {
          set((state) => ({
            breadcrumbs: [...state.breadcrumbs, breadcrumb],
          }));
        },
        
        /**
         * 設置頁面標題
         */
        setPageTitle: (title: string) => {
          set({ pageTitle: title });
          if (typeof document !== 'undefined') {
            document.title = title;
          }
        },
        
        /**
         * 設置頁面描述
         */
        setPageDescription: (description: string) => {
          set({ pageDescription: description });
          if (typeof document !== 'undefined') {
            const metaDescription = document.querySelector('meta[name="description"]');
            if (metaDescription) {
              metaDescription.setAttribute('content', description);
            }
          }
        },
        
        /**
         * 設置頁面元數據
         */
        setPageMeta: (title: string, description?: string) => {
          get().setPageTitle(title);
          if (description) {
            get().setPageDescription(description);
          }
        },
        
        /**
         * 設置搜索焦點狀態
         */
        setSearchFocused: (focused: boolean) => {
          set({ searchFocused: focused });
        },
        
        /**
         * 設置搜索值
         */
        setSearchValue: (value: string) => {
          set({ searchValue: value });
        },
        
        /**
         * 設置滾動位置
         */
        setScrollY: (y: number) => {
          set({ scrollY: y, isScrolled: y > 0 });
        },
        
        /**
         * 根據類型獲取通知
         */
        getNotificationsByType: (type: Notification['type']) => {
          return get().notifications.filter((n) => n.type === type);
        },
        
        /**
         * 檢查是否有指定類型的模態框
         */
        hasModal: (type: string) => {
          return get().modals.some((m) => m.type === type);
        },
        
        /**
         * 根據類型獲取模態框
         */
        getModalByType: (type: string) => {
          return get().modals.find((m) => m.type === type);
        },
      };
    },
    {
      name: 'ui-storage',
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);