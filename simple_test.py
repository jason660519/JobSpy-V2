import asyncio
from playwright.async_api import async_playwright

async def test_seek():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        response = await page.goto('https://www.seek.com.au', wait_until='networkidle')
        print(f'Status: {response.status}')
        await page.close()
        await context.close()
        await browser.close()
        print('Success!')

asyncio.run(test_seek())