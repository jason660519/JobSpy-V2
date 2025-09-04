import React, { useState, useEffect } from 'react';
import { 
  Star, 
  TrendingUp, 
  Heart, 
  Bookmark,
  Clock,
  Zap
} from 'lucide-react';
import { useJobStore } from '../../stores/jobStore';
import { useUserStore } from '../../stores/userStore';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';

interface JobRecommendationsProps {
  limit?: number;
  title?: string;
}

export const JobRecommendations: React.FC<JobRecommendationsProps> = ({ 
  limit = 5,
  title = '為您推薦'
}) => {
  const { jobs, fetchJobs } = useJobStore();
  const { userProfile } = useUserStore();
  const [recommendedJobs, setRecommendedJobs] = useState<any[]>([]);

  // Generate recommendations based on user profile
  useEffect(() => {
    if (jobs.length > 0 && userProfile) {
      // Simple recommendation algorithm based on user preferences
      const recommendations = jobs
        .filter(job => {
          // Filter by desired position
          if (userProfile.jobPreferences?.desiredPosition) {
            const desired = userProfile.jobPreferences.desiredPosition.toLowerCase();
            return job.title.toLowerCase().includes(desired) || 
                   job.description.toLowerCase().includes(desired);
          }
          return true;
        })
        .filter(job => {
          // Filter by work location
          if (userProfile.jobPreferences?.workLocation) {
            return job.location.includes(userProfile.jobPreferences.workLocation);
          }
          return true;
        })
        .filter(job => {
          // Filter by job type
          if (userProfile.jobPreferences?.jobType) {
            return job.type === userProfile.jobPreferences.jobType;
          }
          return true;
        })
        .sort((a, b) => {
          // Sort by rating and views (simple scoring)
          const scoreA = (a.rating || 0) * 10 + (a.views || 0);
          const scoreB = (b.rating || 0) * 10 + (b.views || 0);
          return scoreB - scoreA;
        })
        .slice(0, limit);
      
      setRecommendedJobs(recommendations);
    } else if (jobs.length > 0) {
      // If no user profile, show popular jobs
      const popularJobs = [...jobs]
        .sort((a, b) => {
          const scoreA = (a.views || 0) + (a.applications || 0);
          const scoreB = (b.views || 0) + (b.applications || 0);
          return scoreB - scoreA;
        })
        .slice(0, limit);
      
      setRecommendedJobs(popularJobs);
    }
  }, [jobs, userProfile, limit]);

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return '1 天前';
    } else if (diffDays < 7) {
      return `${diffDays} 天前`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} 週前`;
    } else {
      return date.toLocaleDateString('zh-TW');
    }
  };

  return (
    <div className="job-recommendations">
      <Card>
        <CardHeader>
          <CardTitle className="d-flex align-items-center">
            <Star size={20} className="me-2 text-warning" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recommendedJobs.length > 0 ? (
            <div className="recommendations-list">
              {recommendedJobs.map(job => (
                <div key={job.id} className="recommendation-item border-bottom py-3">
                  <div className="d-flex">
                    <img
                      src={job.companyLogo || `https://ui-avatars.com/api/?name=${job.company}&background=0D8ABC&color=fff`}
                      alt={job.company}
                      className="rounded me-3"
                      style={{ width: '40px', height: '40px', objectFit: 'cover' }}
                    />
                    <div className="flex-grow-1">
                      <h6 className="mb-1">
                        <a href={`/jobs/${job.id}`} className="text-decoration-none text-dark">
                          {job.title}
                        </a>
                      </h6>
                      <p className="text-muted small mb-1">{job.company} • {job.location}</p>
                      <div className="d-flex justify-content-between align-items-center">
                        <div className="d-flex align-items-center">
                          {job.salaryMin && (
                            <span className="text-success fw-bold small me-2">
                              NT$ {new Intl.NumberFormat('zh-TW').format(job.salaryMin)}+
                            </span>
                          )}
                          <span className="text-muted small">
                            {formatDate(job.postedDate)}
                          </span>
                        </div>
                        <div className="d-flex gap-1">
                          <Button variant="outline-secondary" size="sm" icon={<Heart size={14} />}>
                            <span className="visually-hidden">收藏</span>
                          </Button>
                          <Button variant="outline-secondary" size="sm" icon={<Bookmark size={14} />}>
                            <span className="visually-hidden">書籤</span>
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <Zap size={48} className="text-muted mb-3" />
              <p className="text-muted mb-0">暫無推薦職位</p>
              <small className="text-muted">完善您的個人資料以獲得更好的推薦</small>
            </div>
          )}
          
          {recommendedJobs.length > 0 && (
            <div className="text-center mt-3">
              <Button variant="outline-primary" size="sm">
                查看更多推薦
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};