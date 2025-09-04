import React from 'react';
import { JobCard, JobData } from './JobCard';
import { Button } from '../ui/Button';
import { Plus, Loader2 } from 'lucide-react';

export interface JobListProps {
  jobs: JobData[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  onBookmark?: (job: JobData) => void;
  onApply?: (job: JobData) => void;
  bookmarkedJobs?: string[];
}

export const JobList: React.FC<JobListProps> = ({
  jobs,
  isLoading = false,
  hasMore = false,
  onLoadMore,
  onBookmark,
  onApply,
  bookmarkedJobs = []
}) => {
  if (isLoading && jobs.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">正在載入職位...</p>
        </div>
      </div>
    );
  }
  
  if (jobs.length === 0 && !isLoading) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          未找到符合條件的職位
        </h3>
        <p className="text-gray-600">
          請嘗試調整搜尋條件或關鍵字
        </p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* 職位列表 */}
      <div className="space-y-4">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onBookmark={onBookmark}
            onApply={onApply}
            isBookmarked={bookmarkedJobs.includes(job.id)}
          />
        ))}
      </div>
      
      {/* 載入更多按鈕 */}
      {hasMore && (
        <div className="text-center pt-6">
          <Button
            variant="outline"
            onClick={onLoadMore}
            loading={isLoading}
            icon={<Plus className="h-4 w-4" />}
          >
            {isLoading ? '載入中...' : '載入更多職位'}
          </Button>
        </div>
      )}
      
      {/* 載入更多時的載入指示器 */}
      {isLoading && jobs.length > 0 && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-blue-600 mr-2" />
          <span className="text-gray-600">載入更多職位中...</span>
        </div>
      )}
    </div>
  );
};
