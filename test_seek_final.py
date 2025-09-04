import asyncio
from playwright.async_api import async_playwright
import sys

async def test_seek_connection():
    """Test connection to Seek with more realistic settings"""
    print("Testing Seek connection...")
    
    try:
        async with async_playwright() as p:
            # Launch browser with more realistic settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions'
                ]
            )
            
            # Create context with realistic settings
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                // Hide webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Hide plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Hide languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            # Create page
            page = await context.new_page()
            
            # Navigate to Seek with shorter timeout and different wait condition
            print("Navigating to Seek...")
            response = await page.goto(
                'https://www.seek.com.au', 
                wait_until='domcontentloaded',  # Changed from networkidle
                timeout=15000
            )
            
            print(f"Status: {response.status}")
            
            # Wait for basic elements to load
            try:
                await page.wait_for_selector('body', timeout=5000)
                print("Page loaded successfully!")
                
                # Try to find job-related elements
                job_elements = await page.query_selector_all('[data-automation*="job"], .job')
                print(f"Found {len(job_elements)} job-related elements")
                
            except Exception as e:
                print(f"Warning: {e}")
            
            # Take screenshot
            await page.screenshot(path='seek_connection_test.png', full_page=True)
            print("Screenshot saved as seek_connection_test.png")
            
            # Close resources
            await page.close()
            await context.close()
            await browser.close()
            
            print("Success!")
            return True
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_seek_connection())
    sys.exit(0 if success else 1)