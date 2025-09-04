#!/usr/bin/env python3
"""
Simple script to test connection to Seek website with proper headers
"""

import asyncio
import requests
from playwright.async_api import async_playwright
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from crawler_engine.platforms.seek.adapter import SeekAdapter
from crawler_engine.platforms.seek.config import create_seek_config
from crawler_engine.platforms.base import SearchRequest, SearchMethod


async def test_seek_connection():
    """Test connection to Seek website"""
    print("🚀 Testing Seek website connection...")
    
    try:
        # Test 1: Simple HTTP request with headers
        print("\n📝 Test 1: HTTP request with headers")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get('https://www.seek.com.au', headers=headers, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Success: {response.status_code == 200}")
        
        # Test 2: Playwright browser test
        print("\n🎭 Test 2: Playwright browser test")
        async with async_playwright() as playwright:
            # Launch browser
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Set headers
            await context.set_extra_http_headers(headers)
            
            # Create page
            page = await context.new_page()
            
            # Navigate to Seek
            print("   Navigating to Seek...")
            response = await page.goto('https://www.seek.com.au', wait_until='networkidle')
            print(f"   Status: {response.status}")
            
            # Check if we can find job listings
            try:
                await page.wait_for_selector('[data-automation*="job"]', timeout=10000)
                print("   ✓ Job listings found!")
            except:
                print("   ⚠ Could not find job listings immediately")
            
            # Take screenshot for debugging
            await page.screenshot(path='test_seek_page.png', full_page=True)
            print("   Screenshot saved as test_seek_page.png")
            
            # Close browser
            await page.close()
            await context.close()
            await browser.close()
            
        print("\n✅ Connection tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        return False


async def test_seek_search():
    """Test actual job search on Seek"""
    print("\n🔍 Testing Seek job search...")
    
    try:
        # Initialize Seek adapter
        config = create_seek_config()
        adapter = SeekAdapter(config)
        
        # Create search request
        search_request = SearchRequest(
            query="software engineer",
            location="Sydney",
            page=1,
            limit=5
        )
        
        print(f"   Searching for '{search_request.query}' in '{search_request.location}'...")
        
        # Perform search
        result = await adapter.search_jobs(search_request, SearchMethod.WEB_SCRAPING)
        
        print(f"   Success: {result.success}")
        print(f"   Jobs found: {len(result.jobs)}")
        
        if result.jobs:
            print("   Sample job:")
            job = result.jobs[0]
            print(f"     Title: {job.get('title', 'N/A')}")
            print(f"     Company: {job.get('company', 'N/A')}")
            print(f"     Location: {job.get('location', 'N/A')}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False


async def main():
    """Main function"""
    print("=" * 50)
    print("Seek Connection Test")
    print("=" * 50)
    
    # Test connection
    connection_success = await test_seek_connection()
    
    # Test search (only if connection works)
    search_success = False
    if connection_success:
        search_success = await test_seek_search()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Connection Test: {'✅ PASS' if connection_success else '❌ FAIL'}")
    print(f"Search Test: {'✅ PASS' if search_success else '❌ FAIL'}")
    
    overall_success = connection_success and search_success
    print(f"Overall: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)