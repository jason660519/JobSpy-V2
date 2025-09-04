#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瀏覽器調試腳本 - 使用Playwright自動化檢測前端錯誤
功能：
1. 自動打開瀏覽器訪問localhost:3000
2. 捕獲控制台錯誤信息
3. 監控網絡請求失敗
4. 檢測JavaScript運行時錯誤
5. 生成詳細的調試報告
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import List, Dict, Any

class BrowserDebugger:
    """瀏覽器調試器類"""
    
    def __init__(self):
        """初始化調試器"""
        self.console_logs = []
        self.network_errors = []
        self.js_errors = []
        self.page_errors = []
        self.performance_metrics = {}
        
    async def setup_page_listeners(self, page):
        """設置頁面監聽器來捕獲各種錯誤和事件"""
        
        # 監聽控制台消息
        async def handle_console(msg):
            """處理控制台消息"""
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': msg.type,
                'text': msg.text,
                'location': msg.location if hasattr(msg, 'location') else None
            }
            self.console_logs.append(log_entry)
            
            # 如果是錯誤類型，也添加到錯誤列表
            if msg.type in ['error', 'warning']:
                self.js_errors.append(log_entry)
                
        page.on('console', handle_console)
        
        # 監聽頁面錯誤
        async def handle_page_error(error):
            """處理頁面錯誤"""
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'message': str(error),
                'type': 'page_error'
            }
            self.page_errors.append(error_entry)
            
        page.on('pageerror', handle_page_error)
        
        # 監聽網絡請求
        async def handle_request_failed(request):
            """處理失敗的網絡請求"""
            error_entry = {
                'timestamp': datetime.now().isoformat(),
                'url': request.url,
                'method': request.method,
                'failure': request.failure,
                'type': 'network_error'
            }
            self.network_errors.append(error_entry)
            
        page.on('requestfailed', handle_request_failed)
        
        # 監聽響應錯誤
        async def handle_response(response):
            """處理HTTP響應，記錄錯誤狀態碼"""
            if response.status >= 400:
                error_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'url': response.url,
                    'status': response.status,
                    'status_text': response.status_text,
                    'type': 'http_error'
                }
                self.network_errors.append(error_entry)
                
        page.on('response', handle_response)
    
    async def get_performance_metrics(self, page):
        """獲取頁面性能指標"""
        try:
            # 獲取性能指標
            metrics = await page.evaluate("""
                () => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const paintEntries = performance.getEntriesByType('paint');
                    
                    return {
                        domContentLoaded: perfData ? perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart : 0,
                        loadComplete: perfData ? perfData.loadEventEnd - perfData.loadEventStart : 0,
                        firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
                        totalLoadTime: perfData ? perfData.loadEventEnd - perfData.fetchStart : 0
                    };
                }
            """)
            self.performance_metrics = metrics
        except Exception as e:
            print(f"獲取性能指標時出錯: {e}")
    
    async def check_react_errors(self, page):
        """檢查React相關錯誤"""
        try:
            # 檢查React是否正確加載
            react_status = await page.evaluate("""
                () => {
                    return {
                        reactLoaded: typeof React !== 'undefined',
                        reactDOMLoaded: typeof ReactDOM !== 'undefined',
                        hasReactRoot: document.querySelector('#root') !== null,
                        reactVersion: typeof React !== 'undefined' ? React.version : null
                    };
                }
            """)
            return react_status
        except Exception as e:
            return {'error': str(e)}
    
    async def debug_website(self, url: str = "http://localhost:3000", headless: bool = True):
        """調試網站主函數"""
        async with async_playwright() as p:
            # 啟動瀏覽器
            browser = await p.chromium.launch(
                headless=headless,
                args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            
            try:
                # 創建新頁面
                page = await browser.new_page()
                
                # 設置監聽器
                await self.setup_page_listeners(page)
                
                print(f"正在訪問: {url}")
                
                # 訪問頁面
                try:
                    response = await page.goto(url, wait_until='networkidle', timeout=30000)
                    print(f"頁面響應狀態: {response.status}")
                except Exception as e:
                    print(f"頁面加載失敗: {e}")
                    return self.generate_report()
                
                # 等待頁面完全加載
                await page.wait_for_timeout(3000)
                
                # 獲取性能指標
                await self.get_performance_metrics(page)
                
                # 檢查React狀態
                react_status = await self.check_react_errors(page)
                
                # 檢查頁面標題和基本元素
                title = await page.title()
                print(f"頁面標題: {title}")
                
                # 檢查是否有基本的React根元素
                root_element = await page.query_selector('#root')
                if root_element:
                    print("✓ React根元素存在")
                else:
                    print("✗ React根元素不存在")
                
                # 等待更多可能的異步錯誤
                await page.wait_for_timeout(2000)
                
                # 生成報告
                report = self.generate_report()
                report['react_status'] = react_status
                report['page_title'] = title
                
                return report
                
            finally:
                await browser.close()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成調試報告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_console_logs': len(self.console_logs),
                'total_js_errors': len(self.js_errors),
                'total_network_errors': len(self.network_errors),
                'total_page_errors': len(self.page_errors)
            },
            'console_logs': self.console_logs,
            'js_errors': self.js_errors,
            'network_errors': self.network_errors,
            'page_errors': self.page_errors,
            'performance_metrics': self.performance_metrics
        }
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """打印格式化的調試報告"""
        print("\n" + "="*60)
        print("瀏覽器調試報告")
        print("="*60)
        
        # 摘要信息
        summary = report['summary']
        print(f"\n📊 摘要:")
        print(f"   控制台日誌: {summary['total_console_logs']} 條")
        print(f"   JavaScript錯誤: {summary['total_js_errors']} 個")
        print(f"   網絡錯誤: {summary['total_network_errors']} 個")
        print(f"   頁面錯誤: {summary['total_page_errors']} 個")
        
        # React狀態
        if 'react_status' in report:
            react = report['react_status']
            print(f"\n⚛️  React狀態:")
            print(f"   React已加載: {'✓' if react.get('reactLoaded') else '✗'}")
            print(f"   ReactDOM已加載: {'✓' if react.get('reactDOMLoaded') else '✗'}")
            print(f"   根元素存在: {'✓' if react.get('hasReactRoot') else '✗'}")
            if react.get('reactVersion'):
                print(f"   React版本: {react['reactVersion']}")
        
        # 性能指標
        if report['performance_metrics']:
            perf = report['performance_metrics']
            print(f"\n⚡ 性能指標:")
            print(f"   DOM內容加載: {perf.get('domContentLoaded', 0):.2f}ms")
            print(f"   頁面完全加載: {perf.get('totalLoadTime', 0):.2f}ms")
            print(f"   首次繪製: {perf.get('firstPaint', 0):.2f}ms")
            print(f"   首次內容繪製: {perf.get('firstContentfulPaint', 0):.2f}ms")
        
        # JavaScript錯誤詳情
        if report['js_errors']:
            print(f"\n❌ JavaScript錯誤詳情:")
            for i, error in enumerate(report['js_errors'][:5], 1):  # 只顯示前5個
                print(f"   {i}. [{error['type'].upper()}] {error['text']}")
                if error.get('location'):
                    print(f"      位置: {error['location']}")
                print(f"      時間: {error['timestamp']}")
                print()
        
        # 網絡錯誤詳情
        if report['network_errors']:
            print(f"\n🌐 網絡錯誤詳情:")
            for i, error in enumerate(report['network_errors'][:5], 1):  # 只顯示前5個
                print(f"   {i}. {error.get('url', 'Unknown URL')}")
                if 'status' in error:
                    print(f"      HTTP狀態: {error['status']} {error.get('status_text', '')}")
                if 'failure' in error:
                    print(f"      失敗原因: {error['failure']}")
                print(f"      時間: {error['timestamp']}")
                print()
        
        # 頁面錯誤詳情
        if report['page_errors']:
            print(f"\n🚫 頁面錯誤詳情:")
            for i, error in enumerate(report['page_errors'][:5], 1):  # 只顯示前5個
                print(f"   {i}. {error['message']}")
                print(f"      時間: {error['timestamp']}")
                print()
        
        # 如果沒有錯誤
        if (summary['total_js_errors'] == 0 and 
            summary['total_network_errors'] == 0 and 
            summary['total_page_errors'] == 0):
            print("\n✅ 恭喜！沒有發現明顯的錯誤。")
        
        print("="*60)

async def main():
    """主函數"""
    debugger = BrowserDebugger()
    
    print("開始調試localhost:3000...")
    print("這可能需要幾秒鐘時間...\n")
    
    # 執行調試
    report = await debugger.debug_website()
    
    # 打印報告
    debugger.print_report(report)
    
    # 保存詳細報告到文件
    with open('debug_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n詳細報告已保存到: debug_report.json")

if __name__ == "__main__":
    asyncio.run(main())