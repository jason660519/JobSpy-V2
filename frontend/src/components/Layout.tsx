import React, { useState, useEffect } from 'react';
import MobileNavigation from './MobileNavigation';
import { usePushNotifications } from '../hooks/usePushNotifications';
import { useLocation } from 'react-router-dom';

/**
 * 基礎佈局組件 - 使用 Bootstrap 5 樣式
 * 包含完整的三欄式佈局：header、左側邊欄、主內容區、右側邊欄和 footer
 * 支持移動端響應式設計
 */
interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [showLeftSidebar, setShowLeftSidebar] = useState(false);
  const [showRightSidebar, setShowRightSidebar] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const location = useLocation();
  const isHome = location.pathname === '/';
  
  // Push notification hook
  const { isSupported, permission, requestPermission, subscribeToPush } = usePushNotifications();

  // 檢測屏幕大小
  useEffect(() => {
    const checkScreenSize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      // 在桌面端自動隱藏側邊欄
      if (!mobile) {
        setShowLeftSidebar(false);
        setShowRightSidebar(false);
      }
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // 處理側邊欄切換
  const toggleLeftSidebar = () => {
    setShowLeftSidebar(!showLeftSidebar);
    if (showRightSidebar) setShowRightSidebar(false);
  };

  const toggleRightSidebar = () => {
    setShowRightSidebar(!showRightSidebar);
    if (showLeftSidebar) setShowLeftSidebar(false);
  };

  // 關閉側邊欄
  const closeSidebars = () => {
    setShowLeftSidebar(false);
    setShowRightSidebar(false);
  };

  // 處理 ESC 鍵關閉側邊欄
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        closeSidebars();
      }
    };

    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  // 請求通知權限
  const handleRequestNotifications = async () => {
    if (!isSupported) return;
    
    const permission = await requestPermission();
    if (permission === 'granted') {
      await subscribeToPush();
      // 這裡應該調用 API 來保存訂閱信息到服務器
      console.log('Push notifications enabled');
    }
  };

  return (
    <div className="min-vh-100">
      {/* 頂部導航欄 */}
      <nav className="navbar navbar-expand-lg navbar-dark fixed-top" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div className="container-fluid">
          <a className="navbar-brand" href="/">
            <i className="fas fa-briefcase me-2"></i>
            JobSpy
          </a>
          
          {/* 移動端菜單按鈕 */}
          {isMobile && (
            <div className="d-flex align-items-center">
              <button 
                className="btn btn-outline-light me-2 sidebar-toggle" 
                type="button"
                onClick={toggleLeftSidebar}
                title="切換左側邊欄"
                aria-label="切換左側邊欄"
              >
                <i className="fas fa-bars"></i>
              </button>
            </div>
          )}
          
          <button 
            className="navbar-toggler" 
            type="button" 
            data-bs-toggle="collapse" 
            data-bs-target="#topNavbar"
            aria-controls="topNavbar"
            aria-expanded="false"
            aria-label="切換導航"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className="collapse navbar-collapse" id="topNavbar">
            <ul className="navbar-nav ms-auto align-items-lg-center">
              <li className="nav-item dropdown">
                <a className="nav-link dropdown-toggle text-white" href="#" id="moreMenu" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                  <i className="fas fa-ellipsis-h me-1"></i> 更多
                </a>
                <ul className="dropdown-menu dropdown-menu-end" aria-labelledby="moreMenu">
                  <li><a className="dropdown-item" href="#"><i className="fas fa-book me-2"></i>Doc</a></li>
                  <li><a className="dropdown-item" href="#"><i className="fas fa-download me-2"></i>Downloads</a></li>
                  <li><a className="dropdown-item" href="#"><i className="fas fa-heart me-2"></i>Donate</a></li>
                  <li><a className="dropdown-item" href="#"><i className="fas fa-envelope me-2"></i>聯絡我們</a></li>
                </ul>
              </li>
              <li className="nav-item">
                <button 
                  className="btn btn-outline-light me-2 position-relative" 
                  title="通知"
                  onClick={() => {
                    if (permission === 'granted') {
                      setShowNotifications(!showNotifications);
                    } else {
                      handleRequestNotifications();
                    }
                  }}
                  aria-label="通知"
                >
                  <i className="fas fa-bell"></i>
                  {permission !== 'granted' && (
                    <span className="position-absolute top-0 start-100 translate-middle p-1 bg-danger border border-light rounded-circle">
                      <span className="visually-hidden">新的通知</span>
                    </span>
                  )}
                </button>
              </li>
              {!isHome && (
                <li className="nav-item">
                  <button 
                    className="btn btn-outline-light me-2" 
                    title="切換右側邊欄"
                    onClick={toggleRightSidebar}
                    aria-label="切換右側邊欄"
                  >
                    <i className="fas fa-columns"></i>
                  </button>
                </li>
              )}
            </ul>
          </div>
        </div>
      </nav>

      {/* 移動端遮罩層 */}
      {(showLeftSidebar || showRightSidebar) && (
        <div 
          className="position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50"
          style={{ zIndex: 1040, paddingTop: '76px' }}
          onClick={closeSidebars}
          aria-hidden="true"
        ></div>
      )}

      {/* 移動端導航 */}
      <MobileNavigation 
        isVisible={showLeftSidebar}
        onClose={() => setShowLeftSidebar(false)}
      />

      {/* 主要佈局容器 */}
      <div className="main-container" style={{ paddingTop: '76px' }}>
        <div className="row g-0">
          {/* 左側邊欄 */}
          <div className={`col-md-3 col-lg-2 ${isMobile && !showLeftSidebar ? 'd-none' : ''}`}>
            <div className={`sidebar ${showLeftSidebar ? 'show' : ''}`} style={{ height: 'calc(100vh - 76px)', overflowY: 'auto' }}>
              <div className="sidebar-content p-3">
                {/* 移動端關閉按鈕 */}
                {isMobile && (
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h6 className="mb-0">菜單</h6>
                    <button 
                      className="btn btn-sm btn-outline-secondary"
                      onClick={closeSidebars}
                      title="關閉側邊欄"
                      aria-label="關閉側邊欄"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                )}
                {/* 用戶資訊卡片 */}
                <div className="user-card mb-4">
                  <div className="d-flex align-items-center">
                    <div className="user-avatar me-3">
                      <i className="fas fa-user-circle fa-2x text-primary"></i>
                    </div>
                    <div className="user-info">
                      <h6 className="user-name mb-0">歡迎使用 JobSpy</h6>
                      <small className="user-status text-success">
                        <i className="fas fa-circle"></i> 系統正常
                      </small>
                    </div>
                  </div>
                </div>

                {/* 快速統計 */}
                <div className="stats-widget mb-4">
                  <h6 className="stats-title">
                    <i className="fas fa-chart-line me-2"></i>今日統計
                  </h6>
                  <div className="row">
                    <div className="col-6">
                      <div className="text-center">
                        <div className="h5 mb-0 text-primary">0</div>
                        <small className="text-muted">搜尋次數</small>
                      </div>
                    </div>
                    <div className="col-6">
                      <div className="text-center">
                        <div className="h5 mb-0 text-success">0</div>
                        <small className="text-muted">找到職位</small>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 主要功能 */}
                <div className="mb-4">
                  <h6 className="section-title">
                    <i className="fas fa-rocket me-2"></i>主要功能
                  </h6>
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <a href="/" className="d-flex align-items-center text-decoration-none">
                        <div className="nav-icon me-3">
                          <i className="fas fa-home"></i>
                        </div>
                        <div className="nav-content">
                          <span className="nav-text">首頁搜尋</span>
                          <br />
                          <small className="text-muted">智能職位搜尋</small>
                        </div>
                      </a>
                    </li>
                    <li className="mb-2">
                      <a href="/results" className="d-flex align-items-center text-decoration-none">
                        <div className="nav-icon me-3">
                          <i className="fas fa-chart-bar"></i>
                        </div>
                        <div className="nav-content">
                          <span className="nav-text">測試結果</span>
                          <br />
                          <small className="text-muted">查看搜尋結果</small>
                        </div>
                      </a>
                    </li>
                  </ul>
                </div>

                {/* 工具與資源 */}
                <div className="mb-4">
                  <h6 className="section-title">
                    <i className="fas fa-tools me-2"></i>工具與資源
                  </h6>
                  <ul className="list-unstyled">
                    <li className="mb-2">
                      <a href="#" className="d-flex align-items-center text-decoration-none">
                        <div className="nav-icon me-3">
                          <i className="fas fa-download"></i>
                        </div>
                        <div className="nav-content">
                          <span className="nav-text">下載範例CSV</span>
                          <br />
                          <small className="text-muted">資料格式範例</small>
                        </div>
                      </a>
                    </li>
                    <li className="mb-2">
                      <a href="https://github.com/jason660519/jobseeker" target="_blank" className="d-flex align-items-center text-decoration-none">
                        <div className="nav-icon me-3">
                          <i className="fab fa-github"></i>
                        </div>
                        <div className="nav-content">
                          <span className="nav-text">GitHub 專案</span>
                          <br />
                          <small className="text-muted">開源代碼</small>
                        </div>
                      </a>
                    </li>
                  </ul>
                </div>

                {/* 系統狀態 */}
                <div className="system-status">
                  <div className="d-flex align-items-center mb-2">
                    <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
                    <span className="small">所有平台正常</span>
                  </div>
                  <div className="d-flex align-items-center">
                    <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
                    <span className="small">AI 路由運行中</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 主內容區域 */}
          <div className={`col-md-6 ${isMobile ? 'col-12' : ''}`}>
            <main className="main-content">
              {children}
            </main>
          </div>

          {/* 右側邊欄（首頁隱藏） */}
          {!isHome && (
          <div className={`col-md-3 ${isMobile ? 'd-none' : ''}`}>
            <div className={`right-sidebar ${showRightSidebar ? 'show' : ''}`} style={{ height: 'calc(100vh - 76px)', overflowY: 'auto' }}>
              <div className="right-sidebar-content p-3">
                {/* 移動端關閉按鈕 */}
                {isMobile && (
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h6 className="mb-0">資訊面板</h6>
                    <button 
                      className="btn btn-sm btn-outline-secondary"
                      onClick={closeSidebars}
                      title="關閉側邊欄"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                )}
                {/* 搜尋歷史 */}
                <div className="search-history-widget mb-4">
                  <h6 className="stats-title">
                    <i className="fas fa-history me-2"></i>搜尋歷史
                  </h6>
                  <div className="history-item mb-2 p-2 border rounded">
                    <div className="d-flex align-items-center">
                      <i className="fas fa-search me-2 text-muted"></i>
                      <div>
                        <div className="small">軟體工程師 台北</div>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>2小時前</div>
                      </div>
                    </div>
                  </div>
                  <div className="history-item mb-2 p-2 border rounded">
                    <div className="d-flex align-items-center">
                      <i className="fas fa-search me-2 text-muted"></i>
                      <div>
                        <div className="small">前端開發 遠端</div>
                        <div className="text-muted" style={{ fontSize: '0.75rem' }}>1天前</div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* 熱門搜尋 */}
                <div className="trending-widget mb-4">
                  <h6 className="stats-title">
                    <i className="fas fa-fire me-2"></i>熱門搜尋
                  </h6>
                  <div className="trending-item mb-2 p-2 border rounded">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center">
                        <span className="badge bg-primary me-2">1</span>
                        <span className="small">軟體工程師</span>
                      </div>
                      <span className="text-muted small">1.2k</span>
                    </div>
                  </div>
                  <div className="trending-item mb-2 p-2 border rounded">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center">
                        <span className="badge bg-primary me-2">2</span>
                        <span className="small">前端開發</span>
                      </div>
                      <span className="text-muted small">856</span>
                    </div>
                  </div>
                  <div className="trending-item mb-2 p-2 border rounded">
                    <div className="d-flex justify-content-between align-items-center">
                      <div className="d-flex align-items-center">
                        <span className="badge bg-primary me-2">3</span>
                        <span className="small">產品經理</span>
                      </div>
                      <span className="text-muted small">743</span>
                    </div>
                  </div>
                </div>

                {/* 即時通知 */}
                <div className="notifications-widget">
                  <h6 className="stats-title">
                    <i className="fas fa-bell me-2"></i>即時通知
                  </h6>
                  <div className="alert alert-info alert-sm">
                    <i className="fas fa-info-circle me-2"></i>
                    <small>系統運行正常</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          )}
        </div>
      </div>

      {/* 頁腳 */}
      <footer className="bg-dark text-light py-4">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <h5>
                <i className="fas fa-briefcase me-2"></i>
                jobseeker
              </h5>
              <p className="mb-0">智能職位搜尋平台</p>
            </div>
            <div className="col-md-6 text-md-end">
              <p className="mb-0">
                <i className="fas fa-heart text-danger me-1"></i>
                Made with AI Technology
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};