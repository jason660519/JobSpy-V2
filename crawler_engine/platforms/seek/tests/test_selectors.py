#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seek 選擇器調試腳本

用於檢查 Seek 網站的實際頁面結構並驗證 CSS 選擇器的有效性。
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_seek_selectors():
    """調試 Seek 選擇器"""
    
    # 測試 URL
    test_url = "https://www.seek.com.au/jobs?keywords=software%20engineer&location=Sydney"
    
    async with async_playwright() as playwright:
        # 啟動瀏覽器
        browser = await playwright.chromium.launch(
            headless=False,  # 設為 False 以便觀察
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        try:
            # 創建上下文
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            # 創建頁面
            page = await context.new_page()
            
            print(f"正在導航到: {test_url}")
            
            # 導航到頁面
            await page.goto(test_url, wait_until="networkidle")
            
            # 等待頁面加載
            await asyncio.sleep(5)
            
            print("\n=== 頁面標題 ===")
            title = await page.title()
            print(f"頁面標題: {title}")
            
            print("\n=== 分析 article 元素 ===")
            
            # 分析 article 元素
            articles = await page.query_selector_all('article')
            print(f"找到 {len(articles)} 個 article 元素")
            
            for i, article in enumerate(articles[:3]):  # 只分析前3個
                print(f"\n--- Article {i+1} ---")
                
                # 獲取所有屬性
                attrs = await article.evaluate('''
                    el => {
                        const attrs = {};
                        for (let attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    }
                ''')
                print(f"屬性: {json.dumps(attrs, indent=2)}")
                
                # 獲取文本內容
                text = await article.text_content()
                if text:
                    print(f"文本內容: {text.strip()[:200]}...")
                
                # 查找子元素
                links = await article.query_selector_all('a')
                print(f"包含 {len(links)} 個鏈接")
                
                if links:
                    for j, link in enumerate(links[:2]):  # 只顯示前2個鏈接
                        href = await link.get_attribute('href')
                        link_text = await link.text_content()
                        print(f"  鏈接 {j+1}: {link_text.strip()[:50]}... -> {href}")
            
            print("\n=== 分析 data-testid 元素 ===")
            
            # 分析包含 job 的 data-testid 元素
            job_testid_elements = await page.query_selector_all('[data-testid*="job"]')
            print(f"找到 {len(job_testid_elements)} 個包含 'job' 的 data-testid 元素")
            
            # 統計不同的 data-testid 值
            testid_counts = {}
            for element in job_testid_elements:
                testid = await element.get_attribute('data-testid')
                if testid:
                    testid_counts[testid] = testid_counts.get(testid, 0) + 1
            
            print("\ndata-testid 統計:")
            for testid, count in sorted(testid_counts.items()):
                print(f"  {testid}: {count} 個")
            
            print("\n=== 查找職位標題和公司名稱 ===")
            
            # 嘗試不同的選擇器來找職位標題
            title_selectors = [
                'h1', 'h2', 'h3', 'h4',
                '[data-testid*="title"]',
                '[data-testid*="job-title"]',
                'a[href*="/job/"]',
                'a[href*="jobs"]'
            ]
            
            for selector in title_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"\n{selector}: 找到 {len(elements)} 個元素")
                        
                        # 顯示前幾個元素的內容
                        for i, elem in enumerate(elements[:3]):
                            text = await elem.text_content()
                            href = await elem.get_attribute('href')
                            if text and text.strip():
                                print(f"  {i+1}. {text.strip()[:80]}...")
                                if href:
                                    print(f"      鏈接: {href}")
                except Exception as e:
                    print(f"錯誤處理 {selector}: {str(e)}")
            
            print("\n=== 查找公司名稱 ===")
            
            company_selectors = [
                '[data-testid*="company"]',
                '[data-testid*="advertiser"]',
                'span[title]',
                '.company',
                '[class*="company"]'
            ]
            
            for selector in company_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        print(f"\n{selector}: 找到 {len(elements)} 個元素")
                        
                        for i, elem in enumerate(elements[:3]):
                            text = await elem.text_content()
                            title_attr = await elem.get_attribute('title')
                            if text and text.strip():
                                print(f"  {i+1}. {text.strip()[:50]}...")
                                if title_attr:
                                    print(f"      title 屬性: {title_attr}")
                except Exception as e:
                    print(f"錯誤處理 {selector}: {str(e)}")
            
            # 保持瀏覽器開啟一段時間以便手動檢查
            print("\n瀏覽器將保持開啟 20 秒以便手動檢查...")
            await asyncio.sleep(20)
            
        finally:
            await browser.close()

if __name__ == "__main__":
    print("開始調試 Seek 選擇器...")
    asyncio.run(debug_seek_selectors())
    print("調試完成。")