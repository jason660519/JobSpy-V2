import { useState, useCallback } from 'react';
import { JobData } from '../components/results/JobCard';
import { SearchQuery } from '../components/search/SearchForm';
import { api } from '../services/api';

export interface SearchResult {
  jobs: JobData[];
  total_count: number;
  successful_platforms: number;
  confidence_score: number;
  execution_time: number;
  search_id: string;
  pagination: {
    page: number;
    per_page: number;
    has_next: boolean;
    total_pages: number;
  };
}

export const useJobSearch = () => {
  const [currentQuery, setCurrentQuery] = useState<SearchQuery | null>(null);
  const [searchResults, setSearchResults] = useState<JobData[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  const searchJobs = useCallback(async (query: SearchQuery): Promise<SearchResult | null> => {
    try {
      setIsSearching(true);
      setSearchError(null);
      setCurrentQuery(query);

      const response = await api.post('/jobs/search', {
        query: `${query.location} ${query.jobTitle}`.trim(),
        location: query.location,
        job_type: 'full-time', // 可以從 query 中獲取
        experience_level: '', // 可以從 query 中獲取
        use_ai: query.useAI,
        selected_platforms: query.selectedPlatforms
      });

      if (response.data.success) {
        const result = response.data.data;
        setSearchResults(result.jobs || []);
        return result;
      } else {
        throw new Error(response.data.error || '搜尋失敗');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '搜尋過程中發生錯誤';
      setSearchError(errorMessage);
      console.error('Search error:', error);
      return null;
    } finally {
      setIsSearching(false);
    }
  }, []);

  const loadMoreJobs = useCallback(async (page: number) => {
    if (!currentQuery) return;

    try {
      const response = await api.get(`/jobs/search/${currentQuery}`, {
        params: { page, per_page: 10 }
      });

      if (response.data.success) {
        const newJobs = response.data.data.jobs || [];
        setSearchResults(prev => [...prev, ...newJobs]);
        return newJobs;
      }
    } catch (error) {
      console.error('Load more error:', error);
    }
  }, [currentQuery]);

  return {
    searchJobs,
    loadMoreJobs,
    results: searchResults,
    isLoading: isSearching,
    error: searchError,
    currentQuery
  };
};