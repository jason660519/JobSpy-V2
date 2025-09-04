/**
 * 職位狀態管理 Store
 * 管理職位收藏、申請、詳情等相關狀態
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: {
    min?: number;
    max?: number;
    currency: string;
  };
  description: string;
  requirements: string[];
  benefits?: string[];
  jobType: string;
  experience: string;
  skills: string[];
  publishedDate: string;
  deadline?: string;
  platform: string;
  url: string;
  companyLogo?: string;
  companySize?: string;
  workMode?: string;
  isRemote?: boolean;
  isUrgent?: boolean;
  viewCount?: number;
  applicationCount?: number;
}

export interface JobApplication {
  id: string;
  jobId: string;
  status: 'pending' | 'reviewing' | 'interview' | 'rejected' | 'accepted';
  appliedDate: string;
  notes?: string;
  resumeId?: string;
  coverLetter?: string;
  interviewDate?: string;
  feedback?: string;
}

export interface JobState {
  // 職位詳情
  currentJob: Job | null;
  isLoadingJob: boolean;
  jobError: string | null;
  
  // 收藏職位
  favoriteJobs: Job[];
  isFavoriteLoading: boolean;
  
  // 申請記錄
  applications: JobApplication[];
  isApplicationLoading: boolean;
  
  // 瀏覽歷史
  viewHistory: Job[];
  
  // 推薦職位
  recommendedJobs: Job[];
  isRecommendationLoading: boolean;
  
  // 相似職位
  similarJobs: Job[];
  
  // 動作
  fetchJob: (jobId: string) => Promise<void>;
  clearCurrentJob: () => void;
  
  // 收藏管理
  addToFavorites: (job: Job) => Promise<void>;
  removeFromFavorites: (jobId: string) => Promise<void>;
  isFavorite: (jobId: string) => boolean;
  fetchFavorites: () => Promise<void>;
  
  // 申請管理
  applyToJob: (jobId: string, applicationData: Partial<JobApplication>) => Promise<void>;
  updateApplication: (applicationId: string, updates: Partial<JobApplication>) => Promise<void>;
  fetchApplications: () => Promise<void>;
  getApplicationByJobId: (jobId: string) => JobApplication | undefined;
  
  // 瀏覽歷史
  addToHistory: (job: Job) => void;
  clearHistory: () => void;
  
  // 推薦系統
  fetchRecommendations: () => Promise<void>;
  fetchSimilarJobs: (jobId: string) => Promise<void>;
  
  // 統計
  getApplicationStats: () => {
    total: number;
    pending: number;
    reviewing: number;
    interview: number;
    rejected: number;
    accepted: number;
  };
}

/**
 * 職位 API 服務
 */
class JobService {
  private baseURL = 'http://localhost:8000/api/v1';
  
  /**
   * 獲取職位詳情
   */
  async getJob(jobId: string): Promise<Job> {
    const response = await fetch(`${this.baseURL}/jobs/${jobId}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取職位詳情失敗');
    }
    
    return response.json();
  }
  
  /**
   * 添加到收藏
   */
  async addToFavorites(jobId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/jobs/${jobId}/favorite`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '添加收藏失敗');
    }
  }
  
  /**
   * 從收藏中移除
   */
  async removeFromFavorites(jobId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/jobs/${jobId}/favorite`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '移除收藏失敗');
    }
  }
  
  /**
   * 獲取收藏列表
   */
  async getFavorites(): Promise<Job[]> {
    const response = await fetch(`${this.baseURL}/jobs/favorites`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取收藏列表失敗');
    }
    
    return response.json();
  }
  
  /**
   * 申請職位
   */
  async applyToJob(jobId: string, applicationData: Partial<JobApplication>): Promise<JobApplication> {
    const response = await fetch(`${this.baseURL}/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(applicationData),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '申請職位失敗');
    }
    
    return response.json();
  }
  
  /**
   * 更新申請狀態
   */
  async updateApplication(applicationId: string, updates: Partial<JobApplication>): Promise<JobApplication> {
    const response = await fetch(`${this.baseURL}/applications/${applicationId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '更新申請失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取申請記錄
   */
  async getApplications(): Promise<JobApplication[]> {
    const response = await fetch(`${this.baseURL}/applications`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取申請記錄失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取推薦職位
   */
  async getRecommendations(): Promise<Job[]> {
    const response = await fetch(`${this.baseURL}/jobs/recommendations`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取推薦職位失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取相似職位
   */
  async getSimilarJobs(jobId: string): Promise<Job[]> {
    const response = await fetch(`${this.baseURL}/jobs/${jobId}/similar`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '獲取相似職位失敗');
    }
    
    return response.json();
  }
}

const jobService = new JobService();

/**
 * 職位狀態 Store
 */
export const useJobStore = create<JobState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      currentJob: null,
      isLoadingJob: false,
      jobError: null,
      
      favoriteJobs: [],
      isFavoriteLoading: false,
      
      applications: [],
      isApplicationLoading: false,
      
      viewHistory: [],
      
      recommendedJobs: [],
      isRecommendationLoading: false,
      
      similarJobs: [],
      
      /**
       * 獲取職位詳情
       */
      fetchJob: async (jobId: string) => {
        set({ isLoadingJob: true, jobError: null });
        
        try {
          const job = await jobService.getJob(jobId);
          set({ currentJob: job, isLoadingJob: false });
          
          // 添加到瀏覽歷史
          get().addToHistory(job);
          
          // 獲取相似職位
          get().fetchSimilarJobs(jobId);
        } catch (error) {
          set({
            isLoadingJob: false,
            jobError: error instanceof Error ? error.message : '獲取職位詳情失敗',
          });
        }
      },
      
      /**
       * 清除當前職位
       */
      clearCurrentJob: () => {
        set({ currentJob: null, jobError: null, similarJobs: [] });
      },
      
      /**
       * 添加到收藏
       */
      addToFavorites: async (job: Job) => {
        set({ isFavoriteLoading: true });
        
        try {
          await jobService.addToFavorites(job.id);
          set((state) => ({
            favoriteJobs: [...state.favoriteJobs, job],
            isFavoriteLoading: false,
          }));
        } catch (error) {
          set({ isFavoriteLoading: false });
          throw error;
        }
      },
      
      /**
       * 從收藏中移除
       */
      removeFromFavorites: async (jobId: string) => {
        set({ isFavoriteLoading: true });
        
        try {
          await jobService.removeFromFavorites(jobId);
          set((state) => ({
            favoriteJobs: state.favoriteJobs.filter((job) => job.id !== jobId),
            isFavoriteLoading: false,
          }));
        } catch (error) {
          set({ isFavoriteLoading: false });
          throw error;
        }
      },
      
      /**
       * 檢查是否已收藏
       */
      isFavorite: (jobId: string) => {
        return get().favoriteJobs.some((job) => job.id === jobId);
      },
      
      /**
       * 獲取收藏列表
       */
      fetchFavorites: async () => {
        set({ isFavoriteLoading: true });
        
        try {
          const favorites = await jobService.getFavorites();
          set({ favoriteJobs: favorites, isFavoriteLoading: false });
        } catch (error) {
          set({ isFavoriteLoading: false });
          console.error('獲取收藏列表失敗:', error);
        }
      },
      
      /**
       * 申請職位
       */
      applyToJob: async (jobId: string, applicationData: Partial<JobApplication>) => {
        set({ isApplicationLoading: true });
        
        try {
          const application = await jobService.applyToJob(jobId, applicationData);
          set((state) => ({
            applications: [...state.applications, application],
            isApplicationLoading: false,
          }));
        } catch (error) {
          set({ isApplicationLoading: false });
          throw error;
        }
      },
      
      /**
       * 更新申請狀態
       */
      updateApplication: async (applicationId: string, updates: Partial<JobApplication>) => {
        set({ isApplicationLoading: true });
        
        try {
          const updatedApplication = await jobService.updateApplication(applicationId, updates);
          set((state) => ({
            applications: state.applications.map((app) =>
              app.id === applicationId ? updatedApplication : app
            ),
            isApplicationLoading: false,
          }));
        } catch (error) {
          set({ isApplicationLoading: false });
          throw error;
        }
      },
      
      /**
       * 獲取申請記錄
       */
      fetchApplications: async () => {
        set({ isApplicationLoading: true });
        
        try {
          const applications = await jobService.getApplications();
          set({ applications, isApplicationLoading: false });
        } catch (error) {
          set({ isApplicationLoading: false });
          console.error('獲取申請記錄失敗:', error);
        }
      },
      
      /**
       * 根據職位ID獲取申請記錄
       */
      getApplicationByJobId: (jobId: string) => {
        return get().applications.find((app) => app.jobId === jobId);
      },
      
      /**
       * 添加到瀏覽歷史
       */
      addToHistory: (job: Job) => {
        set((state) => {
          const history = state.viewHistory.filter((item) => item.id !== job.id);
          return {
            viewHistory: [job, ...history].slice(0, 50), // 保留最近 50 個瀏覽記錄
          };
        });
      },
      
      /**
       * 清除瀏覽歷史
       */
      clearHistory: () => {
        set({ viewHistory: [] });
      },
      
      /**
       * 獲取推薦職位
       */
      fetchRecommendations: async () => {
        set({ isRecommendationLoading: true });
        
        try {
          const recommendations = await jobService.getRecommendations();
          set({ recommendedJobs: recommendations, isRecommendationLoading: false });
        } catch (error) {
          set({ isRecommendationLoading: false });
          console.error('獲取推薦職位失敗:', error);
        }
      },
      
      /**
       * 獲取相似職位
       */
      fetchSimilarJobs: async (jobId: string) => {
        try {
          const similarJobs = await jobService.getSimilarJobs(jobId);
          set({ similarJobs });
        } catch (error) {
          console.error('獲取相似職位失敗:', error);
        }
      },
      
      /**
       * 獲取申請統計
       */
      getApplicationStats: () => {
        const { applications } = get();
        
        return {
          total: applications.length,
          pending: applications.filter((app) => app.status === 'pending').length,
          reviewing: applications.filter((app) => app.status === 'reviewing').length,
          interview: applications.filter((app) => app.status === 'interview').length,
          rejected: applications.filter((app) => app.status === 'rejected').length,
          accepted: applications.filter((app) => app.status === 'accepted').length,
        };
      },
    }),
    {
      name: 'job-storage',
      partialize: (state) => ({
        favoriteJobs: state.favoriteJobs,
        viewHistory: state.viewHistory,
        applications: state.applications,
      }),
    }
  )
);