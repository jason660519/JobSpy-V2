import React from 'react';
import { Search, Globe, Briefcase, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '../ui/Card';
import { ProgressBar } from '../ui/ProgressBar';

export interface SearchProgressProps {
  isVisible: boolean;
  progress: number;
  currentStep: number;
  message?: string;
}

const SEARCH_STEPS = [
  {
    id: 'analyze',
    label: '分析查詢',
    icon: Search,
    description: '正在分析您的搜尋需求...'
  },
  {
    id: 'select',
    label: '選擇平台',
    icon: Globe,
    description: '正在選擇最佳搜尋平台...'
  },
  {
    id: 'search',
    label: '搜尋職位',
    icon: Briefcase,
    description: '正在搜尋相關職位...'
  },
  {
    id: 'process',
    label: '整理結果',
    icon: CheckCircle,
    description: '正在整理和排序結果...'
  }
];

export const SearchProgress: React.FC<SearchProgressProps> = ({
  isVisible,
  progress,
  currentStep,
  message
}) => {
  if (!isVisible) return null;
  
  const steps = SEARCH_STEPS.map((step, index) => ({
    id: step.id,
    label: step.label,
    completed: index < currentStep,
    active: index === currentStep
  }));
  
  const currentStepData = SEARCH_STEPS[currentStep];
  const CurrentIcon = currentStepData?.icon || Search;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <Card className="w-full max-w-md mx-4">
        <CardContent className="p-8">
          {/* 載入動畫 */}
          <div className="text-center mb-6">
            <div className="relative inline-block">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <CurrentIcon className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </div>
          
          {/* 進度條 */}
          <div className="mb-6">
            <ProgressBar
              progress={progress}
              steps={steps}
              showSteps={true}
            />
          </div>
          
          {/* 當前步驟信息 */}
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              正在搜尋職位...
            </h3>
            <p className="text-sm text-gray-600 mb-1">
              {currentStepData?.description || '正在處理您的請求...'}
            </p>
            {message && (
              <p className="text-xs text-gray-500">
                {message}
              </p>
            )}
          </div>
          
          {/* 進度百分比 */}
          <div className="mt-4 text-center">
            <span className="text-2xl font-bold text-blue-600">
              {Math.round(progress)}%
            </span>
            <p className="text-sm text-gray-500">完成進度</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
