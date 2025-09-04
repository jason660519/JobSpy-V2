import React from 'react';
import { 
  MapPin, 
  Building, 
  Calendar, 
  ExternalLink, 
  Heart, 
  Send,
  DollarSign
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

export interface JobData {
  id: string;
  title: string;
  company: string;
  location: string;
  description?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  job_type?: string;
  is_remote?: boolean;
  site: string;
  job_url?: string;
  job_url_direct?: string;
  date_posted?: string;
}

export interface JobCardProps {
  job: JobData;
  onBookmark?: (job: JobData) => void;
  onApply?: (job: JobData) => void;
  isBookmarked?: boolean;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onBookmark,
  onApply,
  isBookmarked = false
}) => {
  const formatSalary = (min?: number, max?: number, currency?: string) => {
    if (!min && !max) return null;
    
    const currencySymbol = currency || '';
    
    if (min && max) {
      return `${currencySymbol}${min.toLocaleString()} - ${currencySymbol}${max.toLocaleString()}`;
    } else if (min) {
      return `${currencySymbol}${min.toLocaleString()}+`;
    } else if (max) {
      return `最高 ${currencySymbol}${max.toLocaleString()}`;
    }
    
    return null;
  };
  
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return null;
    
    try {
      const date = new Date(dateStr);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) {
        return '1 天前';
      } else if (diffDays < 7) {
        return `${diffDays} 天前`;
      } else {
        return date.toLocaleDateString('zh-TW');
      }
    } catch (e) {
      return dateStr;
    }
  };
  
  const salaryText = formatSalary(job.salary_min, job.salary_max, job.salary_currency);
  const dateText = formatDate(job.date_posted);
  
  return (
    <Card className="hover:shadow-lg transition-all duration-200" hover>
      <div className="p-6">
        {/* 標題和薪資 */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {job.job_url ? (
                <a 
                  href={job.job_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                >
                  {job.title}
                </a>
              ) : (
                job.title
              )}
            </h3>
            
            {/* 標籤 */}
            <div className="flex flex-wrap gap-2 mb-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {job.site}
              </span>
              {job.job_type && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {job.job_type}
                </span>
              )}
              {job.is_remote && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                  遠端工作
                </span>
              )}
            </div>
          </div>
          
          {salaryText && (
            <div className="text-right">
              <div className="flex items-center text-green-600 font-semibold">
                <DollarSign className="h-4 w-4 mr-1" />
                {salaryText}
              </div>
            </div>
          )}
        </div>
        
        {/* 公司信息 */}
        <div className="flex items-center text-gray-600 mb-2">
          <Building className="h-4 w-4 mr-2 text-blue-500" />
          <span className="font-medium">{job.company}</span>
        </div>
        
        {/* 地點 */}
        <div className="flex items-center text-gray-600 mb-3">
          <MapPin className="h-4 w-4 mr-2 text-gray-500" />
          <span>{job.location}</span>
        </div>
        
        {/* 描述 */}
        {job.description && (
          <div className="mb-4">
            <p className="text-gray-600 text-sm line-clamp-3">
              {job.description}
            </p>
          </div>
        )}
        
        {/* 底部信息 */}
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            {dateText && (
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                {dateText}
              </div>
            )}
          </div>
          
          {/* 操作按鈕 */}
          <div className="flex space-x-2">
            {onBookmark && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onBookmark(job)}
                icon={<Heart className={`h-4 w-4 ${isBookmarked ? 'text-red-500 fill-current' : ''}`} />}
              >
                收藏
              </Button>
            )}
            
            {job.job_url && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(job.job_url, '_blank')}
                icon={<ExternalLink className="h-4 w-4" />}
              >
                查看詳情
              </Button>
            )}
            
            {job.job_url_direct && onApply && (
              <Button
                variant="primary"
                size="sm"
                onClick={() => onApply(job)}
                icon={<Send className="h-4 w-4" />}
              >
                立即申請
              </Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};
