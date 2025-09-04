/**
 * 搜索狀態管理 Store
 * 管理職位搜索、篩選、排序等相關狀態
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface SearchQuery {
  keyword: string;
  location: string;
  salaryMin?: number;
  salaryMax?: number;
  jobType?: string[];
  experience?: string;
  companySize?: string;
  skills?: string[];
  workMode?: string;
  publishedDate?: string;
  platforms?: string[];
}

export interface SearchFilters {
  jobTypes: string[];
  experienceLevels: string[];
  companySizes: string[];
  workModes: string[];
  skills: string[];
  salaryRange: [number, number];
  publishedDate: string;
}

export interface SearchState {
  // 搜索狀態
  query: SearchQuery;
  filters: SearchFilters;
  isSearching: boolean;
  error: string | null;
  
  // 結果狀態
  results: any[];
  totalResults: number;
  currentPage: number;
  pageSize: number;
  sortBy: string;
  viewMode: 'grid' | 'list';
  
  // 搜索歷史
  searchHistory: SearchQuery[];
  
  // 快速篩選標籤
  quickFilters: string[];
  
  // 動作
  setQuery: (query: Partial<SearchQuery>) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  search: (query?: SearchQuery) => Promise<void>;
  clearSearch: () => void;
  clearError: () => void;
  
  // 結果管理
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
  setSortBy: (sortBy: string) => void;
  setViewMode: (mode: 'grid' | 'list') => void;
  
  // 歷史管理
  addToHistory: (query: SearchQuery) => void;
  clearHistory: () => void;
  
  // 快速篩選
  addQuickFilter: (filter: string) => void;
  removeQuickFilter: (filter: string) => void;
  clearQuickFilters: () => void;
}

/**
 * 搜索 API 服務
 */
class SearchService {
  private baseURL = 'http://localhost:8000/api/v1';
  
  /**
   * 搜索職位
   */
  async searchJobs(query: SearchQuery, page: number = 1, pageSize: number = 20, sortBy: string = 'relevance') {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      sort_by: sortBy,
    });
    
    // 添加搜索參數
    if (query.keyword) params.append('keyword', query.keyword);
    if (query.location) params.append('location', query.location);
    if (query.salaryMin) params.append('salary_min', query.salaryMin.toString());
    if (query.salaryMax) params.append('salary_max', query.salaryMax.toString());
    if (query.jobType?.length) params.append('job_type', query.jobType.join(','));
    if (query.experience) params.append('experience', query.experience);
    if (query.companySize) params.append('company_size', query.companySize);
    if (query.skills?.length) params.append('skills', query.skills.join(','));
    if (query.workMode) params.append('work_mode', query.workMode);
    if (query.publishedDate) params.append('published_date', query.publishedDate);
    if (query.platforms?.length) params.append('platforms', query.platforms.join(','));
    
    const response = await fetch(`${this.baseURL}/jobs/search?${params}`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || '搜索失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取搜索建議
   */
  async getSearchSuggestions(query: string) {
    const response = await fetch(`${this.baseURL}/jobs/suggestions?q=${encodeURIComponent(query)}`);
    
    if (!response.ok) {
      throw new Error('獲取建議失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取熱門關鍵詞
   */
  async getPopularKeywords() {
    const response = await fetch(`${this.baseURL}/jobs/popular-keywords`);
    
    if (!response.ok) {
      throw new Error('獲取熱門關鍵詞失敗');
    }
    
    return response.json();
  }
  
  /**
   * 獲取篩選器選項
   */
  async getFilterOptions() {
    const response = await fetch(`${this.baseURL}/jobs/filter-options`);
    
    if (!response.ok) {
      throw new Error('獲取篩選器選項失敗');
    }
    
    return response.json();
  }
}

const searchService = new SearchService();

/**
 * 搜索狀態 Store
 */
export const useSearchStore = create<SearchState>()(
  persist(
    (set, get) => ({
      // 初始狀態
      query: {
        keyword: '',
        location: '',
        platforms: ['104', 'linkedin', 'indeed'],
      },
      filters: {
        jobTypes: [],
        experienceLevels: [],
        companySizes: [],
        workModes: [],
        skills: [],
        salaryRange: [0, 200000],
        publishedDate: 'all',
      },
      isSearching: false,
      error: null,
      
      results: [],
      totalResults: 0,
      currentPage: 1,
      pageSize: 20,
      sortBy: 'relevance',
      viewMode: 'grid',
      
      searchHistory: [],
      quickFilters: [],
      
      /**
       * 設置搜索查詢
       */
      setQuery: (newQuery: Partial<SearchQuery>) => {
        set((state) => ({
          query: { ...state.query, ...newQuery },
        }));
      },
      
      /**
       * 設置篩選器
       */
      setFilters: (newFilters: Partial<SearchFilters>) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters },
        }));
      },
      
      /**
       * 執行搜索
       */
      search: async (searchQuery?: SearchQuery) => {
        const { query, currentPage, pageSize, sortBy } = get();
        const finalQuery = searchQuery || query;
        
        set({ isSearching: true, error: null });
        
        try {
          const response = await searchService.searchJobs(
            finalQuery,
            currentPage,
            pageSize,
            sortBy
          );
          
          set({
            results: response.jobs,
            totalResults: response.total,
            isSearching: false,
          });
          
          // 添加到搜索歷史
          get().addToHistory(finalQuery);
        } catch (error) {
          set({
            isSearching: false,
            error: error instanceof Error ? error.message : '搜索失敗',
          });
        }
      },
      
      /**
       * 清除搜索
       */
      clearSearch: () => {
        set({
          results: [],
          totalResults: 0,
          currentPage: 1,
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
       * 設置頁碼
       */
      setPage: (page: number) => {
        set({ currentPage: page });
        get().search();
      },
      
      /**
       * 設置每頁數量
       */
      setPageSize: (size: number) => {
        set({ pageSize: size, currentPage: 1 });
        get().search();
      },
      
      /**
       * 設置排序方式
       */
      setSortBy: (sortBy: string) => {
        set({ sortBy, currentPage: 1 });
        get().search();
      },
      
      /**
       * 設置視圖模式
       */
      setViewMode: (mode: 'grid' | 'list') => {
        set({ viewMode: mode });
      },
      
      /**
       * 添加到搜索歷史
       */
      addToHistory: (query: SearchQuery) => {
        set((state) => {
          const history = state.searchHistory.filter(
            (item) => JSON.stringify(item) !== JSON.stringify(query)
          );
          return {
            searchHistory: [query, ...history].slice(0, 10), // 保留最近 10 次搜索
          };
        });
      },
      
      /**
       * 清除搜索歷史
       */
      clearHistory: () => {
        set({ searchHistory: [] });
      },
      
      /**
       * 添加快速篩選
       */
      addQuickFilter: (filter: string) => {
        set((state) => {
          if (!state.quickFilters.includes(filter)) {
            return {
              quickFilters: [...state.quickFilters, filter],
            };
          }
          return state;
        });
      },
      
      /**
       * 移除快速篩選
       */
      removeQuickFilter: (filter: string) => {
        set((state) => ({
          quickFilters: state.quickFilters.filter((f) => f !== filter),
        }));
      },
      
      /**
       * 清除快速篩選
       */
      clearQuickFilters: () => {
        set({ quickFilters: [] });
      },
    }),
    {
      name: 'search-storage',
      partialize: (state) => ({
        searchHistory: state.searchHistory,
        viewMode: state.viewMode,
        pageSize: state.pageSize,
      }),
    }
  )
);