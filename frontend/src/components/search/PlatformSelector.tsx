import React, { useState } from 'react';
import { 
  Linkedin, 
  Briefcase, 
  Building, 
  Search, 
  Compass, 
  Globe, 
  Check,
  X
} from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

export interface Platform {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  description: string;
}

const PLATFORMS: Platform[] = [
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: Linkedin,
    color: 'text-blue-600',
    description: '專業社交網路'
  },
  {
    id: 'indeed',
    name: 'Indeed',
    icon: Briefcase,
    color: 'text-indigo-600',
    description: '全球最大求職網站'
  },
  {
    id: 'glassdoor',
    name: 'Glassdoor',
    icon: Building,
    color: 'text-green-600',
    description: '公司評價與職位'
  },
  {
    id: 'ziprecruiter',
    name: 'ZipRecruiter',
    icon: Search,
    color: 'text-yellow-600',
    description: '快速職位配對'
  },
  {
    id: 'seek',
    name: 'Seek',
    icon: Compass,
    color: 'text-red-600',
    description: '澳洲主要求職網站'
  },
  {
    id: 'google',
    name: 'Google Jobs',
    icon: Globe,
    color: 'text-blue-500',
    description: 'Google 職位搜尋'
  },
  {
    id: '104',
    name: '104人力銀行',
    icon: Briefcase,
    color: 'text-orange-600',
    description: '台灣主要求職網站'
  },
  {
    id: '1111',
    name: '1111人力銀行',
    icon: Briefcase,
    color: 'text-purple-600',
    description: '台灣求職平台'
  }
];

export interface PlatformSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  selectedPlatforms: string[];
  onPlatformChange: (platforms: string[]) => void;
}

export const PlatformSelector: React.FC<PlatformSelectorProps> = ({
  isOpen,
  onClose,
  selectedPlatforms,
  onPlatformChange
}) => {
  const [tempSelection, setTempSelection] = useState<string[]>(selectedPlatforms);
  
  React.useEffect(() => {
    setTempSelection(selectedPlatforms);
  }, [selectedPlatforms, isOpen]);
  
  const handlePlatformToggle = (platformId: string) => {
    setTempSelection(prev => 
      prev.includes(platformId)
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };
  
  const handleSelectAll = () => {
    setTempSelection(PLATFORMS.map(p => p.id));
  };
  
  const handleClearAll = () => {
    setTempSelection([]);
  };
  
  const handleApply = () => {
    if (tempSelection.length === 0) {
      alert('請至少選擇一個搜尋網站！');
      return;
    }
    onPlatformChange(tempSelection);
    onClose();
  };
  
  const selectedCount = tempSelection.length;
  
  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="選擇搜尋網站"
      description="請選擇您要搜尋的求職網站："
      size="lg"
    >
      <div className="space-y-4">
        {/* 操作按鈕 */}
        <div className="flex justify-between">
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSelectAll}
              icon={<Check className="h-4 w-4" />}
            >
              全選
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearAll}
              icon={<X className="h-4 w-4" />}
            >
              清除全部
            </Button>
          </div>
          
          <div className="text-sm text-gray-600">
            已選擇 {selectedCount} 個平台
          </div>
        </div>
        
        {/* 平台列表 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {PLATFORMS.map((platform) => {
            const Icon = platform.icon;
            const isSelected = tempSelection.includes(platform.id);
            
            return (
              <Card
                key={platform.id}
                className={`cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'ring-2 ring-blue-500 bg-blue-50' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handlePlatformToggle(platform.id)}
                hover
              >
                <div className="flex items-center space-x-3 p-4">
                  <div className={`flex-shrink-0 ${platform.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900">
                      {platform.name}
                    </h3>
                    <p className="text-xs text-gray-500">
                      {platform.description}
                    </p>
                  </div>
                  
                  <div className="flex-shrink-0">
                    <div className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${
                      isSelected
                        ? 'bg-blue-600 border-blue-600'
                        : 'border-gray-300'
                    }`}>
                      {isSelected && (
                        <Check className="h-3 w-3 text-white" />
                      )}
                    </div>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
        
        {/* 確認按鈕 */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <Button
            variant="outline"
            onClick={onClose}
          >
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleApply}
            disabled={selectedCount === 0}
          >
            確認選擇 ({selectedCount})
          </Button>
        </div>
      </div>
    </Modal>
  );
};
