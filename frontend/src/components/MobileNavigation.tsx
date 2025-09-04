/**
 * 移動端導航組件
 * 提供移動端專用的導航功能和用戶體驗
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../styles/mobile-navigation.css';

interface MobileNavigationProps {
  isVisible: boolean;
  onClose: () => void;
}

/**
 * 移動端導航組件
 */
export const MobileNavigation: React.FC<MobileNavigationProps> = ({ 
  isVisible, 
  onClose 
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');

  // 導航項目
  const navigationItems = [
    {
      icon: 'fas fa-home',
      label: '首頁',
      path: '/',
      description: '返回首頁搜索'
    },
    {
      icon: 'fas fa-search',
      label: '職位搜索',
      path: '/search',
      description: '智能職位搜索'
    },
    {
      icon: 'fas fa-list',
      label: '搜索結果',
      path: '/results',
      description: '查看搜索結果'
    },
    {
      icon: 'fas fa-user',
      label: '個人資料',
      path: '/profile',
      description: '管理個人資料'
    },
    {
      icon: 'fas fa-sign-in-alt',
      label: '登入',
      path: '/login',
      description: '用戶登入'
    },
    {
      icon: 'fas fa-user-plus',
      label: '註冊',
      path: '/register',
      description: '新用戶註冊'
    }
  ];

  // 快速操作
  const quickActions = [
    {
      icon: 'fas fa-download',
      label: '下載 CSV',
      action: () => {
        // 下載 CSV 邏輯
        console.log('下載 CSV');
      }
    },
    {
      icon: 'fab fa-github',
      label: 'GitHub',
      action: () => {
        window.open('https://github.com/jason660519/jobseeker', '_blank');
      }
    },
    {
      icon: 'fas fa-heart',
      label: '贊助',
      action: () => {
        // 贊助邏輯
        console.log('贊助');
      }
    }
  ];

  /**
   * 處理導航點擊
   */
  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  /**
   * 處理搜索提交
   */
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate('/search', { state: { keywords: searchQuery } });
      onClose();
    }
  };

  /**
   * 檢查是否為當前頁面
   */
  const isCurrentPage = (path: string) => {
    return location.pathname === path;
  };

  if (!isVisible) return null;

  return (
    <div className="mobile-navigation">
      {/* 導航頭部 */}
      <div className="mobile-nav-header">
        <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
          <div className="d-flex align-items-center">
            <i className="fas fa-briefcase text-primary me-2"></i>
            <h5 className="mb-0 fw-bold">JobSpy v2</h5>
          </div>
          <button 
            className="btn btn-sm btn-outline-secondary"
            onClick={onClose}
            title="關閉導航"
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      </div>

      {/* 快速搜索 */}
      <div className="mobile-nav-search p-3 bg-light">
        <form onSubmit={handleSearch}>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="快速搜索職位..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="btn btn-primary" type="submit">
              <i className="fas fa-search"></i>
            </button>
          </div>
        </form>
      </div>

      {/* 主要導航 */}
      <div className="mobile-nav-main">
        <div className="p-3">
          <h6 className="text-muted mb-3">
            <i className="fas fa-compass me-2"></i>
            主要功能
          </h6>
          <div className="list-group list-group-flush">
            {navigationItems.map((item, index) => (
              <button
                key={index}
                className={`list-group-item list-group-item-action border-0 rounded mb-2 ${
                  isCurrentPage(item.path) ? 'active' : ''
                }`}
                onClick={() => handleNavigation(item.path)}
              >
                <div className="d-flex align-items-center">
                  <div className="nav-icon me-3">
                    <i className={`${item.icon} ${isCurrentPage(item.path) ? 'text-white' : 'text-primary'}`}></i>
                  </div>
                  <div className="nav-content flex-grow-1">
                    <div className={`nav-title fw-semibold ${
                      isCurrentPage(item.path) ? 'text-white' : 'text-dark'
                    }`}>
                      {item.label}
                    </div>
                    <div className={`nav-description small ${
                      isCurrentPage(item.path) ? 'text-white-50' : 'text-muted'
                    }`}>
                      {item.description}
                    </div>
                  </div>
                  {isCurrentPage(item.path) && (
                    <i className="fas fa-check text-white"></i>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 快速操作 */}
      <div className="mobile-nav-actions">
        <div className="p-3 border-top">
          <h6 className="text-muted mb-3">
            <i className="fas fa-bolt me-2"></i>
            快速操作
          </h6>
          <div className="row g-2">
            {quickActions.map((action, index) => (
              <div key={index} className="col-4">
                <button
                  className="btn btn-outline-primary w-100 d-flex flex-column align-items-center py-3"
                  onClick={action.action}
                >
                  <i className={`${action.icon} mb-2`}></i>
                  <span className="small">{action.label}</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 系統狀態 */}
      <div className="mobile-nav-status">
        <div className="p-3 bg-light border-top">
          <div className="d-flex align-items-center justify-content-between">
            <div className="d-flex align-items-center">
              <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
              <span className="small text-muted">系統運行正常</span>
            </div>
            <span className="badge bg-success">在線</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileNavigation;