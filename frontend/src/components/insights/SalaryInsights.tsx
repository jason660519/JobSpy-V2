import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  DollarSign, 
  MapPin, 
  Briefcase, 
  Calendar,
  Filter,
  BarChart3,
  PieChart
} from 'lucide-react';
import { useJobStore } from '../../stores/jobStore';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';

interface SalaryInsightsProps {
  jobId?: string;
}

export const SalaryInsights: React.FC<SalaryInsightsProps> = ({ jobId }) => {
  const { jobs } = useJobStore();
  const [timeRange, setTimeRange] = useState('30d');
  const [locationFilter, setLocationFilter] = useState('');
  const [jobTypeFilter, setJobTypeFilter] = useState('');

  // Filter jobs based on criteria
  const filteredJobs = jobs.filter(job => {
    // If specific job ID is provided, only show that job
    if (jobId && job.id !== jobId) return false;
    
    // Location filter
    if (locationFilter && !job.location.includes(locationFilter)) return false;
    
    // Job type filter
    if (jobTypeFilter && job.type !== jobTypeFilter) return false;
    
    return true;
  });

  // Calculate salary statistics
  const salaryStats = {
    min: Math.min(...filteredJobs.map(job => job.salaryMin || 0).filter(s => s > 0)),
    max: Math.max(...filteredJobs.map(job => job.salaryMax || 0).filter(s => s > 0)),
    avg: filteredJobs.length > 0 
      ? filteredJobs.reduce((sum, job) => sum + ((job.salaryMin || 0) + (job.salaryMax || 0)) / 2, 0) / filteredJobs.length
      : 0,
    count: filteredJobs.length
  };

  // Group jobs by location
  const jobsByLocation = filteredJobs.reduce((acc, job) => {
    const location = job.location || '未指定';
    acc[location] = (acc[location] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Group jobs by type
  const jobsByType = filteredJobs.reduce((acc, job) => {
    const type = job.type || '未指定';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Format currency
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-TW', {
      style: 'currency',
      currency: 'TWD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <div className="salary-insights">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="fw-bold mb-0">
          <TrendingUp size={20} className="me-2" />
          薪資洞察
        </h5>
        
        {/* Filters */}
        <div className="d-flex gap-2">
          <select 
            className="form-select form-select-sm"
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
            <option value="90d">最近90天</option>
            <option value="all">全部</option>
          </select>
          
          <input
            type="text"
            className="form-control form-control-sm"
            placeholder="地點篩選"
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
          />
          
          <select 
            className="form-select form-select-sm"
            value={jobTypeFilter}
            onChange={(e) => setJobTypeFilter(e.target.value)}
          >
            <option value="">所有類型</option>
            <option value="全職">全職</option>
            <option value="兼職">兼職</option>
            <option value="合約">合約</option>
            <option value="實習">實習</option>
          </select>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="h6 text-muted">
                <DollarSign size={16} className="me-1" />
                平均薪資
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h4 fw-bold text-success">
                {formatCurrency(salaryStats.avg)}
              </div>
              <small className="text-muted">基於 {salaryStats.count} 個職位</small>
            </CardContent>
          </Card>
        </div>
        
        <div className="col-md-3 mb-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="h6 text-muted">
                <BarChart3 size={16} className="me-1" />
                最低薪資
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h4 fw-bold text-primary">
                {salaryStats.min > 0 ? formatCurrency(salaryStats.min) : 'N/A'}
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="col-md-3 mb-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="h6 text-muted">
                <TrendingUp size={16} className="me-1" />
                最高薪資
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h4 fw-bold text-warning">
                {salaryStats.max > 0 ? formatCurrency(salaryStats.max) : 'N/A'}
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="col-md-3 mb-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="h6 text-muted">
                <Briefcase size={16} className="me-1" />
                職位數量
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h4 fw-bold text-info">
                {salaryStats.count}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Charts */}
      <div className="row">
        {/* Salary Distribution */}
        <div className="col-md-6 mb-4">
          <Card>
            <CardHeader>
              <CardTitle className="h6">
                <BarChart3 size={18} className="me-2" />
                薪資分佈
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="chart-placeholder bg-light rounded p-4 text-center">
                <BarChart3 size={48} className="text-muted mb-2" />
                <p className="text-muted mb-0">薪資分佈圖表</p>
                <small className="text-muted">（圖表功能將在完整實現中提供）</small>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Location Distribution */}
        <div className="col-md-6 mb-4">
          <Card>
            <CardHeader>
              <CardTitle className="h6">
                <MapPin size={18} className="me-2" />
                地區分佈
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="chart-placeholder bg-light rounded p-4 text-center">
                <PieChart size={48} className="text-muted mb-2" />
                <p className="text-muted mb-0">地區分佈圖表</p>
                <small className="text-muted">（圖表功能將在完整實現中提供）</small>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle className="h6">
            <Calendar size={18} className="me-2" />
            詳細數據
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>職位</th>
                  <th>公司</th>
                  <th>地點</th>
                  <th>類型</th>
                  <th>薪資範圍</th>
                  <th>發布日期</th>
                </tr>
              </thead>
              <tbody>
                {filteredJobs.map(job => (
                  <tr key={job.id}>
                    <td>{job.title}</td>
                    <td>{job.company}</td>
                    <td>{job.location}</td>
                    <td>
                      <span className="badge bg-primary">{job.type}</span>
                    </td>
                    <td className="text-success fw-bold">
                      {formatCurrency(job.salaryMin || 0)} - {formatCurrency(job.salaryMax || 0)}
                    </td>
                    <td>{new Date(job.postedDate).toLocaleDateString('zh-TW')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {filteredJobs.length === 0 && (
            <div className="text-center py-4">
              <p className="text-muted mb-0">沒有找到符合條件的職位數據</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};