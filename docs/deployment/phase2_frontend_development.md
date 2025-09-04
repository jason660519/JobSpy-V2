# Phase 2: Frontend Development

## Objective
Create a modern React application that provides the same functionality as the current Flask web interface, with improved performance and user experience.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite (for fast development and builds)
- **Styling**: Tailwind CSS + Headless UI
- **State Management**: React Query + Zustand
- **HTTP Client**: Axios
- **Deployment**: GitHub Pages

## Project Setup

### 2.1 Initialize React Project

```bash
# Create new React project with Vite
npm create vite@latest jobspy-frontend -- --template react-ts

cd jobspy-frontend

# Install additional dependencies
npm install @tanstack/react-query zustand axios
npm install -D tailwindcss postcss autoprefixer @types/node

# Initialize Tailwind CSS
npx tailwindcss init -p
```

### 2.2 Project Structure

```
jobspy-frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── forms/
│   │   │   ├── JobSearchForm.tsx
│   │   │   └── FormFields.tsx
│   │   └── results/
│   │       ├── JobTable.tsx
│   │       ├── JobCard.tsx
│   │       ├── ExportButton.tsx
│   │       └── Pagination.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── SearchPage.tsx
│   │   └── AboutPage.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── jobService.ts
│   │   └── types.ts
│   ├── stores/
│   │   ├── useJobStore.ts
│   │   └── useUIStore.ts
│   ├── hooks/
│   │   ├── useJobSearch.ts
│   │   └── useDebounce.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── styles/
│   │   └── globals.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── README.md
```

## Detailed Implementation

### 2.3 API Service Layer

**src/services/types.ts:**
```typescript
export interface JobSearchParams {
  site_name: string;
  search_term?: string;
  location?: string;
  results_wanted?: number;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  description: string;
  url: string;
  date_posted?: string;
  job_type?: string;
}

export interface JobSearchResponse {
  success: boolean;
  jobs: Job[];
  count: number;
  timestamp: string;
}

export interface ApiError {
  error: string;
  details?: any;
}

export interface AsyncTaskResponse {
  task_id: string;
  status: 'processing' | 'completed' | 'failed';
  message?: string;
}

export interface TaskStatusResponse {
  status: 'processing' | 'completed' | 'failed';
  progress?: number;
  jobs?: Job[];
  count?: number;
  error?: string;
}
```

**src/services/api.ts:**
```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://web-production-f5cc.up.railway.app';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use((config) => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
```

**src/services/jobService.ts:**
```typescript
import apiClient from './api';
import { JobSearchParams, JobSearchResponse, AsyncTaskResponse, TaskStatusResponse } from './types';

export class JobService {
  // Health check
  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }

  // Synchronous job search
  static async searchJobs(params: JobSearchParams): Promise<JobSearchResponse> {
    const response = await apiClient.post('/search', params);
    return response.data;
  }

  // Asynchronous job search for large requests
  static async searchJobsAsync(params: JobSearchParams): Promise<AsyncTaskResponse> {
    const response = await apiClient.post('/search/async', params);
    return response.data;
  }

  // Check async task status
  static async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
    const response = await apiClient.get(`/task/${taskId}`);
    return response.data;
  }

  // Export jobs data
  static async exportJobs(jobs: any[], format: 'csv' | 'json' = 'csv'): Promise<{ download_url: string; filename: string }> {
    const response = await apiClient.post('/export', { jobs, format });
    return response.data;
  }
}
```

### 2.4 State Management

**src/stores/useJobStore.ts:**
```typescript
import { create } from 'zustand';
import { Job, JobSearchParams } from '../services/types';

interface JobState {
  // State
  jobs: Job[];
  isLoading: boolean;
  error: string | null;
  searchParams: JobSearchParams | null;
  totalCount: number;
  currentPage: number;
  
  // Actions
  setJobs: (jobs: Job[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSearchParams: (params: JobSearchParams) => void;
  setCurrentPage: (page: number) => void;
  clearJobs: () => void;
}

export const useJobStore = create<JobState>((set) => ({
  // Initial state
  jobs: [],
  isLoading: false,
  error: null,
  searchParams: null,
  totalCount: 0,
  currentPage: 1,
  
  // Actions
  setJobs: (jobs) => set({ jobs, totalCount: jobs.length }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setSearchParams: (searchParams) => set({ searchParams }),
  setCurrentPage: (currentPage) => set({ currentPage }),
  clearJobs: () => set({ jobs: [], totalCount: 0, currentPage: 1, error: null }),
}));
```

**src/stores/useUIStore.ts:**
```typescript
import { create } from 'zustand';

interface UIState {
  // Theme
  isDarkMode: boolean;
  
  // Modals and overlays
  isExportModalOpen: boolean;
  
  // Notifications
  notifications: Array<{
    id: string;
    type: 'success' | 'error' | 'info' | 'warning';
    message: string;
    timestamp: number;
  }>;
  
  // Actions
  toggleDarkMode: () => void;
  setExportModalOpen: (open: boolean) => void;
  addNotification: (type: UIState['notifications'][0]['type'], message: string) => void;
  removeNotification: (id: string) => void;
}

export const useUIStore = create<UIState>((set, get) => ({
  // Initial state
  isDarkMode: false,
  isExportModalOpen: false,
  notifications: [],
  
  // Actions
  toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
  setExportModalOpen: (isExportModalOpen) => set({ isExportModalOpen }),
  
  addNotification: (type, message) => {
    const id = Date.now().toString();
    const notification = { id, type, message, timestamp: Date.now() };
    set((state) => ({ 
      notifications: [...state.notifications, notification] 
    }));
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      get().removeNotification(id);
    }, 5000);
  },
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),
}));
```

### 2.5 Custom Hooks

**src/hooks/useJobSearch.ts:**
```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { JobService } from '../services/jobService';
import { JobSearchParams } from '../services/types';
import { useJobStore } from '../stores/useJobStore';
import { useUIStore } from '../stores/useUIStore';

export const useJobSearch = () => {
  const { setJobs, setLoading, setError } = useJobStore();
  const { addNotification } = useUIStore();

  const searchMutation = useMutation({
    mutationFn: (params: JobSearchParams) => JobService.searchJobs(params),
    onMutate: () => {
      setLoading(true);
      setError(null);
    },
    onSuccess: (data) => {
      setJobs(data.jobs);
      setLoading(false);
      addNotification('success', `Found ${data.count} jobs`);
    },
    onError: (error: any) => {
      setLoading(false);
      const errorMessage = error.response?.data?.error || 'Failed to search jobs';
      setError(errorMessage);
      addNotification('error', errorMessage);
    },
  });

  const asyncSearchMutation = useMutation({
    mutationFn: (params: JobSearchParams) => JobService.searchJobsAsync(params),
    onSuccess: (data) => {
      addNotification('info', 'Job search started. You will be notified when complete.');
      // Start polling for task status
      pollTaskStatus(data.task_id);
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.error || 'Failed to start job search';
      addNotification('error', errorMessage);
    },
  });

  // Poll task status for async searches
  const pollTaskStatus = (taskId: string) => {
    const interval = setInterval(async () => {
      try {
        const status = await JobService.getTaskStatus(taskId);
        
        if (status.status === 'completed') {
          clearInterval(interval);
          setJobs(status.jobs || []);
          setLoading(false);
          addNotification('success', `Job search completed! Found ${status.count} jobs`);
        } else if (status.status === 'failed') {
          clearInterval(interval);
          setLoading(false);
          setError(status.error || 'Job search failed');
          addNotification('error', status.error || 'Job search failed');
        }
      } catch (error) {
        clearInterval(interval);
        setLoading(false);
        addNotification('error', 'Failed to check search status');
      }
    }, 2000); // Poll every 2 seconds
  };

  return {
    searchJobs: searchMutation.mutate,
    searchJobsAsync: asyncSearchMutation.mutate,
    isSearching: searchMutation.isPending || asyncSearchMutation.isPending,
  };
};

// Health check hook
export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: JobService.healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });
};
```

**src/hooks/useDebounce.ts:**
```typescript
import { useEffect, useState } from 'react';

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};
```

### 2.6 Components

**src/components/forms/JobSearchForm.tsx:**
```typescript
import React, { useState } from 'react';
import { useJobSearch } from '../../hooks/useJobSearch';
import { JobSearchParams } from '../../services/types';
import { useJobStore } from '../../stores/useJobStore';

const SUPPORTED_SITES = [
  { value: 'indeed', label: 'Indeed' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'glassdoor', label: 'Glassdoor' },
  { value: 'zip_recruiter', label: 'ZipRecruiter' },
];

export const JobSearchForm: React.FC = () => {
  const [formData, setFormData] = useState<JobSearchParams>({
    site_name: 'indeed',
    search_term: '',
    location: '',
    results_wanted: 20,
  });

  const { searchJobs, searchJobsAsync, isSearching } = useJobSearch();
  const { clearJobs, setSearchParams } = useJobStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    clearJobs();
    setSearchParams(formData);

    // Use async search for large requests
    if (formData.results_wanted && formData.results_wanted > 50) {
      searchJobsAsync(formData);
    } else {
      searchJobs(formData);
    }
  };

  const handleInputChange = (field: keyof JobSearchParams, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Job Site Selection */}
        <div>
          <label htmlFor="site_name" className="block text-sm font-medium text-gray-700 mb-2">
            Job Site
          </label>
          <select
            id="site_name"
            value={formData.site_name}
            onChange={(e) => handleInputChange('site_name', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          >
            {SUPPORTED_SITES.map(site => (
              <option key={site.value} value={site.value}>
                {site.label}
              </option>
            ))}
          </select>
        </div>

        {/* Search Term */}
        <div>
          <label htmlFor="search_term" className="block text-sm font-medium text-gray-700 mb-2">
            Job Title / Keywords
          </label>
          <input
            type="text"
            id="search_term"
            value={formData.search_term}
            onChange={(e) => handleInputChange('search_term', e.target.value)}
            placeholder="e.g., Python Developer, Data Scientist"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Location */}
        <div>
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            id="location"
            value={formData.location}
            onChange={(e) => handleInputChange('location', e.target.value)}
            placeholder="e.g., Taipei, Taiwan"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Results Count */}
        <div>
          <label htmlFor="results_wanted" className="block text-sm font-medium text-gray-700 mb-2">
            Number of Results
          </label>
          <select
            id="results_wanted"
            value={formData.results_wanted}
            onChange={(e) => handleInputChange('results_wanted', parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={10}>10 jobs</option>
            <option value={20}>20 jobs</option>
            <option value={50}>50 jobs</option>
            <option value={100}>100 jobs (slower)</option>
          </select>
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-center">
        <button
          type="submit"
          disabled={isSearching}
          className={`px-8 py-3 rounded-md font-medium text-white transition-colors ${
            isSearching
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
          }`}
        >
          {isSearching ? 'Searching Jobs...' : 'Search Jobs'}
        </button>
      </div>
    </form>
  );
};
```

**src/components/results/JobTable.tsx:**
```typescript
import React from 'react';
import { Job } from '../../services/types';
import { useJobStore } from '../../stores/useJobStore';

interface JobTableProps {
  jobs: Job[];
}

export const JobTable: React.FC<JobTableProps> = ({ jobs }) => {
  const { currentPage } = useJobStore();
  const itemsPerPage = 10;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const displayedJobs = jobs.slice(startIndex, startIndex + itemsPerPage);

  const formatSalary = (salary: string | undefined) => {
    if (!salary) return 'Not specified';
    return salary;
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return dateString;
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Job Title
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Company
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Location
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Salary
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Posted Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {displayedJobs.map((job, index) => (
            <tr key={job.id || index} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{job.title}</div>
                <div className="text-sm text-gray-500">{job.job_type}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {job.company}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {job.location}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatSalary(job.salary)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatDate(job.date_posted)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-900"
                >
                  View Job
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**src/pages/HomePage.tsx:**
```typescript
import React from 'react';
import { JobSearchForm } from '../components/forms/JobSearchForm';
import { JobTable } from '../components/results/JobTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ExportButton } from '../components/results/ExportButton';
import { Pagination } from '../components/results/Pagination';
import { useJobStore } from '../stores/useJobStore';
import { useHealthCheck } from '../hooks/useJobSearch';

export const HomePage: React.FC = () => {
  const { jobs, isLoading, error, totalCount } = useJobStore();
  const { data: healthData, isError: healthError } = useHealthCheck();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">JobSpy</h1>
            <div className="flex items-center space-x-4">
              {healthError && (
                <span className="text-red-500 text-sm">API Offline</span>
              )}
              {healthData && (
                <span className="text-green-500 text-sm">API Online</span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Form */}
        <div className="mb-8">
          <JobSearchForm />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <LoadingSpinner />
            <span className="ml-2 text-gray-600">Searching for jobs...</span>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Search Error
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  {error}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {jobs.length > 0 && (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                Found {totalCount} jobs
              </h2>
              <ExportButton jobs={jobs} />
            </div>

            {/* Job Table */}
            <JobTable jobs={jobs} />

            {/* Pagination */}
            {totalCount > 10 && <Pagination />}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && jobs.length === 0 && (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start Your Job Search
            </h3>
            <p className="text-gray-600">
              Use the search form above to find job opportunities
            </p>
          </div>
        )}
      </main>
    </div>
  );
};
```

## Environment Configuration

**Create .env files:**

**.env (development):**
```
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=JobSpy - Job Search Tool
```

**.env.production:**
```
VITE_API_URL=https://web-production-f5cc.up.railway.app
VITE_APP_TITLE=JobSpy - Job Search Tool
```

## Build Configuration

**vite.config.ts:**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/jobspy/', // Your GitHub Pages repository name
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  server: {
    port: 3000,
    open: true,
  },
})
```

**package.json scripts:**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "deploy": "npm run build && gh-pages -d dist"
  }
}
```

## Completion Checklist

- [ ] Initialize React project with Vite and TypeScript
- [ ] Set up Tailwind CSS and component library
- [ ] Create API service layer and types
- [ ] Implement state management with Zustand
- [ ] Create custom hooks for data fetching
- [ ] Build form components for job search
- [ ] Create results display components
- [ ] Implement loading and error states
- [ ] Add pagination and export functionality
- [ ] Configure environment variables
- [ ] Set up build configuration for GitHub Pages
- [ ] Test all components locally
- [ ] Optimize performance and bundle size

## Next Steps

After completing Phase 2, proceed to [Phase 3: Deployment](./phase3_deployment.md) to deploy both the API and frontend to their respective platforms.