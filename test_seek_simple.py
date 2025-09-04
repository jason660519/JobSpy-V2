#!/usr/bin/env python3
"""
Simple script to test connection to Seek website with Playwright
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_seek_connection():
    """Test connection to Seek website using Playwright"""
    print("🚀 Testing Seek website connection with Playwright...")
    
    try:
        # Import Playwright
        from playwright.async_api import async_playwright
        
        # Test with Playwright browser
        print("\n🎭 Playwright browser test")
        async with async_playwright() as playwright:
            # Launch browser
            browser = await playwright.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Set realistic headers
            await context.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            
            # Create page
            page = await context.new_page()
            
            # Navigate to Seek
            print("   Navigating to Seek...")
            response = await page.goto('https://www.seek.com.au', wait_until='networkidle')
            print(f"   Status: {response.status}")
            
            # Check if we can find job listings
            try:
                # Wait for job listings to load
                await page.wait_for_selector('[data-automation*="job"], .job-tile', timeout=15000)
                print("   ✓ Job listings found!")
                
                # Try a search
                print("   Searching for 'software engineer'...")
                search_url = "https://www.seek.com.au/jobs?keywords=software+engineer&location=Sydney"
                response = await page.goto(search_url, wait_until='networkidle')
                print(f"   Search page status: {response.status}")
                
                # Wait for results
                await page.wait_for_selector('[data-automation*="job"], .job-tile', timeout=15000)
                
                # Count job cards
                job_cards = await page.query_selector_all('[data-automation*="job"], .job-tile')
                print(f"   Found {len(job_cards)} job cards")
                
                # Extract some job information
                if job_cards:
                    first_card = job_cards[0]
                    title_element = await first_card.query_selector('[data-automation*="jobTitle"], h3')
                    if title_element:
                        title = await title_element.text_content()
                        print(f"   Sample job title: {title.strip()}")
                        
            except Exception as e:
                print(f"   ⚠ Warning: {e}")
            
            # Take screenshot for debugging
            await page.screenshot(path='seek_test_page.png', full_page=True)
            print("   Screenshot saved as seek_test_page.png")
            
            # Close browser
            await page.close()
            await context.close()
            await browser.close()
            
        print("\n✅ Connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        return False


async def main():
    """Main function"""
    print("=" * 50)
    print("Seek Connection Test")
    print("=" * 50)
    
    # Test connection
    success = await test_seek_connection()
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Connection Test: {'✅ PASS' if success else '❌ FAIL'}")
    
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)