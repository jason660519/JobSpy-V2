import React, { useState } from 'react';
import { X, Briefcase, MapPin, DollarSign, Calendar, Users, Star } from 'lucide-react';
import { useJobStore } from '../../stores/jobStore';
import { Button } from '../ui/Button';

interface JobComparisonProps {
  jobIds: string[];
  onRemoveJob: (jobId: string) => void;
  onClose: () => void;
}

export const JobComparison: React.FC<JobComparisonProps> = ({ 
  jobIds, 
  onRemoveJob,
  onClose 
}) => {
  const { jobs } = useJobStore();
  const [selectedJobs, setSelectedJobs] = useState(jobIds);

  // Get job details for selected jobs
  const jobDetails = jobs.filter(job => selectedJobs.includes(job.id));

  // Format salary
  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return '面議';
    
    const formatNumber = (num: number) => {
      return new Intl.NumberFormat('zh-TW').format(num);
    };
    
    if (min && max) {
      return `NT$ ${formatNumber(min)} - ${formatNumber(max)}`;
    } else if (min) {
      return `NT$ ${formatNumber(min)}+`;
    } else if (max) {
      return `最高 NT$ ${formatNumber(max)}`;
    }
    
    return '面議';
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-TW');
  };

  return (
    <div className="job-comparison">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">職位比較</h4>
        <button 
          className="btn btn-close" 
          onClick={onClose}
          aria-label="關閉比較"
        ></button>
      </div>

      {/* Comparison Table */}
      <div className="table-responsive">
        <table className="table table-bordered">
          <thead>
            <tr>
              <th style={{ width: '200px' }}>特徵</th>
              {jobDetails.map(job => (
                <th key={job.id} className="text-center">
                  <div className="d-flex flex-column align-items-center">
                    <button 
                      className="btn btn-sm btn-outline-danger mb-2"
                      onClick={() => onRemoveJob(job.id)}
                      aria-label={`移除 ${job.title}`}
                    >
                      <X size={16} />
                    </button>
                    <div className="fw-bold text-truncate" style={{ maxWidth: '150px' }}>
                      {job.title}
                    </div>
                    <small className="text-muted">{job.company}</small>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* Title */}
            <tr>
              <td className="fw-bold">職位名稱</td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">{job.title}</td>
              ))}
            </tr>

            {/* Company */}
            <tr>
              <td className="fw-bold">公司</td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">{job.company}</td>
              ))}
            </tr>

            {/* Location */}
            <tr>
              <td className="fw-bold">
                <MapPin size={16} className="me-1" />
                地點
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">{job.location}</td>
              ))}
            </tr>

            {/* Salary */}
            <tr>
              <td className="fw-bold">
                <DollarSign size={16} className="me-1" />
                薪資
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  <span className="text-success fw-bold">
                    {formatSalary(job.salaryMin, job.salaryMax)}
                  </span>
                </td>
              ))}
            </tr>

            {/* Job Type */}
            <tr>
              <td className="fw-bold">
                <Briefcase size={16} className="me-1" />
                類型
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  <span className="badge bg-primary">
                    {job.type}
                  </span>
                </td>
              ))}
            </tr>

            {/* Posted Date */}
            <tr>
              <td className="fw-bold">
                <Calendar size={16} className="me-1" />
                發布日期
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  {formatDate(job.postedDate)}
                </td>
              ))}
            </tr>

            {/* Experience */}
            <tr>
              <td className="fw-bold">
                <Users size={16} className="me-1" />
                經驗要求
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  {job.experience || '不限'}
                </td>
              ))}
            </tr>

            {/* Rating */}
            <tr>
              <td className="fw-bold">
                <Star size={16} className="me-1" />
                評分
              </td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  <div className="d-flex align-items-center justify-content-center">
                    <Star size={16} className="text-warning me-1" fill="currentColor" />
                    <span>{job.rating || 'N/A'}</span>
                  </div>
                </td>
              ))}
            </tr>

            {/* Tags */}
            <tr>
              <td className="fw-bold">技能標籤</td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  <div className="d-flex flex-wrap justify-content-center gap-1">
                    {job.tags?.slice(0, 3).map((tag, index) => (
                      <span key={index} className="badge bg-light text-dark">
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
              ))}
            </tr>

            {/* Apply Button */}
            <tr>
              <td className="fw-bold">操作</td>
              {jobDetails.map(job => (
                <td key={job.id} className="text-center">
                  <Button variant="primary" size="sm">
                    申請職位
                  </Button>
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* No jobs selected */}
      {jobDetails.length === 0 && (
        <div className="text-center py-5">
          <Briefcase size={48} className="text-muted mb-3" />
          <p className="text-muted">請選擇要比較的職位</p>
        </div>
      )}
    </div>
  );
};