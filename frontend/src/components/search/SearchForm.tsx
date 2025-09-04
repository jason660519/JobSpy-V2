import React, { useState } from 'react';
import { Search, MapPin, Settings } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/Card';
import { PlatformSelector } from './PlatformSelector';

export interface SearchQuery {
  jobTitle: string;
  location: string;
  selectedPlatforms: string[];
  useAI: boolean;
}

export interface SearchFormProps {
  onSearch: (query: SearchQuery) => void;
  isLoading: boolean;
  initialQuery?: Partial<SearchQuery>;
}

export const SearchForm: React.FC<SearchFormProps> = ({
  onSearch,
  isLoading,
  initialQuery = {}
}) => {
  const [query, setQuery] = useState<SearchQuery>({
    jobTitle: initialQuery.jobTitle || '',
    location: initialQuery.location || '',
    selectedPlatforms: initialQuery.selectedPlatforms || ['linkedin', 'indeed', 'glassdoor'],
    useAI: initialQuery.useAI ?? true
  });
  
  const [showPlatformSelector, setShowPlatformSelector] = useState(false);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.jobTitle.trim() && !query.location.trim()) {
      return;
    }
    
    onSearch(query);
  };
  
  const handlePlatformChange = (platforms: string[]) => {
    setQuery(prev => ({ ...prev, selectedPlatforms: platforms }));
  };
  
  const selectedPlatformsCount = query.selectedPlatforms.length;
  const platformButtonText = selectedPlatformsCount === 0 
    ? '全部' 
    : selectedPlatformsCount === 1 
    ? query.selectedPlatforms[0] 
    : `${selectedPlatformsCount}個`;
  
  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center text-2xl">
          <Search className="mr-3 h-6 w-6 text-blue-600" />
          智能職位搜尋
        </CardTitle>
        <CardDescription>
          告訴我們您想要什麼工作，AI 會為您找到最適合的機會
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 主要搜尋區域 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="職位名稱"
              placeholder="例如：軟體工程師、產品經理"
              value={query.jobTitle}
              onChange={(e) => setQuery(prev => ({ ...prev, jobTitle: e.target.value }))}
              icon={<Search className="h-5 w-5" />}
              iconPosition="left"
            />
            
            <Input
              label="工作地點"
              placeholder="例如：台北、新加坡、遠端"
              value={query.location}
              onChange={(e) => setQuery(prev => ({ ...prev, location: e.target.value }))}
              icon={<MapPin className="h-5 w-5" />}
              iconPosition="left"
            />
          </div>
          
          {/* 平台選擇區域 */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              搜尋平台
            </label>
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowPlatformSelector(true)}
              className="w-full justify-between"
              icon={<Settings className="h-4 w-4" />}
            >
              選擇平台
              <span className="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
                {platformButtonText}
              </span>
            </Button>
          </div>
          
          {/* AI 選項 */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="useAI"
              checked={query.useAI}
              onChange={(e) => setQuery(prev => ({ ...prev, useAI: e.target.checked }))}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="useAI" className="text-sm text-gray-700">
              使用 AI 智能分析提升搜尋準確度
            </label>
          </div>
          
          {/* 搜尋按鈕 */}
          <div className="text-center">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              disabled={!query.jobTitle.trim() && !query.location.trim()}
              className="px-8 py-3"
              icon={<Search className="h-5 w-5" />}
            >
              {isLoading ? '正在搜尋...' : '開始搜尋職位'}
            </Button>
            
            <p className="mt-2 text-xs text-gray-500">
              <span className="inline-flex items-center">
                <svg className="mr-1 h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                </svg>
                搜尋過程安全且隱私保護
              </span>
            </p>
          </div>
        </form>
      </CardContent>
      
      {/* 平台選擇器模態框 */}
      <PlatformSelector
        isOpen={showPlatformSelector}
        onClose={() => setShowPlatformSelector(false)}
        selectedPlatforms={query.selectedPlatforms}
        onPlatformChange={handlePlatformChange}
      />
    </Card>
  );
};
