export interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  requirements: string[];
  skills: string[];
  salary_range?: {
    min: number;
    max: number;
    currency: string;
  };
  job_type: string;
  experience_level: string;
  remote_friendly: boolean;
  source: string;
  source_url: string;
  posted_date: string;
  relevance_score?: number;
}

export interface SearchRequest {
  query: string;
  location?: string;
  job_type?: string;
  experience_level?: string;
  salary_range?: {
    min: number;
    max: number;
  };
  use_ai?: boolean;
}

export interface SearchFilters {
  location: string;
  jobType: string;
  experienceLevel: string;
  salaryRange: {
    min: number;
    max: number;
  };
  useAI: boolean;
}

export interface JobSearchResponse {
  jobs: JobListing[];
  total_count: number;
  search_metadata: {
    query_analysis: any;
    sources_used: string[];
    ai_enhancement_used: boolean;
    processing_time_ms: number;
  };
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}