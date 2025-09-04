import React from 'react';
import { 
  Search, 
  Briefcase, 
  Globe, 
  Clock, 
  FileText,
  Code
} from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';

export interface SearchStats {
  totalJobs: number;
  successfulPlatforms: number;
  confidenceScore: number;
  executionTime: number;
  searchId?: string;
}

export interface ResultsStatsProps {
  stats: SearchStats;
  onDownloadCsv?: () => void;
  onDownloadJson?: () => void;
  isLoading?: boolean;
}

export const ResultsStats: React.FC<ResultsStatsProps> = ({
  stats,
  onDownloadCsv,
  onDownloadJson,
  isLoading = false
}) => {
  const formatTime = (seconds: number) => {
    if (seconds < 1) {
      return `${Math.round(seconds * 1000)}ms`;
    }
    return `${seconds.toFixed(1)}s`;
  };
  
  const formatConfidence = (score: number) => {
    return `${Math.round(score * 100)}%`;
  };
  
  return (
    <div className="space-y-6">
      {/* 統計卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Briefcase className="h-8 w-8 text-blue-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.totalJobs.toLocaleString()}
          </h3>
          <p className="text-sm text-gray-600">找到職位</p>
        </Card>
        
        <Card className="text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Globe className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {stats.successfulPlatforms}
          </h3>
          <p className="text-sm text-gray-600">成功平台</p>
        </Card>
        
        <Card className="text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Search className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {formatConfidence(stats.confidenceScore)}
          </h3>
          <p className="text-sm text-gray-600">信心指數</p>
        </Card>
        
        <Card className="text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Clock className="h-8 w-8 text-orange-600" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">
            {formatTime(stats.executionTime)}
          </h3>
          <p className="text-sm text-gray-600">搜尋時間</p>
        </Card>
      </div>
      
      {/* 下載按鈕 */}
      {(onDownloadCsv || onDownloadJson) && (
        <Card className="p-4">
          <div className="flex flex-col sm:flex-row items-center justify-between space-y-3 sm:space-y-0">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">
                下載搜尋結果
              </h3>
              <p className="text-sm text-gray-600">
                將搜尋結果匯出為 CSV 或 JSON 格式
              </p>
            </div>
            
            <div className="flex space-x-3">
              {onDownloadCsv && (
                <Button
                  variant="outline"
                  onClick={onDownloadCsv}
                  disabled={isLoading}
                  icon={<FileText className="h-4 w-4" />}
                >
                  下載 CSV
                </Button>
              )}
              
              {onDownloadJson && (
                <Button
                  variant="outline"
                  onClick={onDownloadJson}
                  disabled={isLoading}
                  icon={<Code className="h-4 w-4" />}
                >
                  下載 JSON
                </Button>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
