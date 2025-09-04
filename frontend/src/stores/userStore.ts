/**
 * 用戶狀態管理 Store
 * 管理用戶個人資料、簡歷、偏好設置等相關狀態
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UserProfile {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  phone?: string;
  location?: string;
  website?: string;
  linkedin?: string;
  github?: string;
  bio?: string;
  title?: string;
  company?: string;
  experience?: string;
  skills: string[];
  languages: string[];
  education: Education[];
  certifications: Certification[];
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
}

export interface Education {
  id: string;
  school: string;
  degree: string;
  field: string;
  startDate: string;
  endDate?: string;
  gpa?: number;
  description?: string;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  issueDate: string;
  expiryDate?: string;
  credentialId?: string;
  url?: string;
}

export interface Resume {
  id: string;
  name: string;
  template: string;
  content: {
    personalInfo: {
      name: string;
      email: string;
      phone?: string;
      location?: string;
      website?: string;
      linkedin?: string;
      github?: string;
    };
    summary?: string;
    experience: WorkExperience[];
    education: Education[];
    skills: string[];
    certifications: Certification[];
    projects?: Project[];
    languages?: Language[];
  };
  isDefault: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WorkExperience {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  location?: string;
  description: string;
  achievements: string[];
  skills: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  technologies: string[];
  url?: string;
  github?: string;
  startDate: string;
  endDate?: string;
  highlights: string[];
}

export interface Language {
  name: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'native';
}

export interface UserPreferences {
  jobAlerts: {
    enabled: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
    keywords: string[];
    locations: string[];
    salaryMin?: number;
    jobTypes: string[];
  };
  privacy: {
    profileVisibility: 'public' | 'private' | 'recruiters';
    showEmail: boolean;
    showPhone: boolean;
    allowMessages: boolean;
  };
  notifications: {
    email: boolean;
    push: boolean;
    jobRecommendations: boolean;
    applicationUpdates: boolean;
    messages: boolean;
  };
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
}

export interface UserState {
  // 用戶資料
  profile: UserProfile | null;
  isProfileLoading: boolean;
  profileError: string | null;
  
  // 簡歷管理
  resumes: Resume[];
  currentResume: Resume | null;
  isResumeLoading: boolean;
  resumeError: string | null;
  
  // 偏好設置
  preferences: UserPreferences | null;
  isPreferencesLoading: boolean;
  
  // 統計數據
  stats: {
    profileViews: number;
    applicationsSent: number;
    interviewsScheduled: number;
    offersReceived: number;
  } | null;
  
  // 動作
  fetchProfile: () => Promise<void>;
  updateProfile: (updates: Partial<UserProfile>) => Promise<void>;
  uploadAvatar: (file: File) => Promise<void>;
  
  // 簡歷管理
  fetchResumes: () => Promise<void>;
  createResume: (resume: Omit<Resume, 'id' | 'createdAt' | 'updatedAt'>) => Promise<void>;
  updateResume: (resumeId: string, updates: Partial<Resume>) => Promise<void>;
  deleteResume: (resumeId: string) => Promise<void>;
  setDefaultResume: (resumeId: string) => Promise<void>;
  duplicateResume: (resumeId: string) => Promise<void>;
  
  // 偏好設置
  fetchPreferences: () => Promise<void>;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  
  // 統計數據
  fetchStats: () => Promise<void>;
  
  // 工具方法
  getFullName: () => string;
  getDefaultResume: () => Resume | null;
  clearUserData: () => void;
}

/**
 * 用戶 API 服務
 */
class UserService {
  private baseURL = 'http://localhost:8000/api/v1';
  
  private getAuthHeaders() {
    return {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json',
    };
  }
  
  /**
   * 獲取用戶資料
   */
  async getProfile(): Promise<UserProfile> {
    const response = await fetch(`${this.baseURL}/user/profile`, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取用戶資料失敗');
    }
    
    return response.json();
  }
  
  /**
   * 更新用戶資料
   */
  async updateProfile(updates: Partial<UserProfile>): Promise<UserProfile> {
    const response = await fetch(`${this.baseURL}/user/profile`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新用戶資料失敗');
    }
    
    return response.json();
  }
  
  /**
   * 上傳頭像
   */
  async uploadAvatar(file: File): Promise<{ avatarUrl: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await fetch(`${this.baseURL}/user/avatar`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '上傳頭像失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取簡歷列表
   */
  async getResumes(): Promise<Resume[]> {
    const response = await fetch(`${this.baseURL}/user/resumes`, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取簡歷列表失敗');
    }
    
    return response.json();
  }
  
  /**
   * 創建簡歷
   */
  async createResume(resume: Omit<Resume, 'id' | 'createdAt' | 'updatedAt'>): Promise<Resume> {
    const response = await fetch(`${this.baseURL}/user/resumes`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(resume),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '創建簡歷失敗');
    }
    
    return response.json();
  }
  
  /**
   * 更新簡歷
   */
  async updateResume(resumeId: string, updates: Partial<Resume>): Promise<Resume> {
    const response = await fetch(`${this.baseURL}/user/resumes/${resumeId}`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新簡歷失敗');
    }
    
    return response.json();
  }
  
  /**
   * 刪除簡歷
   */
  async deleteResume(resumeId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/user/resumes/${resumeId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '刪除簡歷失敗');
    }
  }
  
  /**
   * 獲取用戶偏好設置
   */
  async getPreferences(): Promise<UserPreferences> {
    const response = await fetch(`${this.baseURL}/user/preferences`, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取偏好設置失敗');
    }
    
    return response.json();
  }
  
  /**
   * 更新用戶偏好設置
   */
  async updatePreferences(updates: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await fetch(`${this.baseURL}/user/preferences`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新偏好設置失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取用戶統計數據
   */
  async getStats(): Promise<UserState['stats']> {
    const response = await fetch(`${this.baseURL}/user/stats`, {
      headers: this.getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取統計數據失敗');
    }
    
    return response.json();
  }
}

const userService = new UserService();

/**
 * 用戶狀態 Store
 */
export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      profile: null,
      isProfileLoading: false,
      profileError: null,
      
      resumes: [],
      currentResume: null,
      isResumeLoading: false,
      resumeError: null,
      
      preferences: null,
      isPreferencesLoading: false,
      
      stats: null,
      
      /**
       * 獲取用戶資料
       */
      fetchProfile: async () => {
        set({ isProfileLoading: true, profileError: null });
        
        try {
          const profile = await userService.getProfile();
          set({ profile, isProfileLoading: false });
        } catch (error) {
          set({
            isProfileLoading: false,
            profileError: error instanceof Error ? error.message : '獲取用戶資料失敗',
          });
        }
      },
      
      /**
       * 更新用戶資料
       */
      updateProfile: async (updates: Partial<UserProfile>) => {
        set({ isProfileLoading: true, profileError: null });
        
        try {
          const updatedProfile = await userService.updateProfile(updates);
          set({ profile: updatedProfile, isProfileLoading: false });
        } catch (error) {
          set({
            isProfileLoading: false,
            profileError: error instanceof Error ? error.message : '更新用戶資料失敗',
          });
          throw error;
        }
      },
      
      /**
       * 上傳頭像
       */
      uploadAvatar: async (file: File) => {
        set({ isProfileLoading: true, profileError: null });
        
        try {
          const { avatarUrl } = await userService.uploadAvatar(file);
          set((state) => ({
            profile: state.profile ? { ...state.profile, avatar: avatarUrl } : null,
            isProfileLoading: false,
          }));
        } catch (error) {
          set({
            isProfileLoading: false,
            profileError: error instanceof Error ? error.message : '上傳頭像失敗',
          });
          throw error;
        }
      },
      
      /**
       * 獲取簡歷列表
       */
      fetchResumes: async () => {
        set({ isResumeLoading: true, resumeError: null });
        
        try {
          const resumes = await userService.getResumes();
          const defaultResume = resumes.find((resume) => resume.isDefault) || null;
          set({ resumes, currentResume: defaultResume, isResumeLoading: false });
        } catch (error) {
          set({
            isResumeLoading: false,
            resumeError: error instanceof Error ? error.message : '獲取簡歷列表失敗',
          });
        }
      },
      
      /**
       * 創建簡歷
       */
      createResume: async (resumeData: Omit<Resume, 'id' | 'createdAt' | 'updatedAt'>) => {
        set({ isResumeLoading: true, resumeError: null });
        
        try {
          const newResume = await userService.createResume(resumeData);
          set((state) => ({
            resumes: [...state.resumes, newResume],
            currentResume: newResume.isDefault ? newResume : state.currentResume,
            isResumeLoading: false,
          }));
        } catch (error) {
          set({
            isResumeLoading: false,
            resumeError: error instanceof Error ? error.message : '創建簡歷失敗',
          });
          throw error;
        }
      },
      
      /**
       * 更新簡歷
       */
      updateResume: async (resumeId: string, updates: Partial<Resume>) => {
        set({ isResumeLoading: true, resumeError: null });
        
        try {
          const updatedResume = await userService.updateResume(resumeId, updates);
          set((state) => ({
            resumes: state.resumes.map((resume) =>
              resume.id === resumeId ? updatedResume : resume
            ),
            currentResume: state.currentResume?.id === resumeId ? updatedResume : state.currentResume,
            isResumeLoading: false,
          }));
        } catch (error) {
          set({
            isResumeLoading: false,
            resumeError: error instanceof Error ? error.message : '更新簡歷失敗',
          });
          throw error;
        }
      },
      
      /**
       * 刪除簡歷
       */
      deleteResume: async (resumeId: string) => {
        set({ isResumeLoading: true, resumeError: null });
        
        try {
          await userService.deleteResume(resumeId);
          set((state) => ({
            resumes: state.resumes.filter((resume) => resume.id !== resumeId),
            currentResume: state.currentResume?.id === resumeId ? null : state.currentResume,
            isResumeLoading: false,
          }));
        } catch (error) {
          set({
            isResumeLoading: false,
            resumeError: error instanceof Error ? error.message : '刪除簡歷失敗',
          });
          throw error;
        }
      },
      
      /**
       * 設置默認簡歷
       */
      setDefaultResume: async (resumeId: string) => {
        try {
          await get().updateResume(resumeId, { isDefault: true });
          // 將其他簡歷設為非默認
          const { resumes } = get();
          for (const resume of resumes) {
            if (resume.id !== resumeId && resume.isDefault) {
              await get().updateResume(resume.id, { isDefault: false });
            }
          }
        } catch (error) {
          throw error;
        }
      },
      
      /**
       * 複製簡歷
       */
      duplicateResume: async (resumeId: string) => {
        const { resumes } = get();
        const originalResume = resumes.find((resume) => resume.id === resumeId);
        
        if (!originalResume) {
          throw new Error('找不到要複製的簡歷');
        }
        
        const duplicatedResume = {
          ...originalResume,
          name: `${originalResume.name} (副本)`,
          isDefault: false,
        };
        
        delete (duplicatedResume as any).id;
        delete (duplicatedResume as any).createdAt;
        delete (duplicatedResume as any).updatedAt;
        
        await get().createResume(duplicatedResume);
      },
      
      /**
       * 獲取偏好設置
       */
      fetchPreferences: async () => {
        set({ isPreferencesLoading: true });
        
        try {
          const preferences = await userService.getPreferences();
          set({ preferences, isPreferencesLoading: false });
        } catch (error) {
          set({ isPreferencesLoading: false });
          console.error('獲取偏好設置失敗:', error);
        }
      },
      
      /**
       * 更新偏好設置
       */
      updatePreferences: async (updates: Partial<UserPreferences>) => {
        set({ isPreferencesLoading: true });
        
        try {
          const updatedPreferences = await userService.updatePreferences(updates);
          set({ preferences: updatedPreferences, isPreferencesLoading: false });
        } catch (error) {
          set({ isPreferencesLoading: false });
          throw error;
        }
      },
      
      /**
       * 獲取統計數據
       */
      fetchStats: async () => {
        try {
          const stats = await userService.getStats();
          set({ stats });
        } catch (error) {
          console.error('獲取統計數據失敗:', error);
        }
      },
      
      /**
       * 獲取完整姓名
       */
      getFullName: () => {
        const { profile } = get();
        if (!profile) return '';
        return `${profile.firstName} ${profile.lastName}`.trim();
      },
      
      /**
       * 獲取默認簡歷
       */
      getDefaultResume: () => {
        const { resumes } = get();
        return resumes.find((resume) => resume.isDefault) || null;
      },
      
      /**
       * 清除用戶數據
       */
      clearUserData: () => {
        set({
          profile: null,
          resumes: [],
          currentResume: null,
          preferences: null,
          stats: null,
          profileError: null,
          resumeError: null,
        });
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        profile: state.profile,
        preferences: state.preferences,
      }),
    }
  )
);