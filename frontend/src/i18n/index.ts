import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  'zh-TW': {
    translation: {
      // 通用
      common: {
        search: '搜尋',
        cancel: '取消',
        confirm: '確認',
        loading: '載入中...',
        error: '錯誤',
        success: '成功',
        warning: '警告',
        info: '資訊',
        notifications: '通知',
        enableNotifications: '啟用通知',
        notificationPermission: '需要您的許可才能發送通知',
        allow: '允許',
        deny: '拒絕'
      },
      
      // 搜尋表單
      search: {
        title: '智能職位搜尋',
        description: '告訴我們您想要什麼工作，AI 會為您找到最適合的機會',
        jobTitle: '職位名稱',
        jobTitlePlaceholder: '例如：軟體工程師、產品經理',
        location: '工作地點',
        locationPlaceholder: '例如：台北、新加坡、遠端',
        platforms: '搜尋平台',
        selectPlatforms: '選擇平台',
        useAI: '使用 AI 智能分析提升搜尋準確度',
        searchButton: '開始搜尋職位',
        searching: '正在搜尋...',
        privacy: '搜尋過程安全且隱私保護'
      },
      
      // 平台選擇器
      platforms: {
        title: '選擇搜尋網站',
        description: '請選擇您要搜尋的求職網站：',
        selectAll: '全選',
        clearAll: '清除全部',
        selected: '已選擇',
        platforms: '個平台',
        confirm: '確認選擇',
        linkedin: 'LinkedIn',
        indeed: 'Indeed',
        glassdoor: 'Glassdoor',
        ziprecruiter: 'ZipRecruiter',
        seek: 'Seek',
        google: 'Google Jobs',
        '104': '104人力銀行',
        '1111': '1111人力銀行'
      },
      
      // 搜尋進度
      progress: {
        title: '正在搜尋職位...',
        analyze: '分析查詢',
        analyzeDesc: '正在分析您的搜尋需求...',
        select: '選擇平台',
        selectDesc: '正在選擇最佳搜尋平台...',
        search: '搜尋職位',
        searchDesc: '正在搜尋相關職位...',
        process: '整理結果',
        processDesc: '正在整理和排序結果...',
        completed: '完成進度'
      },
      
      // 結果統計
      stats: {
        totalJobs: '找到職位',
        successfulPlatforms: '成功平台',
        confidenceScore: '信心指數',
        executionTime: '搜尋時間',
        downloadTitle: '下載搜尋結果',
        downloadDescription: '將搜尋結果匯出為 CSV 或 JSON 格式',
        downloadCsv: '下載 CSV',
        downloadJson: '下載 JSON'
      },
      
      // 職位卡片
      job: {
        bookmark: '收藏',
        viewDetails: '查看詳情',
        applyNow: '立即申請',
        remote: '遠端工作',
        daysAgo: '天前',
        dayAgo: '天前'
      },
      
      // 職位列表
      jobList: {
        loading: '正在載入職位...',
        noResults: '未找到符合條件的職位',
        noResultsDesc: '請嘗試調整搜尋條件或關鍵字',
        loadMore: '載入更多職位',
        loadingMore: '載入更多職位中...'
      }
    }
  },
  'en': {
    translation: {
      // 通用
      common: {
        search: 'Search',
        cancel: 'Cancel',
        confirm: 'Confirm',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        warning: 'Warning',
        info: 'Info',
        notifications: 'Notifications',
        enableNotifications: 'Enable Notifications',
        notificationPermission: 'We need your permission to send notifications',
        allow: 'Allow',
        deny: 'Deny'
      },
      
      // 搜尋表單
      search: {
        title: 'AI-Powered Job Search',
        description: 'Tell us what job you want, and AI will find the best opportunities for you',
        jobTitle: 'Job Title',
        jobTitlePlaceholder: 'e.g., Software Engineer, Product Manager',
        location: 'Location',
        locationPlaceholder: 'e.g., Taipei, Singapore, Remote',
        platforms: 'Search Platforms',
        selectPlatforms: 'Select Platforms',
        useAI: 'Use AI intelligent analysis to improve search accuracy',
        searchButton: 'Start Job Search',
        searching: 'Searching...',
        privacy: 'Search process is secure and privacy-protected'
      },
      
      // 平台選擇器
      platforms: {
        title: 'Select Search Platforms',
        description: 'Please select the job search platforms you want to use:',
        selectAll: 'Select All',
        clearAll: 'Clear All',
        selected: 'Selected',
        platforms: 'platforms',
        confirm: 'Confirm Selection',
        linkedin: 'LinkedIn',
        indeed: 'Indeed',
        glassdoor: 'Glassdoor',
        ziprecruiter: 'ZipRecruiter',
        seek: 'Seek',
        google: 'Google Jobs',
        '104': '104 Job Bank',
        '1111': '1111 Job Bank'
      },
      
      // 搜尋進度
      progress: {
        title: 'Searching for jobs...',
        analyze: 'Analyze Query',
        analyzeDesc: 'Analyzing your search requirements...',
        select: 'Select Platforms',
        selectDesc: 'Selecting the best search platforms...',
        search: 'Search Jobs',
        searchDesc: 'Searching for relevant positions...',
        process: 'Process Results',
        processDesc: 'Organizing and sorting results...',
        completed: 'Progress'
      },
      
      // 結果統計
      stats: {
        totalJobs: 'Jobs Found',
        successfulPlatforms: 'Successful Platforms',
        confidenceScore: 'Confidence Score',
        executionTime: 'Search Time',
        downloadTitle: 'Download Search Results',
        downloadDescription: 'Export search results as CSV or JSON format',
        downloadCsv: 'Download CSV',
        downloadJson: 'Download JSON'
      },
      
      // 職位卡片
      job: {
        bookmark: 'Bookmark',
        viewDetails: 'View Details',
        applyNow: 'Apply Now',
        remote: 'Remote Work',
        daysAgo: 'days ago',
        dayAgo: 'day ago'
      },
      
      // 職位列表
      jobList: {
        loading: 'Loading jobs...',
        noResults: 'No jobs found matching your criteria',
        noResultsDesc: 'Please try adjusting your search criteria or keywords',
        loadMore: 'Load More Jobs',
        loadingMore: 'Loading more jobs...'
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'zh-TW', // 預設語言
    fallbackLng: 'zh-TW',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;